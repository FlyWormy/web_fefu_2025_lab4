from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth.models import User
from .forms import FeedbackForm, RegistrationForm


def index(request):
    return render(request, 'main/index.html')


def about(request):
    return render(request, 'main/about.html')


def student_profile(request, student_id):
    if student_id > 100:
        return render(request, 'main/student_profile.html', {
            'error': f'Студент с ID {student_id} не найден'
        }, status=404)
    return render(request, 'main/student_profile.html', {
        'student_id': student_id
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


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            request.session['form_data'] = {
                'username': username,
                'email': email
            }
            return redirect('success')
    else:
        form = RegistrationForm()

    return render(request, 'main/register.html', {'form': form})


def success_view(request):
    form_data = request.session.get('form_data', {})
    return render(request, 'main/success.html', {'form_data': form_data})