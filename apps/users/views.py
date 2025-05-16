from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from apps.users.forms import CustomUserCreationForm, ParticipantSignUpForm, OrganizerSignUpForm

CustomUser = get_user_model()


class RegisterAsParticipantView(CreateView):
    template_name = "users/register_participant.html"
    model = CustomUser
    form_class = ParticipantSignUpForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()

        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://{current_site.domain}/users/activate/{uid}/{token}/"
        message = render_to_string('email/activation_email.html', context={
            'user': user,
            'activation_link': activation_link
        })
        print("Activation link:", activation_link)

        send_mail(
            subject="Akkountingizni faollashtiring",
            message=message,
            from_email="zarnigor1008@gmail.com",
            recipient_list=[user.email],
        )

        return redirect("users:login")


# With the function below, when user registers as an organizer, the superuser
# will receive an email to approve them as an organizer
def notify_superuser_new_organizer(user):
    superusers = CustomUser.objects.filter(is_superuser=True, email__isnull=False).exclude(email='')

    recipient_list = [admin.email for admin in superusers]
    if recipient_list:
        send_mail(
            subject="New Organizer Registration",
            message=f"The user {user.email} has registered as an organizer. Please review their request in the admin panel.",
            from_email="noreply@eventhub.com",
            recipient_list=recipient_list,
            fail_silently=False
        )


class RegisterAsOrganizerView(CreateView):
    model = CustomUser
    form_class = OrganizerSignUpForm
    template_name = 'users/register_organizer.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()

        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://{current_site.domain}/users/activate/{uid}/{token}/"
        message = render_to_string('email/activation_email.html', context={
            'user': user,
            'activation_link': activation_link
        })
        print("Activation link:", activation_link)

        send_mail(
            subject="Akkountingizni faollashtiring",
            message=message,
            from_email="zarnigor1008@gmail.com",
            recipient_list=[user.email],
        )

        notify_superuser_new_organizer(user)

        return redirect("users:login")


class ActivationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Sizning akkountingiz muvaffaqiyatli aktivlashtirildi.")
            return redirect("users:login")
        else:
            messages.error(request, "Aktivatsiya havolasi xato yoki eskirgan.")
            return redirect("users:login")


def custom_logout_view(request):
    logout(request)
    return redirect("home")


class OrganizerConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_organizer_confirmed = True
            user.save()
            messages.success(request, "Sizning akkountingiz tashkilotchi sifatida aktivlashtirildi.")
            return redirect("home")
        else:
            messages.error(request, "Aktivatsiya havolasi xato yoki eskirgan.")
            return redirect("home")






