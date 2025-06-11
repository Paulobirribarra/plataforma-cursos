#plataforma-cursos/usuarios/views.py
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from cursos.models import Course
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import datetime
from .forms import CustomUserCreationForm, NewsletterPreferencesForm, UserProfileForm
from allauth.account.models import EmailAddress
from allauth.account.views import SignupView

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def check_email_available(request):
    """
    Vista AJAX para verificar si un email está disponible para registro
    """
    import json
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({
            'available': False,
            'message': 'Error en la solicitud'
        })
    
    if not email:
        return JsonResponse({
            'available': True,
            'message': ''
        })
    
    # Verificar formato de email básico
    if '@' not in email or '.' not in email.split('@')[1]:
        return JsonResponse({
            'available': False,
            'message': 'Por favor, ingresa un email válido'
        })
    
    User = get_user_model()
    
    # Verificar si el email ya existe
    email_exists = User.objects.filter(email__iexact=email).exists()
    
    if email_exists:
        return JsonResponse({
            'available': False,
            'message': 'Este email ya está registrado. <a href="/accounts/login/" class="text-blue-600 hover:underline">¿Ya tienes cuenta?</a>'
        })
    else:
        return JsonResponse({
            'available': True,
            'message': '✓ Email disponible'
        })

class CustomSignupView(SignupView):
    form_class = CustomUserCreationForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        try:
            logger.info(f"Usuario registrado: {form.cleaned_data['email']}")
            return super().form_valid(form)
        except ValidationError as e:
            # Capturar errores de validación y agregarlos al formulario
            form.add_error('password1', e)
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        # Registrar los errores para depuración
        logger.warning(f"Error en formulario de registro: {form.errors}")
        return super().form_invalid(form)

register = CustomSignupView.as_view()

@login_required
def dashboard(request):
    # Verificar si el correo del usuario está confirmado
    email_verified = EmailAddress.objects.filter(user=request.user, verified=True).exists()
    
    if not email_verified:
        logger.warning(f"Usuario no verificado intentó acceder al dashboard: {request.user.email}")
        messages.warning(request, "Por favor, verifica tu correo electrónico para acceder al dashboard.")
        return redirect('account_email_verification_sent')
    
    logger.info(f"Acceso al dashboard por usuario: {request.user.email}")
    courses = Course.objects.all() if request.user.is_staff else []
    
    # Obtener membresía activa del usuario
    from membresias.models import Membership
    active_membership = Membership.objects.filter(
        user=request.user, 
        status='active'
    ).first()
    
    # Información sobre cursos de recompensa
    reward_courses_info = None
    if active_membership:
        reward_courses_info = {
            'remaining': active_membership.welcome_courses_remaining,
            'can_claim': active_membership.can_claim_reward_course(),
            'available_courses': active_membership.get_available_reward_courses()[:3],  # Mostrar solo 3 en el dashboard
            'total_available': active_membership.get_available_reward_courses().count(),
        }
      # Contar cursos del usuario
    user_courses_count = request.user.user_courses.count()    # Contar items en el carrito
    from carrito.models import Cart, CartItem
    active_cart = Cart.objects.filter(user=request.user, is_active=True).first()
    cart_items_count = CartItem.objects.filter(cart=active_cart).count() if active_cart else 0
      # Obtener estadísticas de boletines (solo para staff)
    newsletter_stats = {}
    if request.user.is_staff:
        from boletines.models import Boletin
        newsletter_stats = {
            'total': Boletin.objects.count(),
            'enviados': Boletin.objects.filter(estado='enviado').count(),
            'borrador': Boletin.objects.filter(estado='borrador').count(),
            'programados': Boletin.objects.filter(estado='programado').count(),
        }
    
    # Obtener pagos recientes del usuario
    from pagos.models import Payment
    recent_payments = Payment.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]  # Últimos 5 pagos
    
    return render(request, 'usuarios/dashboard.html', {
        'courses': courses,
        'email_verified': email_verified,
        'active_membership': active_membership,
        'reward_courses_info': reward_courses_info,
        'user_courses_count': user_courses_count,
        'cart_items_count': cart_items_count,
        'newsletter_stats': newsletter_stats,
        'recent_payments': recent_payments,
    })

