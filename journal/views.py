from django.shortcuts import render, redirect, get_object_or_404
from .models import JournalEntry
from .forms import JournalEntryForm
from django.core.paginator import Paginator

# View for the main journal page
def journal_entry(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit= False)
            entry.user = request.user
            entry.save()
            # Redirect to the newly created entry's detail page
            return redirect('journal_details', entry_id=entry.id)
    else:
        form = JournalEntryForm()

    # Fetch recent entries, show the 5 latest ones
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')[:3]
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

# My entries
def my_entries(request):
    # Get all the entries for the logged-in user
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
    
    # Optional: Add sorting functionality based on query parameters
    sort_option = request.GET.get('sort', '')
    if sort_option == 'date_asc':
        entries = entries.order_by('created_at')
    elif sort_option == 'date_desc':
        entries = entries.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(entries, 10)  # Show 10 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context to pass to the template
    context = {
        'entries': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'my_entries.html', context)