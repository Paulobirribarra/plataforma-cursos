from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.views import View
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context, Template

from .models import Boletin, BoletinSuscriptor, PlantillaBoletin
from .forms import (
    BoletinForm, BoletinRapidoForm, PlantillaBoletinForm,
    BoletinDuplicarForm, BoletinEnviarForm, BoletinFiltroForm
)
from usuarios.models import CustomUser
from blogs.models import BlogPost

import json


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar que el usuario sea staff"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')


# =============================================================================
# VISTAS PÚBLICAS
# =============================================================================

class BoletinListView(ListView):
    """Vista para listar boletines públicos"""
    model = Boletin
    template_name = 'boletines/lista.html'
    context_object_name = 'boletines'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Boletin.objects.filter(
            estado='enviado',
            activo=True
        ).select_related('creado_por', 'blog_relacionado', 'curso_relacionado')
        
        # Filtros de búsqueda
        categoria = self.request.GET.get('categoria')
        if categoria and categoria in dict(Boletin.CATEGORIA_CHOICES):
            queryset = queryset.filter(categoria=categoria)
        
        buscar = self.request.GET.get('buscar')
        if buscar:
            queryset = queryset.filter(
                Q(titulo__icontains=buscar) |
                Q(resumen__icontains=buscar) |
                Q(contenido__icontains=buscar)
            )
        
        return queryset.order_by('-fecha_enviado')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Boletin.CATEGORIA_CHOICES
        context['categoria_seleccionada'] = self.request.GET.get('categoria', '')
        context['buscar'] = self.request.GET.get('buscar', '')
        return context


class BoletinDetailView(DetailView):
    """Vista para ver el detalle de un boletín"""
    model = Boletin
    template_name = 'boletines/detalle.html'
    context_object_name = 'boletin'
    
    def get_queryset(self):
        return Boletin.objects.filter(
            estado='enviado',
            activo=True
        ).select_related('creado_por', 'blog_relacionado', 'curso_relacionado')
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        
        # Registrar tracking si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                suscripcion = BoletinSuscriptor.objects.get(
                    boletin=self.object,
                    usuario=request.user
                )
                suscripcion.marcar_como_abierto()
            except BoletinSuscriptor.DoesNotExist:
                pass
        
        return response


class TrackingAbrirView(View):
    """Vista para tracking de apertura de emails"""
    
    def get(self, request, slug):
        try:
            boletin = get_object_or_404(Boletin, slug=slug)
            
            if request.user.is_authenticated:
                suscripcion, created = BoletinSuscriptor.objects.get_or_create(
                    boletin=boletin,
                    usuario=request.user
                )
                suscripcion.marcar_como_abierto()
            
            # Retornar imagen transparente de 1x1 pixel
            from django.http import HttpResponse
            import base64
            
            # GIF transparente de 1x1 pixel
            gif_data = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
            return HttpResponse(gif_data, content_type='image/gif')
            
        except Exception:
            return HttpResponse(status=404)


class TrackingClickView(View):
    """Vista para tracking de clicks en boletines"""
    
    def get(self, request, slug):
        try:
            boletin = get_object_or_404(Boletin, slug=slug)
            url = request.GET.get('url')
            
            if request.user.is_authenticated:
                suscripcion, created = BoletinSuscriptor.objects.get_or_create(
                    boletin=boletin,
                    usuario=request.user
                )
                suscripcion.registrar_click()
            
            if url:
                return redirect(url)
            else:
                return redirect('boletines:detalle', slug=slug)
                
        except Exception:
            return redirect('boletines:lista')


class SuscribirBoletinView(View):
    """Vista para manejar suscripciones al newsletter"""
    
    def post(self, request):
        """Manejar suscripción vía AJAX"""
        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Debes estar autenticado para suscribirte'
                })
            
            # Alternar estado de suscripción
            user = request.user
            user.suscrito_newsletter = not user.suscrito_newsletter
            user.save(update_fields=['suscrito_newsletter'])
            
            mensaje = 'Te has suscrito al newsletter' if user.suscrito_newsletter else 'Te has desuscrito del newsletter'
            
            return JsonResponse({
                'success': True,
                'suscrito': user.suscrito_newsletter,
                'mensaje': mensaje
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Error al procesar la suscripción'
            })
    
    def get(self, request):
        """Manejar suscripción vía GET (formulario tradicional)"""
        if not request.user.is_authenticated:
            messages.error(request, 'Debes estar autenticado para suscribirte')
            return redirect('account_login')
        
        user = request.user
        user.suscrito_newsletter = not user.suscrito_newsletter
        user.save(update_fields=['suscrito_newsletter'])
        
        if user.suscrito_newsletter:
            messages.success(request, 'Te has suscrito al newsletter exitosamente')
        else:
            messages.info(request, 'Te has desuscrito del newsletter')
        
        return redirect('usuarios:dashboard')
        try:
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para suscribirte al newsletter')
                return redirect('account_login')
            
            # Alternar estado de suscripción
            user = request.user
            user.suscrito_newsletter = not user.suscrito_newsletter
            user.save(update_fields=['suscrito_newsletter'])
            
            if user.suscrito_newsletter:
                messages.success(request, '¡Te has suscrito exitosamente al newsletter!')
            else:
                messages.info(request, 'Te has desuscrito del newsletter')
            
            # Redirigir a la página anterior o a la lista de boletines
            next_url = request.GET.get('next', reverse('boletines:lista'))
            return redirect(next_url)
            
        except Exception as e:
            messages.error(request, 'Error al procesar la suscripción. Inténtalo de nuevo.')
            return redirect('boletines:lista')


