# Generated by Django 5.2.1 on 2025-05-16 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='organizing_company',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
