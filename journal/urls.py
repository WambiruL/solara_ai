from django.urls import path
from . import views

urlpatterns = [
    path('journal_entry/', views.journal_entry, name='journal_entry'),
    path('journal/details/<int:entry_id>/', views.journal_details, name='journal_details'),
    path('my-entries/', views.my_entries, name='my_entries'),
    path('sentiment-visualization/', views.sentiment_visualization, name='sentiment_visualization'),
]
