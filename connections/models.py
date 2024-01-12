from django.db import models

from custom_auth.models import User
from .constants import REQUEST_STATUS, REQUEST_PENDING

class ConnectionRequestModel(models.Model):
    sender = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE, related_name='sender')
    request_to = models.ForeignKey(to=User, null=False, on_delete=models.CASCADE, related_name='connected_to')
    status = models.CharField(max_length=1, choices=REQUEST_STATUS, default=REQUEST_PENDING)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sender', 'request_to'], name='unique_connection'),
        ]
