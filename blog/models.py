from django.db import models
from django.utils import timezone
from django.conf import settings

from django.conf import settings




class Post(models.Model):
    title = models.CharField(max_length=100)
    intro = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return self.title