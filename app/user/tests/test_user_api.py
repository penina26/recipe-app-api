"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


def create_user_url():
    """Return user create URL."""
    return reverse('user:create')


def create_token_url():
    """Return URL for generating an authentication token."""
    return reverse('user:token')


# Added the me_url helper
def me_url():
    """Return user profile URL."""
    return reverse('user:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApi(TestCase):
    """Test public features of a user API."""
    
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        res = self.client.post(create_user_url(), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**payload)
        
        res = self.client.post(create_user_url(), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name'
        }
        res = self.client.post(create_user_url(), payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generating a token for valid credentials."""
        create_user(email='test@example.com', password='testpass123', name='Test Name')
        
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(create_token_url(), payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='testpass123')
        
        payload = {
            'email': 'test@example.com',
            'password': 'badpassword'
        }
        res = self.client.post(create_token_url(), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(create_token_url(), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_token_no_user(self):
        """Test retrieving token for non-existent user returns an error."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(create_token_url(), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Added security check to ensure unauthenticated users are blocked
    def test_retrieve_user_unauthorized(self):
        """Test unauthorized request to user profile endpoint fails."""
        res = self.client.get(me_url())

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class specifically for testing authenticated endpoints
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )
        self.client = APIClient()
        # This simulates passing the token in the request header
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving the authenticated user's profile."""
        res = self.client.get(me_url())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_update_user_profile(self):
        """Test updating the authenticated user's profile."""
        payload = {'name': 'New Name', 'password': 'newpassword123'}
        res = self.client.patch(me_url(), payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)