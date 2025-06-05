from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'image')
    readonly_fields = ['image']

admin.site.register(Post, PostAdmin)