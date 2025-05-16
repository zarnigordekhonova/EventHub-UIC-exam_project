from django.contrib import admin
from django.core.mail import send_mail
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'first_name', 'last_name', 'role',
        'is_active', 'is_staff', 'is_superuser',
        'is_organizer', 'is_organizer_pending',
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'is_organizer_pending')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    actions = ['approve_organizers']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        ('Role Info', {
            'fields': ('role', 'is_organizer', 'is_organizer_pending')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'password1', 'password2',
                'role', 'is_active', 'is_staff', 'is_superuser',
                'is_organizer', 'is_organizer_pending',
            ),
        }),
    )

    def approve_organizers(self, request, queryset):
        pending = queryset.filter(role='organizer', is_organizer_pending=True)
        count = 0
        for user in pending:
            user.is_organizer_pending = False
            user.is_organizer = True
            user.save()
            count += 1

            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirm_link = f"http://{current_site.domain}/users/confirm-organizer/{uid}/{token}/"

            message = render_to_string('email/organizer_confirm_email.html', {
                'user': user,
                'confirm_link': confirm_link
            })

            send_mail(
                subject="Siz tashkilotchi sifatida aktivlashtirildingiz!",
                message=message,
                from_email="zarnigor1008@gmail.com",
                recipient_list=[user.email],
            )

        self.message_user(request, f"{count} organizer(s) approved and emailed.")


