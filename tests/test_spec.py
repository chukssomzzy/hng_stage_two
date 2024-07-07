import unittest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, decode_token
from api.v1.app import app, jwt
from models import engine
from models.users import User
from models.organisations import Organisation


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Clear the database before each test
        engine.reload()

    def tearDown(self):
        engine.close()
        self.app_context.pop()

    def test_token_generation_and_expiration(self):
        user = User(
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        user.set_password("password123")
        engine.new(user)
        engine.save()

        with app.test_request_context():
            token = create_access_token(identity=user)
            decoded_token = decode_token(token)

        self.assertEqual(decoded_token['sub'], user.id)
        self.assertAlmostEqual(decoded_token['exp'],
                               (datetime.utcnow() + timedelta(hours=1))
                               .timestamp(),
                               delta=5)  # Allow 5 seconds difference

    def test_organisation_data_access(self):
        # Create two users and two organisations
        user1 = User(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com")
        user1.set_password("password123")
        user2 = User(
            first_name="Bob",
            last_name="Jones",
            email="bob@example.com")
        user2.set_password("password456")

        org1 = Organisation(name="Alice's Org")
        org2 = Organisation(name="Bob's Org")

        user1.organisations.append(org1)
        user2.organisations.append(org2)

        engine.new(user1)
        engine.new(user2)
        engine.new(org1)
        engine.new(org2)
        engine.save()

        # Test that user1 can access org1 but not org2
        with self.app.application.test_request_context():
            # with jwt.require_jwt():
            token = create_access_token(identity=user1)

        response = self.app.get(f'/api/organisations/{org1.id}',
                                headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

        response = self.app.get(f'/api/organisations/{org2.id}',
                                headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 400)

    def test_register_user_success(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword123"
        }
        response = self.app.post('/auth/register', json=data)
        self.assertEqual(response.status_code, 201)

        response_data = response.get_json()
        self.assertIn('accessToken', response_data['data'])
        self.assertEqual(response_data['data']['firstName'], "John")
        self.assertEqual(response_data['data']['lastName'], "Doe")
        self.assertEqual(response_data['data']['email'],
                         "john.doe@example.com")

        # Check if default organisation was created
        user = engine.filter("User", email="john.doe@example.com")[0]
        self.assertEqual(len(user.organisations), 1)
        self.assertEqual(user.organisations[0].name, "John's organisation")

    def test_login_user_success(self):
        # First, register a user
        register_data = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane.doe@example.com",
            "password": "securepassword123"
        }
        self.app.post('/auth/register', json=register_data)

        # Now, try to log in
        login_data = {
            "email": "jane.doe@example.com",
            "password": "securepassword123"
        }
        response = self.app.post('/auth/login', json=login_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        self.assertIn('accessToken', response_data['data'])
        self.assertEqual(response_data['data']['firstName'], "Jane")
        self.assertEqual(response_data['data']['lastName'], "Doe")
        self.assertEqual(response_data['data']['email'],
                         "jane.doe@example.com")

    def test_login_user_failure(self):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = self.app.post('/auth/login', json=login_data)
        self.assertEqual(response.status_code, 401)

    def test_register_missing_fields(self):
        required_fields = ["firstName", "lastName", "email", "password"]

        for field in required_fields:
            data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123"
            }
            data.pop(field)

            response = self.app.post('/auth/register', json=data)
            self.assertEqual(response.status_code, 422)
            response_data = response.get_json()
            self.assertIn('errors', response_data)
            self.assertIn(field, response_data['errors'][0]['message'])

    def test_register_duplicate_email(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "securepassword123"
        }

        # First registration should succeed
        response = self.app.post('/auth/register', json=data)
        self.assertEqual(response.status_code, 201)

        # Second registration with same email should fail
        response = self.app.post('/auth/register', json=data)
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertIn('Bad Request', response_data["status"])
        self.assertIn('Registration unsuccessful', response_data['message'])


if __name__ == '__main__':
    unittest.main()
