from django.urls import path
from landing_page.views import index


urlpatterns = [
    path('', index, name = "index"),
]
