from django.shortcuts import render, reverse
from django.views.generic import TemplateView
from apps.events.models import Event

class GetToHomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_authenticated and user.role == "organizer" and user.is_organizer:
            context['events'] = Event.objects.filter(organizer=user)
        else:
            context['events'] = Event.objects.all()

        return context

