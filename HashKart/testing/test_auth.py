import unittest
import json
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import User

class AuthRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_missing_parameters(self):
        response = self.client.post('/auth/signup')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Missing username, email, or password')

    def test_signup_username_exists(self):
        user_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'}
        User(username='testuser', email='test@example.com', password_hash='hashed_password').save()
        response = self.client.post('/auth/signup', json=user_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Username already exists')

    def test_signup_email_exists(self):
        user_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'}
        User(username='existing_user', email='test@example.com', password_hash='hashed_password').save()
        response = self.client.post('/auth/signup', json=user_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Email already exists')

    def test_signup_success(self):
        user_data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post('/auth/signup', json=user_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User created successfully')

    @patch('app.routes.create_access_token')
    def test_login_success(self, mock_create_access_token):
        user = User(username='testuser', email='test@example.com', password_hash='hashed_password')
        user.save()
        user_id = 1
        mock_create_access_token.return_value = 'mocked_token'
        response = self.client.post('/auth/login', json={'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        self.assertEqual(data['access_token'], 'mocked_token')

    def test_login_invalid_credentials(self):
        response = self.client.post('/auth/login', json={'username': 'invalid_user', 'password': 'invalid_password'})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Invalid username or password')

    def test_profile_unauthorized(self):
        response = self.client.get('/auth/profile')
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Missing Authorization Header')

    def test_profile_success(self):
        user = User(username='testuser', email='test@example.com', password_hash='hashed_password')
        user.save()
        access_token = user.generate_auth_token().decode()
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get('/auth/profile', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')

if __name__ == '__main__':
    unittest.main()