# =============================================================================
# VISTAS DE ADMINISTRACIÓN
# =============================================================================

@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(TemplateView):
    """Dashboard principal de administración de boletines"""
    template_name = 'boletines/admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['boletines_total'] = Boletin.objects.count()
        context['boletines_enviados'] = Boletin.objects.filter(estado='enviado').count()
        context['boletines_borrador'] = Boletin.objects.filter(estado='borrador').count()
        context['boletines_programados'] = Boletin.objects.filter(estado='programado').count()
        
        # Filtros
        form = BoletinFiltroForm(self.request.GET)
        context['filtro_form'] = form
        
        # Queryset filtrado
        queryset = Boletin.objects.select_related('creado_por', 'blog_relacionado', 'curso_relacionado')
        
        if form.is_valid():
            if form.cleaned_data['categoria']:
                queryset = queryset.filter(categoria=form.cleaned_data['categoria'])
            if form.cleaned_data['estado']:
                queryset = queryset.filter(estado=form.cleaned_data['estado'])
            if form.cleaned_data['fecha_desde']:
                queryset = queryset.filter(fecha_creacion__gte=form.cleaned_data['fecha_desde'])
            if form.cleaned_data['fecha_hasta']:
                queryset = queryset.filter(fecha_creacion__lte=form.cleaned_data['fecha_hasta'])
            if form.cleaned_data['buscar']:
                buscar = form.cleaned_data['buscar']
                queryset = queryset.filter(
                    Q(titulo__icontains=buscar) |
                    Q(resumen__icontains=buscar) |
                    Q(contenido__icontains=buscar)
                )
        
        # Paginación
        paginator = Paginator(queryset.order_by('-fecha_creacion'), 15)
        page = self.request.GET.get('page')
        context['boletines'] = paginator.get_page(page)
        
        # Boletines recientes
        context['boletines_recientes'] = Boletin.objects.order_by('-fecha_creacion')[:5]
        
        # Estadísticas por categoría
        context['stats_categoria'] = (
            Boletin.objects.values('categoria')
            .annotate(total=Count('id'))
            .order_by('categoria')
        )
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminCrearView(CreateView):
    """Vista para crear nuevos boletines"""
    model = Boletin
    form_class = BoletinForm
    template_name = 'boletines/admin/crear.html'
    success_url = reverse_lazy('boletines:admin_dashboard')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, f'Boletín "{form.instance.titulo}" creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plantillas'] = PlantillaBoletin.objects.filter(activa=True)
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminEditarView(UpdateView):
    """Vista para editar boletines existentes"""
    model = Boletin
    form_class = BoletinForm
    template_name = 'boletines/admin/editar.html'
    
    def get_success_url(self):
        return reverse('boletines:admin_dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Boletín "{form.instance.titulo}" actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plantillas'] = PlantillaBoletin.objects.filter(activa=True)
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminEliminarView(DeleteView):
    """Vista para eliminar boletines"""
    model = Boletin
    template_name = 'boletines/admin/eliminar.html'
    success_url = reverse_lazy('boletines:admin_dashboard')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # No permitir eliminar boletines ya enviados
        if self.object.estado == 'enviado':
            messages.error(request, 'No se pueden eliminar boletines ya enviados')
            return redirect('boletines:admin_dashboard')
        
        titulo = self.object.titulo
        messages.success(request, f'Boletín "{titulo}" eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class AdminEnviarView(TemplateView):
    """Vista para enviar boletines"""
    template_name = 'boletines/admin/enviar.html'
    
    def get_object(self):
        return get_object_or_404(Boletin, slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boletin'] = self.get_object()
        context['form'] = BoletinEnviarForm()
        context['destinatarios_count'] = context['boletin'].get_destinatarios_count()
        return context
    def post(self, request, *args, **kwargs):
        boletin = self.get_object()
        form = BoletinEnviarForm(request.POST)
        
        if form.is_valid():
            tipo_envio = form.cleaned_data['tipo_envio']
            
            if tipo_envio == 'prueba':
                # Envío de prueba
                self._enviar_prueba(boletin, form.cleaned_data['email_prueba'])
                messages.success(request, f'Boletín de prueba enviado a {form.cleaned_data["email_prueba"]}')
                
            elif tipo_envio == 'inmediato':
                # Envío inmediato
                resultado = self._enviar_boletin(boletin)
                if resultado['exito']:
                    messages.success(request, f'Boletín enviado a {resultado["enviados"]} destinatarios')
                else:
                    messages.error(request, f'Error al enviar: {resultado["error"]}')
                    
            elif tipo_envio == 'programado':
                # Programar envío
                boletin.fecha_programada = form.cleaned_data['fecha_programada']
                boletin.estado = 'programado'
                boletin.save()
                messages.success(request, f'Boletín programado para {boletin.fecha_programada}')
            
            return redirect('boletines:admin_dashboard')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
    
    def _enviar_prueba(self, boletin, email):
        """Enviar email de prueba"""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            
            # Renderizar contenido
            context = {
                'boletin': boletin,
                'usuario': self.request.user,
                'es_prueba': True
            }
            
            html_content = render_to_string('boletines/email/boletin.html', context)
            text_content = render_to_string('boletines/email/boletin.txt', context)
            
            # Crear email
            subject = f"[PRUEBA] {boletin.titulo}"
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return True
            
        except Exception as e:
            messages.error(self.request, f'Error al enviar prueba: {str(e)}')
            return False

    def _enviar_boletin(self, boletin):
        """Enviar boletín a todos los destinatarios"""
        try:
            # Obtener destinatarios
            if boletin.solo_suscriptores_premium:
                usuarios = CustomUser.objects.filter(
                    suscrito_newsletter=True,
                    membresia__isnull=False,
                    membresia__activa=True
                )
            else:
                usuarios = CustomUser.objects.filter(suscrito_newsletter=True)
            
            enviados = 0
            errores = 0
            for usuario in usuarios:
                try:
                    # Crear o actualizar suscripción
                    suscripcion, created = BoletinSuscriptor.objects.get_or_create(
                        boletin=boletin,
                        usuario=usuario
                    )
                    
                    if not suscripcion.enviado:
                        if self._enviar_email_individual(boletin, usuario):
                            suscripcion.enviado = True
                            suscripcion.fecha_enviado = timezone.now()
                            suscripcion.save()
                            enviados += 1
                        else:
                            errores += 1
                            
                except Exception as e:
                    errores += 1
                    continue
            
            # Actualizar estado del boletín
            boletin.estado = 'enviado'
            boletin.fecha_enviado = timezone.now()
            boletin.total_enviados = enviados
            boletin.save()
            
            return {
                'exito': True,
                'enviados': enviados,
                'errores': errores
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def _enviar_email_individual(self, boletin, usuario):
        """Enviar email individual"""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            
            context = {
                'boletin': boletin,
                'usuario': usuario,
                'tracking_url': self.request.build_absolute_uri(
                    reverse('boletines:tracking_abrir', kwargs={'slug': boletin.slug})
                )
            }
            
            html_content = render_to_string('boletines/email/boletin.html', context)
            text_content = render_to_string('boletines/email/boletin.txt', context)
            msg = EmailMultiAlternatives(
                subject=boletin.titulo,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            return True
            
        except Exception:
            return False


@method_decorator(staff_member_required, name='dispatch')
class AdminPreviewView(DetailView):
    """Vista para previsualizar boletines"""
    model = Boletin
    template_name = 'boletines/admin/preview.html'
    context_object_name = 'boletin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminDuplicarView(TemplateView):
    """Vista para duplicar boletines"""
    template_name = 'boletines/admin/duplicar.html'
    
    def get_object(self):
        return get_object_or_404(Boletin, slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['boletin'] = self.get_object()
        context['form'] = BoletinDuplicarForm(initial={
            'nuevo_titulo': f"Copia de {context['boletin'].titulo}"
        })
        return context
    
    def post(self, request, *args, **kwargs):
        boletin_original = self.get_object()
        form = BoletinDuplicarForm(request.POST)
        
        if form.is_valid():
            # Crear copia
            nuevo_boletin = Boletin.objects.create(
                titulo=form.cleaned_data['nuevo_titulo'],
                resumen=boletin_original.resumen,
                contenido=boletin_original.contenido,
                categoria=boletin_original.categoria,
                prioridad=boletin_original.prioridad,
                curso_relacionado=boletin_original.curso_relacionado,
                solo_suscriptores_premium=boletin_original.solo_suscriptores_premium,
                creado_por=request.user,
                estado='borrador'
            )
            
            if form.cleaned_data['mantener_programacion'] and boletin_original.fecha_programada:
                nuevo_boletin.fecha_programada = boletin_original.fecha_programada
                nuevo_boletin.estado = 'programado'
                nuevo_boletin.save()
            
            messages.success(request, f'Boletín duplicado como "{nuevo_boletin.titulo}"')
            return redirect('boletines:admin_editar', slug=nuevo_boletin.slug)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


@method_decorator(staff_member_required, name='dispatch')
class AdminEstadisticasView(DetailView):
    """Vista para ver estadísticas de un boletín"""
    model = Boletin
    template_name = 'boletines/admin/estadisticas.html'
    context_object_name = 'boletin'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        boletin = self.object
        
        # Estadísticas básicas
        context['total_enviados'] = boletin.total_enviados
        context['total_abiertos'] = boletin.total_abiertos
        context['total_clicks'] = boletin.total_clicks
        
        # Tasas de apertura y clicks
        if boletin.total_enviados > 0:
            context['tasa_apertura'] = (boletin.total_abiertos / boletin.total_enviados) * 100
            context['tasa_clicks'] = (boletin.total_clicks / boletin.total_enviados) * 100
        else:
            context['tasa_apertura'] = 0
            context['tasa_clicks'] = 0
        
        # Suscripciones detalladas
        context['suscripciones'] = (
            BoletinSuscriptor.objects.filter(boletin=boletin)
            .select_related('usuario')
            .order_by('-fecha_enviado')
        )
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminPlantillasView(TemplateView):
    """Vista para gestionar plantillas de boletines"""
    template_name = 'boletines/admin/plantillas.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plantillas'] = PlantillaBoletin.objects.filter(activa=True)
        return context


class AdminCrearPlantillaView(CreateView):
    """Vista para crear nueva plantilla"""
    model = PlantillaBoletin
    form_class = PlantillaBoletinForm
    template_name = 'boletines/admin/crear_plantilla.html'
    success_url = reverse_lazy('boletines:admin_plantillas')
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        form.instance.creada_por = self.request.user
        messages.success(self.request, 'Plantilla creada exitosamente.')
        return super().form_valid(form)


class AdminEditarPlantillaView(UpdateView):
    """Vista para editar plantilla"""
    model = PlantillaBoletin
    form_class = PlantillaBoletinForm
    template_name = 'boletines/admin/editar_plantilla.html'
    success_url = reverse_lazy('boletines:admin_plantillas')
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Plantilla actualizada exitosamente.')
        return super().form_valid(form)


class AdminEliminarPlantillaView(DeleteView):
    """Vista para eliminar plantilla"""
    model = PlantillaBoletin
    template_name = 'boletines/admin/eliminar_plantilla.html'
    success_url = reverse_lazy('boletines:admin_plantillas')
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Plantilla eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


class APIPreviewTemplateView(View):
    """API para preview de plantillas"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            template_html = request.POST.get('template_html', '')
            css_styles = request.POST.get('css_styles', '')
            
            # Datos de ejemplo para el preview
            context = {
                'titulo': 'Título de Ejemplo',
                'contenido': 'Este es un contenido de ejemplo para el boletín.',
                'fecha': timezone.now(),
                'usuario': {
                    'first_name': 'Usuario',
                    'last_name': 'Ejemplo'
                }
            }
            
            # Renderizar template
            template = Template(template_html)
            html_content = template.render(Context(context))
            
            # Agregar CSS
            if css_styles:
                html_content = f'<style>{css_styles}</style>' + html_content
            
            return JsonResponse({
                'success': True,
                'html': html_content
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class APIDestinatariosCountView(View):
    """API para contar destinatarios según filtros"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        try:
            solo_premium = request.GET.get('solo_premium', 'false').lower() == 'true'
            
            if solo_premium:
                count = CustomUser.objects.filter(
                    suscrito_newsletter=True,
                    membresia__isnull=False,
                    membresia__activa=True
                ).distinct().count()
            else:
                count = CustomUser.objects.filter(suscrito_newsletter=True).count()
            
            return JsonResponse({
                'success': True,
                'count': count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
