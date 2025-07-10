from django import views
from django.urls import path
from .views import register, profile, home
from . import views

app_name = 'users'


urlpatterns = [
    path('', home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         views.password_reset_confirm, 
         name='password_reset_confirm'),
]
