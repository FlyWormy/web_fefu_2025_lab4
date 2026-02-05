from django.contrib import admin
from .models import Student, Course, Enrollment

class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'faculty', 'created_at')
    list_filter = ('faculty', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at',)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'duration_hours', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'instructor', 'description')
    ordering = ('title',)
    readonly_fields = ('created_at',)

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'status')
    list_filter = ('status', 'enrollment_date', 'course')
    search_fields = ('student__first_name', 'student__last_name', 'course__title')
    ordering = ('-enrollment_date',)
    readonly_fields = ('enrollment_date',)

admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)