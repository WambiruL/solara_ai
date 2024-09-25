from django.db import models
from textblob import TextBlob

class JournalEntry(models.Model):
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
