from django.urls import path
from django.contrib.auth.views import LoginView
from apps.users.views import (RegisterAsParticipantView, RegisterAsOrganizerView,
                              ActivationView, custom_logout_view, OrganizerConfirmView)

app_name = 'users'

urlpatterns = [
    path('register-participant/', RegisterAsParticipantView.as_view(), name='register-participant'),
    path('register-organizer/', RegisterAsOrganizerView.as_view(), name='register-organizer'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('confirm-organizer/<uidb64>/<token>/', OrganizerConfirmView.as_view(), name='organizer-confirm'),
]