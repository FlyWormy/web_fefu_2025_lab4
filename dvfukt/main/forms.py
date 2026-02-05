from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Student, Course, Enrollment, Instructor


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        required=False,
        label='О себе',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    role = forms.ChoiceField(
        choices=Student.ROLE_CHOICES,
        initial='STUDENT',
        label='Роль',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    faculty = forms.ChoiceField(
        label='Факультет',
        choices=Student.FACULTY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date_of_birth = forms.DateField(
        label='Дата рождения',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password1', 'password2', 'phone', 'description',
            'role', 'faculty', 'date_of_birth'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        role = self.cleaned_data.get('role', 'STUDENT')

        if commit:
            user.save()
            profile = user.student_profile
            profile.phone = self.cleaned_data.get('phone', '')
            profile.description = self.cleaned_data.get('description', '')
            profile.role = role
            profile.faculty = self.cleaned_data.get('faculty', 'ИТ')
            profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            profile.save()


            if role == 'TEACHER':
                Instructor.objects.get_or_create(
                    email=user.email,
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'specialization': 'Преподаватель',
                        'faculty': profile.faculty,
                    }
                )

        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Email или имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        required=False,
        label='О себе',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

    avatar = forms.ImageField(
        required=False,
        label='Аватар',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    faculty = forms.ChoiceField(
        label='Факультет',
        choices=Student.FACULTY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date_of_birth = forms.DateField(
        label='Дата рождения',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Student
        fields = ['phone', 'description', 'avatar', 'faculty', 'date_of_birth']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.user.email and User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        # Получаем профиль, но не сохраняем пока
        profile = super().save(commit=False)

        # Устанавливаем связь с пользователем
        profile.user = self.user

        # Обновляем данные пользователя
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']

        if commit:
            self.user.save()
            profile.save()

        return profile


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label='Имя',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )

    subject = forms.CharField(
        label='Тема сообщения',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Тема сообщения'
        })
    )

    message = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше сообщение...',
            'rows': 5
        })
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise ValidationError('Имя должно содержать минимум 2 символа')
        return name

    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise ValidationError('Сообщение должно содержать минимум 10 символов')
        return message


class EnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        label='Курс',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')

        if self.student and course:
            if Enrollment.objects.filter(student=self.student, course=course).exists():
                raise ValidationError('Вы уже записаны на этот курс')

        return cleaned_data


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'faculty']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'duration_hours', 'instructor', 'is_active']


class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['first_name', 'last_name', 'email', 'specialization', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'specialization': 'Специализация',
            'is_active': 'Активен',
        }