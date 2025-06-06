#plataforma-cursos/usuarios/views.py
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from cursos.models import Course
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import datetime
from .forms import CustomUserCreationForm
from allauth.account.models import EmailAddress
from allauth.account.views import SignupView

logger = logging.getLogger(__name__)

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
    
    return render(request, 'usuarios/dashboard.html', {
        'courses': courses,
        'email_verified': email_verified,
        'active_membership': active_membership,
        'reward_courses_info': reward_courses_info,
        'user_courses_count': user_courses_count,
        'cart_items_count': cart_items_count,
        'newsletter_stats': newsletter_stats,
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