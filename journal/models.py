from django.db import models
from textblob import TextBlob
from django.contrib.auth.models import User
from .utils import extract_keywords
import random

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sentiment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Analyze sentiment using TextBlob
        analysis = TextBlob(self.content)
        sentiment_score = analysis.sentiment.polarity

        # Set sentiment based on polarity score
        if sentiment_score > 0:
            self.sentiment = 'Positive'
        elif sentiment_score < 0:
            self.sentiment = 'Negative'
        else:
            self.sentiment = 'Neutral'

        super().save(*args, **kwargs)
        
    def get_recommendations(self):
        # Extract keywords from the content
        keywords = extract_keywords(self.content)
        
        # Fetch recommendations based on sentiment and keywords
        recommendations = list(Recommendation.objects.filter(
            models.Q(sentiment=self.sentiment) | 
            models.Q(title__icontains=keywords)
        ))

        # Randomly select 2 recommendations
        return random.sample(recommendations, min(2, len(recommendations)))

class Recommendation(models.Model):
    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]

    TYPE_CHOICES = [
        ('Video', 'Video'),
        ('Article', 'Article'),
        ('Podcast', 'Podcast'),
        ('Book', 'Book'),
    ]

    sentiment = models.CharField(max_length=50, choices=SENTIMENT_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    link = models.URLField()

    def __str__(self):
        return f"{self.type}: {self.title} ({self.sentiment})"

