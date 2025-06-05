from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.utils.text import slugify
from .models import BlogPost
from .forms import BlogPostForm


def is_admin_user(user):
    """Verificar si el usuario es administrador (staff o superuser)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def blog_list(request):
    """Vista para mostrar lista de posts del blog"""
    posts = BlogPost.objects.filter(activo=True).order_by('-fecha_publicacion')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query and query.strip():
        posts = posts.filter(
            Q(titulo__icontains=query) | 
            Q(contenido__icontains=query) |
            Q(resumen__icontains=query)
        )
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        posts = posts.filter(categoria=categoria)
    
    # Paginación
    paginator = Paginator(posts, 6)  # 6 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Posts destacados para sidebar
    posts_destacados = BlogPost.objects.filter(activo=True, destacado=True)[:3]
    
    # Categorías para filtro
    categorias = BlogPost.CATEGORIA_CHOICES
    context = {
        'page_obj': page_obj,
        'posts_destacados': posts_destacados,
        'categorias': categorias,
        'query': query if query.strip() else '',
        'categoria_actual': categoria,
    }
    
    return render(request, 'blog/list.html', context)

def blog_by_category(request, categoria):
    """Vista para mostrar posts por categoría"""
    posts = BlogPost.objects.filter(activo=True, categoria=categoria).order_by('-fecha_publicacion')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query and query.strip():
        posts = posts.filter(
            Q(titulo__icontains=query) | 
            Q(contenido__icontains=query) |
            Q(resumen__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener nombre de categoría
    categoria_nombre = dict(BlogPost.CATEGORIA_CHOICES).get(categoria, categoria)
    context = {
        'page_obj': page_obj,
        'categoria': categoria,
        'categoria_nombre': categoria_nombre,
        'categorias': BlogPost.CATEGORIA_CHOICES,
        'query': query if query.strip() else '',
        'categoria_actual': categoria,
    }
    
    return render(request, 'blog/category.html', context)

def blog_detail(request, slug):
    """Vista para mostrar un post individual"""
    post = get_object_or_404(BlogPost, slug=slug, activo=True)
    
    # Incrementar contador de visitas
    post.incrementar_visitas()
    
    # Posts relacionados
    posts_relacionados = post.posts_relacionados()
    
    # Posts recientes para sidebar
    posts_recientes = BlogPost.objects.filter(activo=True).exclude(id=post.id)[:5]
    
    context = {
        'post': post,
        'posts_relacionados': posts_relacionados,
        'posts_recientes': posts_recientes,
    }
    
    return render(request, 'blog/detail.html', context)

def posts_destacados_json(request):
    """API para obtener posts destacados (para usar en página nosotros)"""
    posts = BlogPost.objects.filter(activo=True, destacado=True)[:3]
    
    data = []
    for post in posts:
        data.append({
            'id': post.id,
            'titulo': post.titulo,
            'resumen': post.resumen,
            'categoria': post.get_categoria_display(),
            'categoria_key': post.categoria,
            'fecha_publicacion': post.fecha_publicacion.strftime('%d/%m/%Y'),
            'imagen_url': post.imagen_destacada.url if post.imagen_destacada else None,
            'url': post.get_absolute_url(),
            'tiempo_lectura': post.tiempo_lectura,
        })
    
    return JsonResponse({'posts': data})


@login_required
@user_passes_test(is_admin_user)
def blog_admin_list(request):
    """Lista de publicaciones para administradores"""
    posts = BlogPost.objects.all().order_by('-fecha_publicacion')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(titulo__icontains=query) | 
            Q(contenido__icontains=query) |
            Q(resumen__icontains=query)
        )
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        posts = posts.filter(categoria=categoria)
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado == 'activo':
        posts = posts.filter(activo=True)
    elif estado == 'inactivo':
        posts = posts.filter(activo=False)
    elif estado == 'destacado':
        posts = posts.filter(destacado=True)
    
    # Paginación
    paginator = Paginator(posts, 10)  # 10 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categorias': BlogPost.CATEGORIA_CHOICES,
        'query': query,
        'categoria_actual': categoria,
        'estado_actual': estado,
    }
    
    return render(request, 'blog/admin/list.html', context)


@login_required
@user_passes_test(is_admin_user)
def blog_create(request):
    """Vista para crear nueva publicación"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, "¡Publicación creada exitosamente!")
            return redirect('blog:admin_list')
    else:
        form = BlogPostForm()
    
    context = {
        'form': form,
        'action': 'crear',
        'title': 'Crear Nueva Publicación',
        'button_text': 'Crear Publicación'
    }
    
    return render(request, 'blog/admin/form.html', context)


@login_required
@user_passes_test(is_admin_user)
def blog_edit(request, id):
    """Vista para editar publicación existente"""
    post = get_object_or_404(BlogPost, id=id)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Publicación actualizada exitosamente!")
            return redirect('blog:admin_list')
    else:
        form = BlogPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'action': 'editar',
        'title': f'Editar: {post.titulo}',
        'button_text': 'Actualizar Publicación'
    }
    
    return render(request, 'blog/admin/form.html', context)


@login_required
@user_passes_test(is_admin_user)
def blog_delete(request, id):
    """Vista para eliminar publicación"""
    post = get_object_or_404(BlogPost, id=id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "¡Publicación eliminada exitosamente!")
        return redirect('blog:admin_list')
    
    context = {
        'post': post,
    }
    
    return render(request, 'blog/admin/confirm_delete.html', context)


@login_required
@user_passes_test(is_admin_user)
def blog_preview(request, id):
    """Vista de previsualización para una publicación"""
    post = get_object_or_404(BlogPost, id=id)
    
    context = {
        'post': post,
        'is_preview': True,
    }
    
    return render(request, 'blog/admin/preview.html', context)
