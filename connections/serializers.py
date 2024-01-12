from django.db.models import Q
from rest_framework import serializers
from .models import ConnectionRequestModel

class ConnectionRequestSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ConnectionRequestModel
        fields = [
            'pk',
            'sender',
            'request_to',
            'status',
            'updated_at'
        ]

    def validate(self, data, *args, **kwargs):
        if self.instance is None:
            if data['sender'].id == data['request_to'].id:
                raise serializers.ValidationError("cannot send request to yourself")
            is_connection_exists = ConnectionRequestModel.objects.filter(
                Q(Q(sender=data['sender']) & Q(request_to=data['request_to'])) | Q(Q(sender=data['request_to']) & Q(request_to=data['sender']))
            ).exists()
            if is_connection_exists:
                raise serializers.ValidationError("connection already exists")
        return data
