from django import forms
from apps.events.models import Event, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'organizing_company', 'start_time', 'end_time', 'location',
                  'max_participants', 'image', 'status']