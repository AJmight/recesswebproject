# users/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('therapists/', views.therapist_directory, name='therapist_directory'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Admin-specific user management paths
    path('admin/manage-therapists/', views.admin_manage_therapists, name='admin_manage_therapists'),
    path('admin/toggle-therapist-approval/<int:pk>/', views.admin_toggle_therapist_approval, name='admin_toggle_therapist_approval'),
    path('admin/edit-user/<int:pk>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/manage-clients/', views.admin_manage_clients, name='admin_manage_clients'),
    # NEW: URL for deleting users (clients or therapists)
    path('admin/delete-user/<int:pk>/', views.admin_delete_user, name='admin_delete_user'),
]
