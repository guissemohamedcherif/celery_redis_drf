# from PIL import Image as PILImage
from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from icecream import ic
from PIL import Image as PILImage
from api.models import *
from api.serializers import *
from api.views import *
# Import the mocker library
from unittest.mock import MagicMock
API_URL = '/api'


class GetTokenApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user('boilerplate@yopmail.com', 'Lechrist@12')
        # self.client.force_authenticate(self.user)

    def test_get_token(self):
        data = {'email': 'boilerplate@yopmail.com', 'password': 'Lechrist@12'}
        res = self.client.post(API_URL+'/auth/get-token', data)
        self.assertEqual(res.status_code, 200)

    def test_verify_token(self):
        data = {'email': 'boilerplate@yopmail.com', 'password': 'Lechrist@12'}
        res1 = self.client.post(API_URL+'/auth/get-token', data)
        res = self.client.post(
            API_URL+'/auth/verify-token',
            {'token': res1.json()['token']})
        self.assertEqual(res.status_code, 200)

    def test_refresh_token(self):
        data = {'email': 'boilerplate@yopmail.com',
                'password': 'Lechrist@12'}
        res1 = self.client.post(API_URL+'/auth/get-token', data)
        res = self.client.post(API_URL+'/auth/refresh-token',
                               {'token': res1.json()['token']})
        self.assertEqual(res.status_code, 200)

    def test_login(self):
        data = {'email': 'boilerplate@yopmail.com', 'password': 'Lechrist@12'}
        res = self.client.post(API_URL+'/auth/login/', data)
        self.assertEqual(res.status_code, 200)


class RequestPasswordResetApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
         'minsomahou@gmail.com', 'Lechrist@12')
        self.client.force_authenticate(self.user)
        self.data = {'email': self.user.email}

    def test_request_password_reset(self):
        res = self.client.post(API_URL+'/auth/request-password-reset/',
                               self.data)
        self.assertEqual(res.status_code, 200)

class ChangePasswordCRUDApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
         'boilerplate@yopmail.com', 'Lechrist@12')
        self.client.force_authenticate(self.user)

    def test_change_password(self):
        data = {'old_password': 'Lechrist@12', 'new_password': 'elchristo'}
        res = self.client.put(API_URL+'/auth/change-password/', data)
        self.assertEqual(res.status_code, 200)
        

        
    

        