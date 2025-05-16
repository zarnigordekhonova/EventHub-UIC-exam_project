from django.contrib import admin
from apps.events.models import Event, EventRegistration

admin.site.register(Event)
admin.site.register(EventRegistration)