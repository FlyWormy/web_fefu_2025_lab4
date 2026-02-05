from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('register/', views.register_view, name='register'),
    path('success/', views.success_view, name='success'),
]