from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import settings
from django.core.mail import send_mail
from apps.events.forms import EventForm
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from apps.users.mixins import ParticipantRequiredMixin
from apps.events.models import Event, EventRegistration
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

CustomUser = get_user_model()


class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'organizer' and self.request.user.is_organizer


class EventCreateView(CreateView, LoginRequiredMixin, OrganizerRequiredMixin):
    model = Event
    form_class = EventForm
    template_name = 'events/create_event.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)


class EventDetailView(DetailView):
    model = Event
    template_name = "events/detail_event.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        total_registrations = event.registrations.count()
        context["total_registrations"] = total_registrations
        context["available_spots"] = event.max_participants - total_registrations

        user = self.request.user
        if user.is_authenticated:
            try:
                registration = event.registrations.get(attendee=user)
                context["user_registration_status"] = "confirmed" if registration.confirmed else "pending"

                uid = urlsafe_base64_encode(force_bytes(registration.pk))
                token = default_token_generator.make_token(user)
                cancel_link = reverse("events:cancel-event-registration", kwargs={'uidb64': uid, 'token': token})
                context["cancel_link"] = cancel_link
            except EventRegistration.DoesNotExist:
                context["user_registration_status"] = "not_registered"

        return context


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    template_name = "events/update_event.html"
    fields = ['title', 'description', 'start_time', 'end_time', 'location',
                  'max_participants', 'image',]
    login_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_status()
        self.object.save()

        registrations = self.object.registrations.filter(confirmed=True)
        participant_emails = [reg.attendee.email for reg in registrations if reg.attendee.email]

        if participant_emails:
            send_mail(
                subject="Tadbir ma'lumotlari yangilandi",
                message=f"Hurmatli foydalanuvchi,\n\n\"{self.object.title}\" nomli tadbir ma’lumotlari yangilandi."
                        f"\nIltimos, sahifani ko‘rib chiqing: {self.request.build_absolute_uri(self.object.get_absolute_url())}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=participant_emails,
                fail_silently=False,
            )

        return response

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def get_success_url(self):
        event_slug = self.object.slug
        return reverse("events:detail-event", kwargs={"slug": event_slug})


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = "events/delete_event.html"
    login_url = reverse_lazy("users:login")

    def get_success_url(self):
        return reverse_lazy("home")

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.registrations.exists():
            messages.error(request, "Bu tadbirni o‘chira olmaysiz, chunki ishtirokchilar ro‘yxatdan o‘tgan.")
            return HttpResponseForbidden("Bu tadbirda ishtirokchilar borligi sababli o‘chira olmaysiz.")
        return super().dispatch(request, *args, **kwargs)


class RegisterForEventView(ParticipantRequiredMixin, View):
    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if EventRegistration.objects.filter(attendee=request.user, event=event).exists():
            messages.error(request, "Siz allaqachon ushbu tadbirga ro‘yxatdan o‘tgansiz.")
            return redirect("events:detail-event", slug=event.slug)

        registration = EventRegistration.objects.create(
            attendee=request.user,
            event=event,
            confirmed=False
        )

        event.update_status()

        uid = urlsafe_base64_encode(force_bytes(registration.pk))
        token = default_token_generator.make_token(request.user)
        confirm_link = request.build_absolute_uri(
            reverse("events:confirm-event-registration", args=[uid, token])
        )

        html_message = render_to_string('email/registration_confirm.html', {
            'user': request.user,
            'confirm_link': confirm_link
        })

        send_mail(
            "Tadbirda ishtirokni tasdiqlang",
            '',
            "zarnigor1008@gmail.com",
            [request.user.email],
            html_message=html_message
        )

        messages.success(request, "Ro‘yxatdan o‘tdingiz. Email orqali tasdiqlang.")
        return redirect("events:detail-event", slug=event.slug)


class ConfirmEventRegistrationView(View):
    def get(self, request, uidb64, token):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
            registration = EventRegistration.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, EventRegistration.DoesNotExist):
            registration = None

        if registration and default_token_generator.check_token(registration.attendee, token):
            registration.confirmed = True
            registration.save()
            messages.success(request, "Ishtirokingiz tasdiqlandi.")
            return redirect("home")
        else:
            messages.error(request, "Tasdiqlash havolasi noto‘g‘ri yoki eskirgan.")
            return redirect("home")


class CancelEventRegistrationView(View):
    def get(self, request, uidb64, token):
        try:
            pk = force_str(urlsafe_base64_decode(uidb64))
            registration = EventRegistration.objects.get(pk=pk)
        except (TypeError, ValueError, OverflowError, EventRegistration.DoesNotExist):
            registration = None

        if registration and default_token_generator.check_token(registration.attendee, token):
            user = registration.attendee
            event = registration.event
            registration.delete()
            event.update_status()

            html_message = render_to_string('email/registration_cancelled.html', {
                'user': user,
                'event': event
            })

            send_mail(
                "Tadbir ro'yxatidan chiqarildingiz",
                '',
                "zarnigor1008@gmail.com",
                [user.email],
                html_message=html_message
            )

            messages.success(request, "Ishtirokingiz bekor qilindi.")
            return redirect("home")




