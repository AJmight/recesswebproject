from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('', views.appointment_list, name='list'),
    path('<int:pk>/', views.appointment_detail, name='detail'),
    path('<int:pk>/update/', views.update_appointment, name='update'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
]