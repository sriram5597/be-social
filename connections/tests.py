from django.test import TestCase, override_settings
from django.core.cache import cache
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.urls import reverse

from custom_auth.models import User
from custom_auth.serializers import UserSerializer
from .models import ConnectionRequestModel
from .constants import REQUEST_PENDING, REQUEST_ACCEPTED, REQUEST_REJECTED

def login_user(client):
    url = reverse('login-user')
    response = client.post(url, {'email': 'existing@example.com', 'password': 'Password@5'}, format='json')
    return response.data.get("access")

def load_existing_user():
    data = {
        'email': 'existing@example.com',
        'first_name': 'Test',
        'last_name': f'Existing User',
        'password': 'Password@5'
    }
    login_user = UserSerializer(data=data)
    login_user.is_valid(raise_exception=True)
    login_user.save()

class SearchUsersTest(TestCase):
    client = APIRequestFactory()
    url = reverse('search-user')
    headers = None
        
    @classmethod
    def load_bulk_users(cls):
        users = []
        for i in range(1, 20):
            data = {
                'email': f'user{i}@example.com',
                'first_name': 'Test',
                'last_name': f'User {i}',
                'password': 'Password@5'
            }
            users.append(data)
        serializer = UserSerializer(data=users, many=True)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            serializer.save()
    
    @classmethod
    def setUpTestData(cls):
        load_existing_user()
        cls.load_bulk_users()
    
    def setUp(self):
        token = ""
        if self.headers is None:
            token = login_user(self.client)
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
            
    def test_search_users_by_name(self):
        response = self.client.get(f'{self.url}?key=test', headers=self.headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEquals(response.data.get('count'), 19)
        self.assertEquals(len(response.data.get('results')), 10)

    def test_fetch_all_users(self):
        response = self.client.get(f'{self.url}', headers=self.headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEquals(response.data.get('count'), 19)
        self.assertEquals(len(response.data.get('results')), 10)
    
    def test_search_users_by_email(self):
        response = self.client.get(f'{self.url}?key=user1@example.com', headers=self.headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEquals(len(response.data.get('results')), 1)

    def test_search_without_token(self):
        response = self.client.get(f'{self.url}?key=Test')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

class SendConnectionRequestTest(TestCase):
    client = APIRequestFactory()
    headers = None
    
    @classmethod
    def load_user(cls):
        users = []
        for i in range(1, 20):
            data = {
                'email': f'friend{i}@example.com',
                'first_name': 'Friend',
                'last_name': f'User {i}',
                'password': 'Password@5'
            }
            users.append(data)
        serializer = UserSerializer(data=users, many=True)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            serializer.save()

    @classmethod
    def setUpTestData(cls):
        load_existing_user()
        cls.load_user()
        
    def setUp(self):
        token = ""
        if self.headers is None:
            token = login_user(self.client)
        self.headers = {
           'Authorization': f'Bearer {token}'
        }
        # print('cache: ', cache.keys())
        cache.clear()
       
    def send_request(self, email):
        url = reverse('create-connection-request')
        user = User.objects.get(email=email)
        data = {
            'request_to': user.id
        }
        response = self.client.post(url, data, format='json', headers=self.headers)
        return response
    
    def test_send_connection_request(self):
        response = self.send_request('friend1@example.com')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('status'), REQUEST_PENDING)
        self.assertGreater(response.data.get('pk'), 0)

    def test_send_connection_request_multiple_times_to_same_user(self):
        friend_email = 'friend1@example.com'
        friend_user = User.objects.get(email=friend_email)
        existing_user = User.objects.get(email='existing@example.com')
        data = {
            'sender': existing_user,
            'request_to': friend_user
        }
        instance = ConnectionRequestModel(**data)
        instance.save()
        response = self.send_request(friend_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_send_connection_request_by_user_who_already_has_request_from_that_user(self):
        friend_email = 'friend1@example.com'
        friend_user = User.objects.get(email=friend_email)
        existing_user = User.objects.get(email='existing@example.com')
        data = {
            'sender': friend_user,
            'request_to': existing_user
        }
        instance = ConnectionRequestModel(**data)
        instance.save()
        response = self.send_request(friend_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_send_connection_request_by_user_to_himself(self):
        response = self.send_request('existing@example.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_connection_request_to_invalid_user(self):
        url = reverse('create-connection-request')
        data = {
            'request_to': 0
        }
        response = self.client.post(url, data, format='json', headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_multiple_connection_requests_in_less_than_a_minute(self):
        for i in range(1, 4):
            response = self.send_request(f'friend{i}@example.com')
        response = self.send_request('friend4@example.com')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
    
class ConnectionRequestCRUDTest(TestCase):
    headers = None
    
    @classmethod
    def load_user(cls):
        data = {
            'email': 'friend@example.com',
            'first_name': 'Friend',
            'last_name': 'User',
            'password': 'Password@5'
        }
        user = UserSerializer(data=data)
        user.is_valid(raise_exception=True)
        user.save()
    
    @classmethod
    def setUpTestData(cls):
        load_existing_user()
        cls.load_user()
        
    def load_connection_request(self, payload):
        friend_user = User.objects.get(email=payload.get('request_to'))
        existing_user = User.objects.get(email=payload.get('sender'))
        data = {
            'sender': existing_user,
            'request_to': friend_user
        }
        if payload.get('status') is not None:
            data['status'] = payload['status']
        connection_request = ConnectionRequestModel(**data)
        connection_request.save()
        return connection_request
        
    def setUp(self):
        token = ""
        if self.headers is None:
            token = login_user(self.client)
        self.headers = {
           'Authorization': f'Bearer {token}'
        }
    
    def test_accept_connection_request(self):
        connection_request = self.load_connection_request({
            'sender': 'friend@example.com',
            'request_to': 'existing@example.com' 
        })
        
        payload = {
            "status": REQUEST_ACCEPTED
        }
        url = reverse('connection-request', kwargs={'connection_id': connection_request.id})
        response = self.client.patch(url, payload, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), REQUEST_ACCEPTED)


    def test_accept_connection_request_for_different_user(self):
        connection_request = self.load_connection_request({
            'request_to': 'friend@example.com',
            'sender': 'existing@example.com' 
        })
        
        payload = {
            "status": REQUEST_ACCEPTED
        }
        url = reverse('connection-request', kwargs={'connection_id': connection_request.id})
        response = self.client.patch(url, payload, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_reject_conection_request(self):
        connection_request = self.load_connection_request({
            'sender': 'friend@example.com',
            'request_to': 'existing@example.com' 
        })
        payload = {
            "status": REQUEST_REJECTED
        }
        url = reverse('connection-request', kwargs={'connection_id': connection_request.id})
        response = self.client.patch(url, payload, content_type='application/json', headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        is_request_exists = ConnectionRequestModel.objects.filter(id=connection_request.id).exists()
        self.assertFalse(is_request_exists)

    def test_list_accpected_connections(self):
        self.load_connection_request({
            'sender': 'friend@example.com',
            'request_to': 'existing@example.com',
            'status': REQUEST_ACCEPTED
        })
        
        url = reverse('list-connection-request')
        response = self.client.get(url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get('count'), 1)

    def test_list_accpected_connections_that_are_sent_by_existing_user(self):
        self.load_connection_request({
            'request_to': 'friend@example.com',
            'sender': 'existing@example.com',
            'status': REQUEST_ACCEPTED
        })
        
        url = reverse('list-connection-request')
        response = self.client.get(url, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get('count'), 1)

    def test_list_pending_requests(self):
        self.load_connection_request({
            'sender': 'friend@example.com',
            'request_to': 'existing@example.com',
            'status': REQUEST_PENDING
        })
        url = reverse('list-connection-request')
        response = self.client.get(f'{url}?status={REQUEST_PENDING}', headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)