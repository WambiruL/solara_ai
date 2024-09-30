from django.test import TestCase, Client  # Import TestCase for testing and Client for simulating HTTP requests
from django.urls import reverse  # reverse() is used to resolve URL names into their actual URLs
from django.contrib.auth.models import User 
from .models import JournalEntry  


class JournalEntryTests(TestCase):
    def setUp(self):
        """
        The setUp method is called before every individual test.
        It initializes the client for making HTTP requests, creates a test user,
        logs in the user, and resolves the URL for journal entries.
        """
        self.client = Client()  # Initialize the client to simulate browser requests
        self.user = User.objects.create_user(username='testuser', password='password')  # Create a test user
        self.client.login(username='testuser', password='password')  # Log in the test user
        self.journal_url = reverse('journal_entry')  # Resolve the URL for journal entry view

    def test_create_journal_entry(self):
        """
        Test the creation of a journal entry.
        The POST request submits journal content and should save the entry in the database.
        After saving, the user is redirected, so we check for a 302 status code.
        """
        response = self.client.post(self.journal_url, {'content': 'Today was a good day!'})  # Simulate POST request
        self.assertEqual(response.status_code, 302)  # Assert the response status code is 302 (redirection)
        self.assertTrue(JournalEntry.objects.filter(content='Today was a good day!').exists())  # Verify that the journal entry was saved

    def test_journal_list_entries(self):
        """
        Test if the journal entries are listed correctly.
        It creates a journal entry, sends a GET request to fetch the list of entries,
        and verifies that the entry is present in the response.
        """
        JournalEntry.objects.create(user=self.user, content='First entry')  # Create a journal entry in the database
        response = self.client.get(self.journal_url)  # Simulate a GET request to fetch the journal entries
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200 (OK)
        self.assertContains(response, 'First entry')  # Check if the response contains the created journal entry

    def test_sentiment_visualization(self):
        """
        Test if the sentiment visualization works correctly.
        It creates a journal entry with a positive sentiment, sends a GET request to the sentiment visualization view,
        and checks if the view successfully returns a sentiment graph (represented by 'graph_html' in the context).
        """
        JournalEntry.objects.create(user=self.user, content='I feel happy today!')  # Create a journal entry in the database
        sentiment_url = reverse('sentiment_visualization')  # Resolve the URL for the sentiment visualization view
        response = self.client.get(sentiment_url)  # Simulate a GET request to the sentiment visualization page
        self.assertEqual(response.status_code, 200)  # Assert the response status code is 200 (OK)
        self.assertIn('graph_html', response.context)  # Check if 'graph_html' is present in the context (indicating the graph is rendered)
