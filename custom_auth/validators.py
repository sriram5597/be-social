from rest_framework import serializers
from custom_auth.models import User

def user_exists_validation(value):
    user = User.objects.filter(email=value).exists()
    if user:
        raise serializers.ValidationError(f"email already in user")
    return value
