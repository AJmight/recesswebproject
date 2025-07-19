# assessments/urls.py

from django.urls import path
from . import views

app_name = 'assessments' # Namespace for this app's URLs

urlpatterns = [
    # Removed redundant paths (admin, home, about, contact, resources, book, client, therapist, etc.)
    # These should be handled in your main project urls.py or other app urls.py files.

    path('', views.assessment_list, name='assessment_list'), # New: list available assessments
    path('take/<int:assessment_id>/', views.take_assessment, name='take_assessment'), # Pass assessment_id
    path('results/<int:user_assessment_id>/', views.assessment_result, name='assessment_result'),
     path('my-results/', views.my_assessment_results, name='my_results'), # List all past results for the current user
    
    # Admin-specific paths for managing assessments (optional, but good for control)
    path('manage/', views.manage_assessments, name='manage_assessments'),
    path('manage/add/', views.add_assessment, name='add_assessment'),
    path('manage/edit/<int:pk>/', views.edit_assessment, name='edit_assessment'),
    path('manage/delete/<int:pk>/', views.delete_assessment, name='delete_assessment'),
    path('manage/questions/<int:assessment_id>/', views.manage_questions, name='manage_questions'),
    path('manage/questions/<int:assessment_id>/add/', views.add_question, name='add_question'),
    path('manage/questions/edit/<int:pk>/', views.edit_question, name='edit_question'),
    path('manage/questions/delete/<int:pk>/', views.delete_question, name='delete_question'),
    
    path('upload/', views.upload_assessment, name='upload_assessment'), # NEW: Upload assessment via JSON
]

