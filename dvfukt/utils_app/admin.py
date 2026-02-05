from django.contrib import admin
from main.models import Instructor
@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'specialization', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')