from django.urls import path
from .views import journal_entry

urlpatterns = [
    path('journal_entry/', journal_entry, name='journal_entry'),
]
