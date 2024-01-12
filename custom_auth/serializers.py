from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from custom_auth.models import User
from .validators import user_exists_validation

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[user_exists_validation])
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = User
        fields = [
            "pk",
            "first_name",
            'last_name',
            'email',
            'password'
        ]

    def save(self):
        password = self.validated_data['password']
        self.validated_data['password'] = make_password(password)
        super(UserSerializer, self).save()
