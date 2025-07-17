
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('crisis-support/', views.crisis_support_view, name='crisis_support'),
     path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]