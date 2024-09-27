from django.shortcuts import render, redirect, get_object_or_404
from textblob import TextBlob
from .models import JournalEntry, Recommendation
from .forms import JournalEntryForm
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import plotly.express as px
import pandas as pd


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
    
    # Sorting functionality based on query parameters
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
        "Sentiment Score": [0] * 7,  # Sum of sentiment scores
        "Entry Count": [0] * 7       # Count of entries per day for averaging
    }

    # Helper function to get the index of a day
    def get_day_index(day):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days.index(day)

    # Process the journal entries and calculate sentiment scores for each day of the week
    for entry in entries:
        day_of_week = entry.created_at.strftime('%A')  # Get day name (e.g., 'Monday')
        day_index = get_day_index(day_of_week)
        
        # Assuming entry.sentiment is stored as a score (TextBlob polarity)
        sentiment_score = TextBlob(entry.content).sentiment.polarity  # Recalculate sentiment score
        data["Sentiment Score"][day_index] += sentiment_score
        data["Entry Count"][day_index] += 1

    # Calculate average sentiment score per day (to avoid division by zero)
    data["Average Sentiment"] = [
        (data["Sentiment Score"][i] / data["Entry Count"][i]) if data["Entry Count"][i] > 0 else 0
        for i in range(7)
    ]

    # Convert data to pandas DataFrame
    df = pd.DataFrame(data)

    # Create the line chart with Plotly (use Average Sentiment for y-axis)
    fig = px.line(df, x='Day', y='Average Sentiment',
                  title="Average Sentiment Score by Day of the Week",
                  labels={"Average Sentiment": "Average Sentiment Score"})

    # Custom styling of the plot
    fig.update_traces(
        mode="lines+markers",  # Line plot with markers
        marker=dict(size=10),   # Marker size
        line=dict(width=3)      # Line thickness
    )

    # Customize the line color for sentiment scores
    fig.update_traces(line=dict(color='#ffd9be'))
    # fig.update_traces(selector=dict(name="Happy"), line=dict(color='#A3E635'))  # Primary accent
    # fig.update_traces(selector=dict(name="Stressed"), line=dict(color='#f44336'))  # Secondary accent
    # fig.update_traces(selector=dict(name="Neutral"), line=dict(color='#ffd9be'))   # Neutral in Headings color

    # Customizing layout
    fig.update_layout(
        plot_bgcolor="#123332",  # Background color
        paper_bgcolor="#123332",  # Outer background color
        font=dict(family="Nunito", size=14, color="#f9eee7"),  # Text color (Text)
        title=dict(
            text="Mood Patterns Over the Week",
            x=0.5,  # Center the title
            font=dict(size=20, color="#ffd9be", weight=700)  # Title in Headings color
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
            title="Overall Mood Change",  # Axis title
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