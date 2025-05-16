from django.urls import path
from apps.events.views import (EventCreateView, EventDetailView,
                               EventUpdateView, EventDeleteView, RegisterForEventView,
                               ConfirmEventRegistrationView, CancelEventRegistrationView)

app_name = "events"

urlpatterns = [
    path("create-event/", EventCreateView.as_view(), name='create-event'),
    path("detail-event/<slug:slug>/", EventDetailView.as_view(), name='detail-event'),
    path("update-event/<str:slug>/", EventUpdateView.as_view(), name='update-event'),
    path("delete-event/<int:pk>/", EventDeleteView.as_view(), name='delete-event'),
    path("register-for-event/<int:event_id>/", RegisterForEventView.as_view(), name='register-for-event'),
    path("confirm-event-registration/<uidb64>/<token>/", ConfirmEventRegistrationView.as_view(),
         name='confirm-event-registration'),
    path("cancel-event-registration/<uidb64>/<token>/", CancelEventRegistrationView.as_view(),
         name='cancel-event-registration')
]