# chatapp/urls.py
from django.urls import path
from . import views

app_name = 'chatapp' # Define app_name for namespacing

urlpatterns = [
    path('chat/', views.chat_home, name='chat_home'), # Main chat contacts/groups list
    path('chat/<str:username>/', views.chat_view, name='chat_room'), # Specific chat room with a user
]