@login_required
def my_courses(request):
    """Vista para mostrar los cursos del usuario (comprados + accesibles por membresía)."""
    from cursos.models import Course
    from membresias.models import Membership
    from cursos.views import check_course_access
    
    # Filtro de tipo
    filter_type = request.GET.get('filter', 'all')
    
    # Obtener cursos comprados directamente
    purchased_courses = request.user.user_courses.all()
    
    # Obtener cursos accesibles por membresía activa
    accessible_course_ids = []
    active_membership = request.user.get_active_membership()
    
    if active_membership:
        # Verificar qué cursos puede acceder con su membresía
        membership_courses = Course.objects.filter(
            membership_required=True,
            is_available=True
        )
        
        for course in membership_courses:
            can_access, _ = check_course_access(request.user, course)
            if can_access:
                accessible_course_ids.append(course.id)
    
    # Crear lista unificada evitando duplicados
    user_courses_list = list(purchased_courses)
    
    # Agregar cursos de membresía que no estén ya comprados
    already_purchased_course_ids = [uc.course.id for uc in purchased_courses]
    
    for course_id in accessible_course_ids:
        if course_id not in already_purchased_course_ids:
            course = Course.objects.get(id=course_id)
            # Crear un objeto pseudo-UserCourse para cursos de membresía
            pseudo_user_course = type('obj', (object,), {
                'course': course,
                'progress': 0.0,
                'completed': False,
                'access_start': active_membership.start_date,
                'access_end': active_membership.end_date,
                'is_membership_access': True
            })()
            user_courses_list.append(pseudo_user_course)
    
    # Aplicar filtros
    if filter_type == 'completed':
        user_courses_list = [uc for uc in user_courses_list if getattr(uc, 'completed', False)]
    elif filter_type == 'in_progress':
        user_courses_list = [uc for uc in user_courses_list if not getattr(uc, 'completed', False) and getattr(uc, 'progress', 0) > 0]
    
    # Estadísticas
    total_courses = len(user_courses_list)
    completed_count = len([uc for uc in user_courses_list if getattr(uc, 'completed', False)])
    in_progress_count = len([uc for uc in user_courses_list if not getattr(uc, 'completed', False) and getattr(uc, 'progress', 0) > 0])
    
    context = {
        'user_courses': user_courses_list,
        'current_filter': filter_type,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'total_courses': total_courses,
        'active_membership': active_membership,
    }
    
    return render(request, 'usuarios/my_courses.html', context)

@login_required
def newsletter_preferences(request):
    """Vista para gestionar las preferencias de newsletter del usuario"""
    if request.method == 'POST':
        form = NewsletterPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            action = 'suscrito' if form.cleaned_data['suscrito_newsletter'] else 'desuscrito'
            messages.success(request, f'Te has {action} al newsletter exitosamente.')
            
            # Log para tracking
            logger.info(f"Usuario {request.user.email} se ha {action} del newsletter")
            
            return redirect('usuarios:newsletter_preferences')
    else:
        form = NewsletterPreferencesForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'newsletter_stats': _get_newsletter_stats(request.user)
    }
    return render(request, 'usuarios/newsletter_preferences.html', context)

@login_required
def toggle_newsletter_ajax(request):
    """Vista AJAX para alternar suscripción al newsletter"""
    if request.method == 'POST':
        user = request.user
        user.suscrito_newsletter = not user.suscrito_newsletter
        user.save(update_fields=['suscrito_newsletter'])
        
        action = 'suscrito' if user.suscrito_newsletter else 'desuscrito'
        logger.info(f"Usuario {user.email} cambió suscripción newsletter via AJAX: {action}")
        
        return JsonResponse({
            'success': True,
            'suscrito': user.suscrito_newsletter,
            'message': f'Te has {action} al newsletter exitosamente.'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@login_required
def profile_preferences(request):
    """Vista para gestionar el perfil completo del usuario"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            logger.info(f"Usuario {request.user.email} actualizó su perfil")
            return redirect('usuarios:profile_preferences')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'newsletter_stats': _get_newsletter_stats(request.user)
    }
    return render(request, 'usuarios/profile_preferences.html', context)

def _get_newsletter_stats(user):
    """Función auxiliar para obtener estadísticas de newsletter del usuario"""
    try:
        from boletines.models import Boletin
        # Obtener últimos boletines enviados
        ultimos_boletines = Boletin.objects.filter(
            estado='enviado'
        ).order_by('-fecha_envio')[:5]
        
        return {
            'total_boletines_enviados': Boletin.objects.filter(estado='enviado').count(),
            'ultimos_boletines': ultimos_boletines,
            'fecha_suscripcion': user.date_joined,
        }
    except ImportError:
        return {
            'total_boletines_enviados': 0,
            'ultimos_boletines': [],
            'fecha_suscripcion': user.date_joined,
        }