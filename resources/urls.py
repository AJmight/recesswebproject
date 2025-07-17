from django.urls import path
from . import views

app_name = 'resources' # Namespace for this app's URLs

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('manage/', views.manage_resources, name='manage_resources'), 
   path('add/', views.add_resource, name='add_resource'),
    path('edit/<int:pk>/', views.edit_resource, name='edit_resource'),
    path('delete/<int:pk>/', views.delete_resource, name='delete_resource'),
]