from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from custom_auth.models import User


class SignupTestCase(TestCase):
    client = APIRequestFactory()
    
    def test_signup_user_with_valid_data(self):
        url = reverse('signup-user')
        data = {
            'email': 'user@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password@5'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.filter(email=data['email']).first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password, data['password'])
        
    def test_signup_user_with_empty_fields(self):
        url = reverse('signup-user')
        data = {
            'email': '  ',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password@5'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_signup_user_with_existing_email(self):
        user = User(email="existing@example.com", password="password")
        user.save()
        url = reverse('signup-user')
        data = {
            'email': 'existing@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Password@5'
        }
        expected_data = {
            'error': 'email is required'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginTestCase(TestCase):
    
    def setUp(self):
        data = {
            "email": "user@example.com",
            "password": "Password@5"
        }
        user = User(**data)
        user.set_password(data['password'])
        user.save()
    
    def test_user_login_with_valid_credentials(self):
        data = {
            "email": "user@example.com",
            "password": "Password@5"
        }
        url = reverse('login-user')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('access'))
        self.assertIsNotNone(response.data.get('refresh'))
    
    def test_user_login_with_invalid_credentials(self):
        data = {
            "email": "user@example.com",
            "password": "Password5"
        }
        url = reverse('login-user')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
