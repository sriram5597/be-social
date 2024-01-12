# Generated by Django 5.0.1 on 2024-01-11 16:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connections', '0002_connectionrequestmodel_delete_friendsrequestmodel'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='connectionrequestmodel',
            constraint=models.UniqueConstraint(fields=('sender', 'request_to'), name='unique_connection'),
        ),
    ]