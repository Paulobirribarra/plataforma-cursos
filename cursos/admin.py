from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_available', 'is_visible', 'created_at')
    list_filter = ('is_available', 'is_visible')
    search_fields = ('title', 'description')