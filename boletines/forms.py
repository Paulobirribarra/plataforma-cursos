from django import forms
from django.utils import timezone
from .models import Boletin, PlantillaBoletin
from blogs.models import BlogPost
from cursos.models import Course


class BoletinForm(forms.ModelForm):
    """Formulario principal para crear/editar boletines"""
    
    class Meta:
        model = Boletin
        fields = [
            'titulo', 'resumen', 'contenido', 'categoria', 'prioridad',
            'imagen_destacada', 'blog_relacionado', 'curso_relacionado',
            'fecha_programada', 'solo_suscriptores_premium'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del boletín'
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Resumen corto que aparecerá en el preview del email'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control editor-content',
                'rows': 12,
                'placeholder': 'Contenido principal del boletín'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen_destacada': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'blog_relacionado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'curso_relacionado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'solo_suscriptores_premium': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'titulo': 'Título',
            'resumen': 'Resumen',
            'contenido': 'Contenido',
            'categoria': 'Categoría',
            'prioridad': 'Prioridad',
            'imagen_destacada': 'Imagen destacada',
            'blog_relacionado': 'Blog relacionado',
            'curso_relacionado': 'Curso relacionado',
            'fecha_programada': 'Programar envío',
            'solo_suscriptores_premium': 'Solo suscriptores premium'
        }
        help_texts = {
            'titulo': 'Máximo 200 caracteres',
            'resumen': 'Máximo 300 caracteres. Aparecerá en el preview del email',
            'contenido': 'Puedes usar HTML básico para formato',
            'fecha_programada': 'Deja vacío para envío manual',
            'solo_suscriptores_premium': 'Enviar solo a usuarios con membresía activa'
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
          # Filtrar blogs publicados
        self.fields['blog_relacionado'].queryset = BlogPost.objects.filter(
            activo=True
        ).order_by('-fecha_publicacion')
        self.fields['blog_relacionado'].empty_label = "Sin blog relacionado"        # Filtrar cursos activos
        self.fields['curso_relacionado'].queryset = Course.objects.filter(
            is_available=True
        ).order_by('-created_at')
        self.fields['curso_relacionado'].empty_label = "Sin curso relacionado"
    
    def clean_fecha_programada(self):
        fecha = self.cleaned_data.get('fecha_programada')
        if fecha and fecha <= timezone.now():
            raise forms.ValidationError(
                'La fecha programada debe ser futura'
            )
        return fecha
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo and len(titulo.strip()) < 5:
            raise forms.ValidationError(
                'El título debe tener al menos 5 caracteres'
            )
        return titulo.strip() if titulo else titulo
    
    def clean_resumen(self):
        resumen = self.cleaned_data.get('resumen')
        if resumen and len(resumen.strip()) < 20:
            raise forms.ValidationError(
                'El resumen debe tener al menos 20 caracteres'
            )
        return resumen.strip() if resumen else resumen


class BoletinRapidoForm(forms.ModelForm):
    """Formulario simplificado para crear boletines rápidos"""
    
    class Meta:
        model = Boletin
        fields = ['titulo', 'resumen', 'contenido', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del boletín'
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Resumen corto'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Contenido del boletín'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class PlantillaBoletinForm(forms.ModelForm):
    """Formulario para crear/editar plantillas de boletines"""
    
    class Meta:
        model = PlantillaBoletin
        fields = [
            'nombre', 'categoria', 'descripcion',
            'html_template', 'css_styles', 'por_defecto'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'html_template': forms.Textarea(attrs={
                'class': 'form-control code-editor',
                'rows': 15
            }),
            'css_styles': forms.Textarea(attrs={
                'class': 'form-control code-editor',
                'rows': 10
            }),
            'por_defecto': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'nombre': 'Nombre de la plantilla',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'html_template': 'Plantilla HTML',
            'css_styles': 'Estilos CSS',
            'por_defecto': 'Plantilla por defecto'
        }
        help_texts = {
            'html_template': 'Usa variables como {{titulo}}, {{contenido}}, {{resumen}}',
            'css_styles': 'CSS específico para esta plantilla',
            'por_defecto': 'Usar por defecto para esta categoría'
        }


class BoletinDuplicarForm(forms.Form):
    """Formulario para duplicar un boletín"""
    
    nuevo_titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título para el nuevo boletín'
        }),
        label='Nuevo título'
    )
    
    mantener_programacion = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Mantener fecha programada',
        help_text='Si no se marca, el nuevo boletín quedará como borrador'
    )


class BoletinEnviarForm(forms.Form):
    """Formulario para enviar boletines"""
    
    ENVIO_CHOICES = [
        ('inmediato', 'Enviar inmediatamente'),
        ('programado', 'Programar envío'),
        ('prueba', 'Envío de prueba'),
    ]
    
    tipo_envio = forms.ChoiceField(
        choices=ENVIO_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        initial='inmediato'
    )
    
    fecha_programada = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        label='Fecha y hora programada'
    )
    
    email_prueba = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        label='Email para prueba'
    )
    
    confirmar_envio = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Confirmo que quiero enviar este boletín'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_envio = cleaned_data.get('tipo_envio')
        fecha_programada = cleaned_data.get('fecha_programada')
        email_prueba = cleaned_data.get('email_prueba')
        
        if tipo_envio == 'programado' and not fecha_programada:
            raise forms.ValidationError(
                'Debes especificar una fecha para el envío programado'
            )
        
        if tipo_envio == 'prueba' and not email_prueba:
            raise forms.ValidationError(
                'Debes especificar un email para el envío de prueba'
            )
        
        if fecha_programada and fecha_programada <= timezone.now():
            raise forms.ValidationError(
                'La fecha programada debe ser futura'
            )
        
        return cleaned_data


class BoletinFiltroForm(forms.Form):
    """Formulario para filtrar boletines en el dashboard"""
    
    categoria = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Boletin.CATEGORIA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Boletin.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título o contenido...'
        })
    )
