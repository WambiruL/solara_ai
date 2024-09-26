from django.contrib import admin
from .models import JournalEntry, Recommendation

# Register your models here.
admin.site.register(JournalEntry)
admin.site.register(Recommendation)