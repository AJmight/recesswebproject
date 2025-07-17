from django.urls import path
from . import views

app_name = 'appointments' # Namespace for this app's URLs

urlpatterns = [
    # Client URLs
    path('book/', views.book_appointment, name='book_appointment'),
    path('client/', views.client_appointments, name='client_appointments'),
    path('client/cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),

    # Therapist URLs
    path('therapist/', views.therapist_appointments, name='therapist_appointments'),
    path('therapist/manage/<int:pk>/', views.manage_appointment_status, name='manage_appointment_status'),
    path('therapist/availability/', views.therapist_set_availability, name='therapist_set_availability'),
    path('therapist/availability/delete/<int:pk>/', views.delete_availability, name='delete_availability'),

    # Add other paths as needed (e.g., specific appointment details)
]