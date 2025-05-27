# cursos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, UserCourse, DiscountCode
from .forms import CourseForm, CourseResourceForm, DiscountCodeForm
from decimal import Decimal
from membresias.models import MembershipPlan

# --------------------------
# Funciones auxiliares
# --------------------------


def extract_youtube_id(url):
    if url:
        if "youtube.com" in url and "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
    return None


# --------------------------
# Vistas públicas
# --------------------------


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_available=True)
    user_course = UserCourse.objects.filter(user=request.user, course=course).first()

    final_price = Decimal("0.00") if course.is_free else course.base_price

    if not course.is_free:
        # Aplicar el mayor descuento disponible (solo código por ahora)
        max_discount = Decimal("0.00")

        # Descuento por código
        code = request.GET.get("discount_code")
        if code:
            try:
                discount_code = DiscountCode.objects.get(
                    course=course, code__iexact=code
                )
                max_discount = max(max_discount, discount_code.discount_percentage)
            except DiscountCode.DoesNotExist:
                messages.error(request, "El código de descuento no es válido.")

        if max_discount > 0:
            final_price *= 1 - max_discount / 100

    # Preprocesar recursos con sus youtube_ids
    resources_with_youtube = [
        (resource, extract_youtube_id(resource.url))
        for resource in course.resources.filter(type="video")
        if extract_youtube_id(resource.url)
    ]

    return render(
        request,
        "cursos/course_detail.html",
        {
            "course": course,
            "final_price": final_price,
            "resources_with_youtube": resources_with_youtube,
            "user_course": user_course,
        },
    )


def course_list(request):
    free_courses = Course.objects.filter(is_available=True, is_free=True)
    general_courses = Course.objects.filter(is_available=True, is_free=False)
    plans = MembershipPlan.objects.filter(is_active=True)
    return render(
        request,
        "cursos/courses_list.html",
        {
            "free_courses": free_courses,
            "general_courses": general_courses,
            "plans": plans,
        },
    )


# --------------------------
# Vistas de administración
# --------------------------


@staff_member_required
def course_list_admin(request):
    courses = Course.objects.all()
    return render(request, "cursos/course_list_admin.html", {"courses": courses})


@staff_member_required
def course_create_or_update(request, pk=None):
    course = get_object_or_404(Course, pk=pk) if pk else None
    form = CourseForm(request.POST or None, instance=course)
    resource_form = CourseResourceForm(request.POST or None, request.FILES or None)
    discount_form = DiscountCodeForm(request.POST or None)

    if request.method == "POST":
        if "save_course" in request.POST:
            if form.is_valid():
                course = form.save(commit=False)
                if not course.created_by and not pk:
                    course.created_by = request.user
                course.save()
                form.save_m2m()
                messages.success(
                    request, f"Curso {'actualizado' if pk else 'creado'} exitosamente."
                )
                return redirect("cursos:course_edit_admin", pk=course.pk)
            else:
                messages.error(
                    request, "Por favor, corrija los errores en el formulario."
                )
        elif "add_resource" in request.POST and course:
            if resource_form.is_valid():
                resource = resource_form.save(commit=False)
                resource.course = course
                resource.save()
                messages.success(request, "Recurso añadido exitosamente.")
                return redirect("cursos:course_edit_admin", pk=course.pk)
            else:
                messages.error(
                    request,
                    "Por favor, corrija los errores en el formulario de recursos.",
                )
        elif "add_discount" in request.POST and course:
            if discount_form.is_valid():
                discount = discount_form.save(commit=False)
                discount.course = course
                discount.save()
                messages.success(request, "Código de descuento añadido exitosamente.")
                return redirect("cursos:course_edit_admin", pk=course.pk)
            else:
                messages.error(
                    request,
                    "Por favor, corrija los errores en el formulario de descuento.",
                )

    return render(
        request,
        "cursos/course_form.html",
        {
            "form": form,
            "course": course,
            "resource_form": resource_form,
            "discount_form": discount_form,
        },
    )


@staff_member_required
def course_resource_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    form = CourseResourceForm()

    if request.method == "POST":
        form = CourseResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.course = course
            resource.save()
            messages.success(request, "Recurso creado exitosamente.")
            return redirect("cursos:course_list_admin")

    return render(
        request, "cursos/course_resource_form.html", {"form": form, "course": course}
    )


@staff_member_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Curso eliminado exitosamente.")
        return redirect("cursos:course_list_admin")
    return render(request, "cursos/course_confirm_delete.html", {"course": course})
