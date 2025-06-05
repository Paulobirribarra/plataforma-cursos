from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from blog import models
from .models import Post
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.shortcuts import redirect

def posts(request):
    # Mostrar todos los posts, para todos
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/posts.html', context)


@login_required
def newPost(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:posts')  # Usa el nombre definido en urls.py
    else:
        form = PostForm()
    return render(request, 'blog/newpost.html', {'form': form})


@login_required
def myPost(request):
    # Mostrar solo posts del usuario autenticado
    context = {
        'posts': Post.objects.filter(author=request.user)
    }
    return render(request, 'blog/mypost.html', context)