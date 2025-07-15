from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_home, name='chat_home'),
    path('chat/<str:username>/', views.chat_view, name='chat_room'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
