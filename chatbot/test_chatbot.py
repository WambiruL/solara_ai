from django.test import TestCase, Client  # Import TestCase for unit testing, and Client to simulate HTTP requests
from django.urls import reverse  # reverse() is used to resolve view names into URLs
from django.contrib.auth.models import User  
from .models import Chat, Feedback 
import json  


class ChatbotViewTests(TestCase):
    def setUp(self):
        """
        The setUp method is called before every test case. It initializes the test client,
        creates a test user, and sets the URL for the chatbot view.
        """
        self.client = Client()  # Initialize the test client to simulate HTTP requests
        self.user = User.objects.create_user(username='testuser', password='password')  # Create a test user
        self.chatbot_url = reverse('chatbot')  # Resolve the chatbot URL using the reverse function

    def test_chatbot_authenticated_user(self):
        """
        Test if an authenticated user can access the chatbot view. 
        It checks if the chatbot page is successfully rendered with a status code of 200 
        and ensures the correct template is used.
        """
        self.client.login(username='testuser', password='password')  # Log in the test user
        response = self.client.get(self.chatbot_url)  # Simulate a GET request to the chatbot URL
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200 (OK)
        self.assertTemplateUsed(response, 'chatbot.html')  # Assert that the correct template is used

    def test_chatbot_post_message(self):
        """
        Test if posting a message to the chatbot saves the message in the database.
        Verifies that the response contains the message and the message is saved in the Chat model.
        """
        self.client.login(username='testuser', password='password')  # Log in the test user
        response = self.client.post(self.chatbot_url, {'message': 'Hello!'})  # Simulate POST request with message
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200
        self.assertIn('message', response.json())  # Check if the response contains the 'message' key
        self.assertTrue(Chat.objects.filter(user=self.user, message='Hello!').exists())  # Check if message is saved in the database

    def test_chatbot_post_empty_message(self):
        """
        Test submitting an empty message to the chatbot. 
        It should return a 400 (Bad Request) status code and an error message in the response.
        """
        self.client.login(username='testuser', password='password')  # Log in the test user
        response = self.client.post(self.chatbot_url, {'message': ''})  # Simulate POST request with empty message
        self.assertEqual(response.status_code, 400)  # Assert the response status code is 400 (Bad Request)
        self.assertIn('error', response.json())  # Check if the response contains an 'error' key

    def test_chatbot_without_authentication(self):
        """
        Test if an unauthenticated user can access the chatbot view. 
        It should still allow access to the chatbot page with a status code of 200.
        """
        response = self.client.get(self.chatbot_url)  # Simulate a GET request without logging in
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200 (OK)


class FeedbackSubmissionTests(TestCase):
    def setUp(self):
        """
        The setUp method initializes the test client and resolves the feedback submission URL.
        """
        self.client = Client()  # Initialize the test client
        self.submit_feedback_url = reverse('submit_feedback')  # Resolve the feedback submission URL

    def test_feedback_submission(self):
        """
        Test submitting valid feedback. 
        It verifies that the feedback is saved in the Feedback model and returns a success status.
        """
        response = self.client.post(
            self.submit_feedback_url,
            data=json.dumps({'feedback': 'Great bot!'}),  # Simulate POST request with feedback in JSON format
            content_type="application/json"  # Specify content type as JSON
        )
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200 (OK)
        self.assertEqual(response.json()['status'], 'success')  # Assert the response contains 'success' status
        self.assertTrue(Feedback.objects.filter(feedback='Great bot!').exists())  # Check if feedback is saved in the database

    def test_invalid_feedback_submission(self):
        """
        Test submitting invalid feedback (empty data). 
        It should return a 400 (Bad Request) status and an error message.
        """
        response = self.client.post(
            self.submit_feedback_url,
            data=json.dumps({}),  # Simulate POST request with empty feedback
            content_type="application/json"  # Specify content type as JSON
        )
        self.assertEqual(response.status_code, 400)  # Assert the response status code is 400 (Bad Request)
        self.assertEqual(response.json()['status'], 'error')  # Assert the response contains 'error' status
