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
        logger.info(f"Usuario registrado: {form.cleaned_data['email']}")
        return super().form_valid(form)

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
    return render(request, 'usuarios/dashboard.html', {
        'courses': courses,
        'email_verified': email_verified,
    })