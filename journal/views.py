from django.shortcuts import render, redirect, get_object_or_404
from .models import JournalEntry
from .forms import JournalEntryForm

# View for the main journal page
def journal_entry(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            # Redirect to the newly created entry's detail page
            return redirect('journal_details', entry_id=entry.id)
    else:
        form = JournalEntryForm()

    # Fetch recent entries, show the 5 latest ones
    entries = JournalEntry.objects.order_by('-created_at')[:5]
    return render(request, 'journal.html', {
        'form': form, 
        'entries': entries
    })

# View for individual journal entry detail page
def journal_details(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id)
    recommendations = entry.get_recommendations()
    
    return render(request, 'journal_details.html', {
        'entry': entry,
        'recommendations': recommendations
    })
