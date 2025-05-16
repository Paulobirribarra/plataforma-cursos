#cursos/admin.py
from django.contrib import admin
from .models import Category, Course, Tag, CourseResource, UserCourse, DiscountCode

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_free', 'is_available', 'is_visible', 'base_price', 'created_by', 'created_at')
    list_filter = ('is_free', 'is_available', 'is_visible', 'category', 'created_by')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'type', 'created_at')
    list_filter = ('type', 'course')
    search_fields = ('title',)

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'access_start', 'access_end', 'progress', 'completed')
    list_filter = ('completed', 'course')
    search_fields = ('user__email', 'course__title')

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('course', 'code', 'discount_percentage', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('course__title', 'code')