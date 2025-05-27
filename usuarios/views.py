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
    
    return render(request, 'usuarios/dashboard.html', {
        'courses': courses,
        'email_verified': email_verified,
        'active_membership': active_membership,
    })

@login_required
def my_courses(request):
    """Vista para mostrar los cursos del usuario."""
    # Filtrar cursos del usuario
    filter_type = request.GET.get('filter', 'all')
    
    user_courses = request.user.user_courses.all()
    
    if filter_type == 'completed':
        user_courses = user_courses.filter(completed=True)
    elif filter_type == 'in_progress':
        user_courses = user_courses.filter(completed=False, progress__gt=0)
    
    # Estadísticas
    total_courses = request.user.user_courses.count()
    completed_count = request.user.user_courses.filter(completed=True).count()
    in_progress_count = request.user.user_courses.filter(completed=False, progress__gt=0).count()
    
    context = {
        'user_courses': user_courses.order_by('-access_start'),
        'current_filter': filter_type,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
    }
    
    return render(request, 'usuarios/my_courses.html', context)