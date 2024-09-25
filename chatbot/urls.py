from django.urls import path
from .views import chatbot, submit_feedback


urlpatterns = [
    path('solara_ai/', chatbot, name = "chatbot" ),
    path('submit_feedback/', submit_feedback, name = 'submit_feedback'),
]
