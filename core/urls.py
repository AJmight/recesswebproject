# core/urls.py

from django.urls import path
from . import views

app_name = 'core' # Namespace for the core app

urlpatterns = [
    # Changed 'views.home_view' to 'views.home' to match the function name in views.py
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('crisis-support/', views.crisis_support, name='crisis_support'),
    # Add any other core app specific URLs here
]
