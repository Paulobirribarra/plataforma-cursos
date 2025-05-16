from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Course
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
import datetime
from django.shortcuts import render

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_available=True)
    final_price = course.price or Decimal('0.00')

    user_subscription = request.user.subscription_level
    if user_subscription == 'basic' and course.discount_basic:
        final_price *= (1 - course.discount_basic / 100)
    elif user_subscription == 'intermediate' and course.discount_intermediate:
        final_price *= (1 - course.discount_intermediate / 100)
    elif user_subscription == 'premium' and course.discount_premium:
        final_price *= (1 - course.discount_premium / 100)

    discount_code = request.GET.get('discount_code', '')
    if discount_code == course.discount_code and course.discount_code_percentage:
        final_price *= (1 - course.discount_code_percentage / 100)

    youtube_id = None
    if course.external_link and 'youtube.com' in course.external_link:
        video_url = course.external_link
        if 'v=' in video_url:
            youtube_id = video_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in video_url:
            youtube_id = video_url.split('youtu.be/')[1].split('?')[0]

    return render(request, 'cursos/course_detail.html', {
        'course': course,
        'final_price': final_price,
        'youtube_id': youtube_id
    })

def course_list(request):
    courses = Course.objects.filter(is_visible=True)
    return render(request, 'home.html', {'courses': courses})

@staff_member_required
def course_create(request):
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

        return redirect('course_list_admin')
    return render(request, 'cursos/course_form.html')

@staff_member_required
def course_list_admin(request):
    courses = Course.objects.all()
    return render(request, 'cursos/course_list_admin.html', {'courses': courses})

@staff_member_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.is_available = request.POST.get('is_available') == 'on'
        course.is_visible = request.POST.get('is_visible') == 'on'
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
            price = Decimal(str(price).replace(',', '.')) if price else course.price
            discount_basic = Decimal(str(discount_basic).replace(',', '.').strip()) if discount_basic else course.discount_basic
            discount_intermediate = Decimal(str(discount_intermediate).replace(',', '.').strip()) if discount_intermediate else course.discount_intermediate
            discount_premium = Decimal(str(discount_premium).replace(',', '.').strip()) if discount_premium else course.discount_premium
            discount_code_percentage = Decimal(str(discount_code_percentage).replace(',', '.').strip()) if discount_code_percentage else course.discount_code_percentage

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
                'course': course,
                'error_message': 'Por favor, ingrese valores numéricos válidos para precio y descuentos.'
            })

        # Convertir duración a DurationField
        if duration_str:
            try:
                hours, minutes, seconds = map(int, duration_str.split(':'))
                course.duration = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                return render(request, 'cursos/course_form.html', {
                    'course': course,
                    'error_message': 'El formato de duración debe ser HH:MM:SS (ej. 02:30:00).'
                })

        course.price = price
        course.discount_basic = discount_basic
        course.discount_intermediate = discount_intermediate
        course.discount_premium = discount_premium
        course.discount_code = discount_code
        course.discount_code_percentage = discount_code_percentage
        course.external_link = external_link

        if 'document' in request.FILES:
            course.document = request.FILES['document']

        course.save()
        return redirect('course_list_admin')
    return render(request, 'cursos/course_form.html', {'course': course})

@staff_member_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list_admin')
    return render(request, 'cursos/course_confirm_delete.html', {'course': course})


def nosotros(request):
    return render(request, 'nosotros.html')
def contacto(request):
    return render(request, 'contacto.html')