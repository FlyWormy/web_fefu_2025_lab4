from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('success/', views.success_view, name='success'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('student/', views.student_profile, name='student_profile_current'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('student/create/', views.student_create, name='student_create'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enrollment/', views.enrollment_view, name='enrollment_current'),
    path('enrollment/<int:student_id>/', views.enrollment_view, name='enrollment'),
    path('course/<int:course_id>/manage/', views.manage_course_students, name='manage_course_students'),
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('instructor/create/', views.instructor_create, name='instructor_create'),
    path('instructor/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),
    path('instructor/<int:instructor_id>/edit/', views.instructor_edit, name='instructor_edit'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)