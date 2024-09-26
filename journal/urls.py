from django.urls import path
from .views import journal_entry, journal_details

urlpatterns = [
    path('journal_entry/', journal_entry, name='journal_entry'),
    path('journal/details/<int:entry_id>/', journal_details, name='journal_details'),
]
