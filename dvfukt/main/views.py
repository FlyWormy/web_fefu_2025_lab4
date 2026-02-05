from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import (
    FeedbackForm, CustomUserCreationForm, EnrollmentForm,
    StudentForm, InstructorForm, CustomAuthenticationForm,
    ProfileUpdateForm
)
from .models import Student, Course, Enrollment, Instructor



def teacher_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'student_profile') and u.student_profile.is_teacher()
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'student_profile') and u.student_profile.is_admin()
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def student_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, 'student_profile') and u.student_profile.is_student()
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            backend_path = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend_path)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'main/registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if hasattr(user, 'backend'):
                    backend_path = user.backend
                else:
                    backend_path = 'django.contrib.auth.backends.ModelBackend'

                login(request, user, backend=backend_path)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                return redirect('profile')
            else:
                messages.error(request, 'Неверные учетные данные')
        else:
            messages.error(request, 'Неверные учетные данные')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'main/registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')



@login_required
def profile_view(request):
    profile = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')

    context = {
        'profile': profile,
        'enrollments': enrollments,
    }

    if profile.is_teacher():
        try:
            instructor_profile = Instructor.objects.get(email=request.user.email)
            courses = Course.objects.filter(instructor=instructor_profile)
            context['taught_courses'] = courses
        except Instructor.DoesNotExist:
            context['taught_courses'] = []

    return render(request, 'main/registration/profile.html', context)


@login_required
def profile_edit_view(request):
    profile, created = Student.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'main/registration/profile_edit.html', {'form': form})


@login_required
@student_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course').order_by('-enrollment_date')

    context = {
        'enrollments': enrollments,
        'profile': request.user.student_profile,
    }
    return render(request, 'main/dashboard/student.html', context)


@login_required
@teacher_required
def teacher_dashboard(request):

    try:
        instructor_profile = Instructor.objects.get(email=request.user.email)
        courses = Course.objects.filter(instructor=instructor_profile)

        course_stats = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course=course)
            course_stats.append({
                'course': course,
                'total_students': enrollments.count(),
                'has_grades': enrollments.filter(grade__isnull=False).count(),
            })

        context = {
            'courses': courses,
            'course_stats': course_stats,
            'profile': request.user.student_profile,
            'instructor_profile': instructor_profile,
        }
        return render(request, 'main/dashboard/teacher.html', context)
    except Instructor.DoesNotExist:
        profile = request.user.student_profile
        instructor_profile = Instructor.objects.create(
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            specialization='Преподаватель',
            faculty=profile.faculty,
        )
        messages.info(request, 'Профиль преподавателя создан')
        return redirect('teacher_dashboard')

@login_required
@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_users': recent_users,
        'profile': request.user.student_profile,
    }
    return render(request, 'main/dashboard/admin.html', context)



def index(request):
    total_students = Student.objects.count()
    total_courses = Course.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]

    return render(request, 'main/index.html', {
        'total_students': total_students,
        'total_courses': total_courses,
        'recent_courses': recent_courses
    })


def about(request):
    return render(request, 'main/about.html')


def make_teacher(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Обновляем роль
        profile = user.student_profile
        profile.role = 'TEACHER'
        profile.save()

        # Создаем профиль преподавателя
        Instructor.objects.get_or_create(
            email=user.email,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'specialization': 'Преподаватель',
                'faculty': profile.faculty,
            }
        )

        messages.success(request, f'{user.get_full_name()} теперь преподаватель')
        return redirect('student_list')

    return render(request, 'main/confirm_make_teacher.html', {'user': user})


@login_required
def student_profile(request, student_id=None):
    if student_id is None:
        student = request.user.student_profile
    else:
        student = get_object_or_404(Student, id=student_id)

    if not request.user.is_staff and request.user != student.user:
        messages.error(request, 'У вас нет прав для просмотра этого профиля')
        return redirect('profile')

    enrollments = student.user.enrollments.select_related('course').all()
    return render(request, 'main/student_profile.html', {
        'student': student,
        'enrollments': enrollments
    })


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            request.session['form_data'] = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject']
            }
            return redirect('success')
    else:
        form = FeedbackForm()

    return render(request, 'main/feedback.html', {'form': form})


def success_view(request):
    form_data = request.session.get('form_data', {})
    return render(request, 'main/success.html', {'form_data': form_data})


@login_required
def course_list(request):
    courses = Course.objects.filter(is_active=True)

    user_enrolled_courses = []
    if request.user.is_authenticated:
        user_enrolled_courses = Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True)

    return render(request, 'main/course_list.html', {
        'courses': courses,
        'user_enrolled_courses': user_enrolled_courses,
    })


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = course.enrollments.select_related('student').all()
    return render(request, 'main/course_detail.html', {
        'course': course,
        'enrollments': enrollments
    })


@login_required
def enrollment_view(request, student_id=None):
    if student_id:
        student = get_object_or_404(Student, id=student_id)
        if not request.user.is_staff and request.user != student.user:
            messages.error(request, 'У вас нет прав для записи на курсы от имени этого студента')
            return redirect('profile')
    else:
        student = request.user.student_profile

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, student=student.user)
        if form.is_valid():
            course = form.cleaned_data['course']
            Enrollment.objects.create(student=student.user, course=course)
            messages.success(request, f'Вы успешно записались на курс "{course.title}"')
            return redirect('student_profile', student_id=student.id)
    else:
        form = EnrollmentForm(student=student.user)

    return render(request, 'main/enrollment.html', {
        'student': student,
        'form': form
    })


@login_required
@teacher_required
def manage_course_students(request, course_id):

    try:
        instructor_profile = Instructor.objects.get(email=request.user.email)
        course = get_object_or_404(Course, id=course_id, instructor=instructor_profile)

        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            grade = request.POST.get('grade')

            if student_id and grade:
                try:
                    enrollment = Enrollment.objects.get(
                        course=course,
                        student_id=student_id
                    )
                    enrollment.grade = grade
                    enrollment.save()
                    messages.success(request, 'Оценка успешно обновлена')
                except Enrollment.DoesNotExist:
                    messages.error(request, 'Запись не найдена')

        enrollments = Enrollment.objects.filter(course=course).select_related('student')

        context = {
            'course': course,
            'enrollments': enrollments,
        }
        return render(request, 'main/course/manage_students.html', context)
    except Instructor.DoesNotExist:
        messages.error(request, 'Профиль преподавателя не найден')
        return redirect('profile')


@login_required
def student_list(request):
    students = Student.objects.all().order_by('last_name', 'first_name')
    return render(request, 'main/student_list.html', {'students': students})


@login_required
@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Студент успешно создан')
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'main/student_form.html', {'form': form})


@login_required
def instructor_list(request):
    instructors = Instructor.objects.all().order_by('last_name', 'first_name')
    return render(request, 'main/instructor_list.html', {'instructors': instructors})


@login_required
def instructor_detail(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    return render(request, 'main/instructor_detail.html', {'instructor': instructor})


@login_required
@admin_required
def instructor_create(request):
    if request.method == 'POST':
        form = InstructorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Преподаватель успешно создан')
            return redirect('instructor_list')
    else:
        form = InstructorForm()
    return render(request, 'main/instructor_form.html', {'form': form})


@login_required
@admin_required
def instructor_edit(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    if request.method == 'POST':
        form = InstructorForm(request.POST, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Преподаватель успешно обновлен')
            return redirect('instructor_detail', instructor_id=instructor.id)
    else:
        form = InstructorForm(instance=instructor)
    return render(request, 'main/instructor_form.html', {'form': form})

