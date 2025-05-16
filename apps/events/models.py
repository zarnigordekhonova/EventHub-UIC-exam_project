from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class Event(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('full', 'Full'),
    ]

    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    organizing_company = models.CharField(max_length=128, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    start_time = models.CharField(max_length=64)
    end_time = models.CharField(max_length=64)
    location = models.CharField(max_length=255)
    max_participants = models.PositiveIntegerField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def update_status(self):
        if self.registrations.count() >= self.max_participants:
            self.status = 'full'
        else:
            self.status = 'open'
        self.save()

    def get_absolute_url(self):
        return reverse("events:detail-event", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(
            *args,
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class EventRegistration(models.Model):
    attendee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Event registration"
        verbose_name_plural = "Events registration"

    def __str__(self):
        return f"{self.attendee.email} | {self.event.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.event.update_status()
        self.event.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.event.update_status()
        self.event.save()