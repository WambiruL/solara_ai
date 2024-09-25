from django.shortcuts import render, redirect
from .models import JournalEntry
from .forms import JournalEntryForm

def journal_entry(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            recommendations = entry.get_recommendations()
            return render(request, 'journal.html', {'form': form, 'entries': [entry], 'recommendations': recommendations})
    else:
        form = JournalEntryForm()

    # Fetch recent entries
    entries = JournalEntry.objects.order_by('-created_at')[:5]
    return render(request, 'journal.html', {'form': form, 'entries': entries})
