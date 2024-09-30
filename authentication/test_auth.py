from django.test import TestCase, Client  # Import TestCase for test framework and Client to simulate browser requests
from django.urls import reverse  # reverse() is used to resolve URL names into actual URLs
from django.contrib.auth.models import User 


class AuthenticationViewTests(TestCase):
    def setUp(self):
        """
        The setUp method is run before every individual test.
        It initializes the client for HTTP requests and sets up URLs for registration and login views.
        """
        self.client = Client()  # Initialize the test client to simulate HTTP requests
        self.register_url = reverse('register')  # Resolve the URL for the registration view
        self.login_url = reverse('login')  # Resolve the URL for the login view

    def test_registration_success(self):
        """
        Test that a user can register successfully.
        A POST request is made with valid data (matching passwords).
        The user should be created, and the response should redirect (status code 302).
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',  # Provide a username for the new user
            'email': 'newuser@example.com',  # Provide an email for the new user
            'password': 'password123',  # Provide a password
            'confirm_password': 'password123'  # Confirm the password matches
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect (typically to a login page)
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Assert the user is saved in the database

    def test_registration_password_mismatch(self):
        """
        Test registration fails when passwords do not match.
        A POST request is made with non-matching passwords.
        The form should return an error, and the user should not be created.
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',  # Provide a username
            'email': 'newuser@example.com',  # Provide an email
            'password': 'password123',  # First password
            'confirm_password': 'wrongpassword'  # Non-matching confirm password
        })
        self.assertEqual(response.status_code, 200)  # Expect status code 200 (form re-rendered with error)
        self.assertContains(response, "Passwords don't match")  # Check that the error message appears in the response
        self.assertFalse(User.objects.filter(username='newuser').exists())  # Assert no user was created

    def test_login_success(self):
        """
        Test that a user can log in successfully.
        A POST request is made with correct username and password.
        The response should redirect (status code 302), and the session should contain the user's ID.
        """
        user = User.objects.create_user(username='testuser', password='password')  # Create a test user
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'})  # POST login request
        self.assertEqual(response.status_code, 302)  # Expect a redirect on successful login
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)  # Verify the session contains the correct user ID

    def test_login_failure(self):
        """
        Test login fails with incorrect credentials.
        A POST request is made with a non-existent username and incorrect password.
        The form should return an error, and the user should not be logged in.
        """
        response = self.client.post(self.login_url, {'username': 'nonexistentuser', 'password': 'wrongpassword'})  # POST invalid login
        self.assertEqual(response.status_code, 200)  # Expect status code 200 (form re-rendered with error)
        self.assertContains(response, 'Invalid Username or Password')  # Check that the error message appears in the response
