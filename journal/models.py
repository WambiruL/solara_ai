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
        
    def get_recommendations(self):
        recommendations = {
            'Positive': [
                {"type": "Video", "title": "How to Stay Productive", "link": "https://www.youtube.com/watch?v=positive_video1"},
                {"type": "Article", "title": "10 Tips for Maintaining Positivity", "link": "https://example.com/positive-article1"},
            ],
            'Negative': [
                {"type": "Video", "title": "Mindfulness Meditation", "link": "https://www.youtube.com/watch?v=negative_video1"},
                {"type": "Article", "title": "Coping with Stress", "link": "https://example.com/negative-article1"},
            ],
            'Neutral': [
                {"type": "Video", "title": "Daily Mindfulness Practices", "link": "https://www.youtube.com/watch?v=neutral_video1"},
                {"type": "Article", "title": "The Power of Calm", "link": "https://example.com/neutral-article1"},
            ]
        }
        return recommendations.get(self.sentiment, [])
