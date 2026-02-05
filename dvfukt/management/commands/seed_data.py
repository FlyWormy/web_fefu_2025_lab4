from django.core.management.base import BaseCommand
from django.utils import timezone
from dvfukt.main.models import Student, Instructor, Course, Enrollment
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):

        instructor1 = Instructor.objects.create(
            first_name='Иван',
            last_name='Петров',
            email='i.petrov@university.ru',
            specialization='Программирование'
        )


        student1 = Student.objects.create(
            first_name='Анна',
            last_name='Иванова',
            email='anna@student.ru',
            faculty='ИТ'
        )


        course1 = Course.objects.create(
            title='Основы Python',
            description='Базовый курс Python',
            duration_hours=36,
            instructor=instructor1
        )


        Enrollment.objects.create(
            student=student1,
            course=course1,
            status='active'
        )

        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы'))