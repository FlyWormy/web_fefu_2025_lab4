from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    FACULTY_CHOICES = [
        ('ИТ', 'Информационные технологии'),
        ('МТ', 'Математика и компьютерные науки'),
        ('ФИ', 'Физика'),
        ('ХИ', 'Химия'),
        ('БИ', 'Биология'),
        ('ЭК', 'Экономика'),
    ]

    ROLE_CHOICES = (
        ('STUDENT', 'Студент'),
        ('TEACHER', 'Преподаватель'),
        ('ADMIN', 'Администратор'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Пользователь'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. Допускается до 15 цифр."
    )

    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name='Телефон'
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name='Роль'
    )

    date_of_birth = models.DateField(null=True, blank=True)
    faculty = models.CharField(max_length=2, choices=FACULTY_CHOICES, default='ИТ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_teacher(self):
        return self.role == 'TEACHER'

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_student(self):
        return self.role == 'STUDENT'

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
        )


@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    instance.student_profile.save()


class Instructor(models.Model):
    FACULTY_CHOICES = [
        ('ИТ', 'Информационные технологии'),
        ('МТ', 'Математика и компьютерные науки'),
        ('ФИ', 'Физика'),
        ('ХИ', 'Химия'),
        ('БИ', 'Биология'),
        ('ЭК', 'Экономика'),
    ]

    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email', unique=True)
    specialization = models.CharField('Специализация', max_length=200)
    faculty = models.CharField('Факультет', max_length=2, choices=FACULTY_CHOICES, default='ИТ')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']


class Course(models.Model):
    title = models.CharField('Название', max_length=200, unique=True)
    description = models.TextField('Описание')
    duration_hours = models.IntegerField(
        'Продолжительность (часов)',
        validators=[MinValueValidator(1), MaxValueValidator(300)]
    )

    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Преподаватель'
    )

    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('completed', 'Завершен'),
        ('dropped', 'Отчислен'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Оценка'
    )

    def __str__(self):
        return f"{self.student.student_profile.get_full_name()} - {self.course.title}"

    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['student', 'course']
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'