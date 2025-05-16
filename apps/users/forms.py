from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')


class ParticipantSignUpForm(CustomUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'participant'
        user.is_active = False  # False until email is activated
        if commit:
            user.save()
        return user


class OrganizerSignUpForm(CustomUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'organizer'
        user.is_active = False
        user.is_organizer_pending = True
        if commit:
            user.save()
        return user

