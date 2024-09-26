from django.shortcuts import render, redirect, get_object_or_404
from .models import JournalEntry
from .forms import JournalEntryForm
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import plotly.express as px
import pandas as pd
from collections import defaultdict

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

def sentiment_visualization(request):
    # Fetch entries for the logged-in user (over the last 30 days)
    user = request.user
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    entries = JournalEntry.objects.filter(user=user, created_at__range=[thirty_days_ago, today])

    # Prepare data for charting (grouping by day of the week)
    data = {
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Positive": [0] * 7,
        "Negative": [0] * 7,
        "Neutral": [0] * 7
    }

    # Helper function to get the index of a day
    def get_day_index(day):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days.index(day)

    # Process the journal entries and count sentiments for each day of the week
    for entry in entries:
        day_of_week = entry.created_at.strftime('%A')  # Get day name (e.g., 'Monday')
        day_index = get_day_index(day_of_week)
        if entry.sentiment == 'Positive':
            data["Positive"][day_index] += 1
        elif entry.sentiment == 'Negative':
            data["Negative"][day_index] += 1
        else:
            data["Neutral"][day_index] += 1

    # Convert data to pandas DataFrame
    df = pd.DataFrame(data)

    # Create the line chart with Plotly
    fig = px.line(df, x='Day', y=['Positive', 'Negative', 'Neutral'],
                  title="Sentiment Analysis by Day of the Week",
                  labels={"value": "Count", "variable": "Sentiment Type"})

    # Custom styling of the plot
    fig.update_traces(
        mode="lines+markers",  # Line plot with markers
        marker=dict(size=10),   # Marker size
        line=dict(width=3)      # Line thickness
    )
    
    # Customize the lines for each sentiment
    fig.update_traces(selector=dict(name="Positive"), line=dict(color='#ef9c82'))  # Primary accent
    fig.update_traces(selector=dict(name="Negative"), line=dict(color='#1d4241'))  # Secondary accent
    fig.update_traces(selector=dict(name="Neutral"), line=dict(color='#ffd9be'))   # Neutral in Headings color

    # Customizing layout
    fig.update_layout(
        plot_bgcolor="#123332",  # Background color
        paper_bgcolor="#123332",  # Outer background color
        font=dict(family="Arial", size=14, color="#f9eee7"),  # Text color (Text)
        title=dict(
            text="Sentiment Analysis by Day of the Week",
            x=0.5,  # Center the title
            font=dict(size=20, color="#ffd9be", weight = 700)  # Title in Headings color
        ),
        xaxis=dict(
            title="Day of the Week",  # Axis title
            titlefont=dict(size=15, color="#ffd9be"),  # Headings color for axis title
            tickfont=dict(size=14, color="#f9eee7"),  # Text color for ticks
            showgrid=True,  # Show vertical gridlines
            gridcolor="rgba(200, 200, 200, 0.3)",  # Light gridlines
            zeroline=False
        ),
        yaxis=dict(
            title="Sentiment Count",  # Axis title
            titlefont=dict(size=15, color="#ffd9be"),  # Headings color for axis title
            tickfont=dict(size=14, color="#f9eee7"),  # Text color for ticks
            showgrid=True,  # Show horizontal gridlines
            gridcolor="rgba(200, 200, 200, 0.3)",  # Light gridlines
            zeroline=False
        ),
        legend=dict(
            title="Sentiment Type",
            font=dict(size=14, color="#f9eee7"),  # Text color for legend
            bordercolor="rgba(255, 255, 255, 0.5)",  # Border for legend box
            borderwidth=1
        )
    )

    # Render chart to HTML
    graph_html = fig.to_html(full_html=False)
    return render(request, 'sentiment_visualization.html', {'graph_html': graph_html})
