#plataforma-cursos\usuarios\views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from cursos.models import Course
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import datetime

@login_required
def dashboard(request):
    courses = Course.objects.all() if request.user.is_staff else []
    return render(request, 'usuarios/dashboard.html', {'courses': courses})

@staff_member_required
def course_create_admin(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_available = request.POST.get('is_available') == 'on'
        is_visible = request.POST.get('is_visible') == 'on'
        duration_str = request.POST.get('duration')
        price = request.POST.get('price')
        discount_basic = request.POST.get('discount_basic', '0')
        discount_intermediate = request.POST.get('discount_intermediate', '0')
        discount_premium = request.POST.get('discount_premium', '0')
        discount_code = request.POST.get('discount_code')
        discount_code_percentage = request.POST.get('discount_code_percentage', '0')
        external_link = request.POST.get('external_link')

        # Normalizar y validar valores decimales
        try:
            price = Decimal(str(price).replace(',', '.')) if price else Decimal('0.00')
            discount_basic = Decimal(str(discount_basic).replace(',', '.').strip()) if discount_basic else Decimal('0.00')
            discount_intermediate = Decimal(str(discount_intermediate).replace(',', '.').strip()) if discount_intermediate else Decimal('0.00')
            discount_premium = Decimal(str(discount_premium).replace(',', '.').strip()) if discount_premium else Decimal('0.00')
            discount_code_percentage = Decimal(str(discount_code_percentage).replace(',', '.').strip()) if discount_code_percentage else Decimal('0.00')

            # Asegurar que los descuentos sean porcentajes válidos (0-100)
            if not (0 <= discount_basic <= 100):
                raise ValidationError("El descuento básico debe estar entre 0 y 100.")
            if not (0 <= discount_intermediate <= 100):
                raise ValidationError("El descuento intermedio debe estar entre 0 y 100.")
            if not (0 <= discount_premium <= 100):
                raise ValidationError("El descuento premium debe estar entre 0 y 100.")
            if not (0 <= discount_code_percentage <= 100):
                raise ValidationError("El porcentaje del código de descuento debe estar entre 0 y 100.")

        except (InvalidOperation, ValueError):
            return render(request, 'cursos/course_form.html', {
                'error_message': 'Por favor, ingrese valores numéricos válidos para precio y descuentos.'
            })

        # Convertir duración a DurationField
        duration = None
        if duration_str:
            try:
                hours, minutes, seconds = map(int, duration_str.split(':'))
                duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                return render(request, 'cursos/course_form.html', {
                    'error_message': 'El formato de duración debe ser HH:MM:SS (ej. 02:30:00).'
                })

        # Crear el curso
        course = Course.objects.create(
            title=title,
            description=description,
            is_available=is_available,
            is_visible=is_visible,
            created_by=request.user,
            duration=duration,
            price=price,
            discount_basic=discount_basic,
            discount_intermediate=discount_intermediate,
            discount_premium=discount_premium,
            discount_code=discount_code,
            discount_code_percentage=discount_code_percentage,
            external_link=external_link
        )

        if 'document' in request.FILES:
            course.document = request.FILES['document']
            course.save()

        return redirect('dashboard')
    return render(request, 'cursos/course_form.html')
def nosotros(request):
    return render(request, 'nosotros.html')
def contacto(request):
    return render(request, 'contacto.html')