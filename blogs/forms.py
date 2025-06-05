# blogs/forms.py
from django import forms
from django.core.validators import RegexValidator
from django.utils.html import strip_tags
import re
from .models import ContactMessage, BlogPost

class ContactForm(forms.ModelForm):
    """Formulario de contacto con validaciones robustas"""
    
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
            'placeholder': 'Tu nombre completo'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZÀ-ÿ\u00f1\u00d1\s]+$',
                message='El nombre solo puede contener letras y espacios.'
            )
        ]
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
            'placeholder': 'tu@email.com'
        })
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
            'placeholder': '+56 9 1234 5678'
        }),
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-\(\)]{7,20}$',
                message='Formato válido: +56912345678 o +56 9 1234 5678'
            )
        ]
    )
    asunto = forms.ChoiceField(
        choices=[
            ('', 'Selecciona un asunto'),
            ('Información sobre cursos', 'Información sobre cursos'),
            ('Consulta sobre membresías', 'Consulta sobre membresías'),
            ('Soporte técnico', 'Soporte técnico'),
            ('Asesoría personalizada', 'Asesoría personalizada'),
            ('Alianzas comerciales', 'Alianzas comerciales'),
            ('Otro', 'Otro'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300'
        })
    )
    
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
            'placeholder': 'Escribe tu mensaje aquí...',
            'rows': 5
        }),
        max_length=2000
    )

    class Meta:
        model = ContactMessage
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Remover HTML tags por seguridad
            nombre = strip_tags(nombre).strip()
            
            # Validar longitud mínima
            if len(nombre) < 2:
                raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
            
            # Validar que no sean solo números
            if nombre.isdigit():
                raise forms.ValidationError('El nombre no puede ser solo números.')
                
            return nombre
        return nombre

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Normalizar email
            email = email.lower().strip()
            
            # Validación adicional de formato
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise forms.ValidationError('Por favor ingresa un email válido.')
                
            return email
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Remover espacios y caracteres especiales
            telefono_clean = re.sub(r'[^\d\+]', '', telefono)
            
            # Validar longitud
            if len(telefono_clean) < 7:
                raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')
            
            return telefono
        return telefono

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto')
        if asunto:
            # Remover HTML tags
            asunto = strip_tags(asunto).strip()
            
            # Validar longitud mínima
            if len(asunto) < 5:
                raise forms.ValidationError('El asunto debe tener al menos 5 caracteres.')
                
            return asunto
        return asunto

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje')
        if mensaje:
            # Remover HTML tags
            mensaje = strip_tags(mensaje).strip()
            
            # Validar longitud mínima
            if len(mensaje) < 10:
                raise forms.ValidationError('El mensaje debe tener al menos 10 caracteres.')
            
            # Detectar posibles intentos de inyección
            suspicious_patterns = [
                r'<script',
                r'javascript:',
                r'on\w+\s*=',
                r'eval\(',
                r'document\.',
                r'window\.',
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, mensaje, re.IGNORECASE):
                    raise forms.ValidationError('El mensaje contiene contenido no permitido.')
                    
            return mensaje
        return mensaje


class BlogPostForm(forms.ModelForm):
    """
    Formulario para crear y editar publicaciones del blog desde el frontend.
    Incluye validaciones y campos personalizados para usuarios administradores.
    """
    
    # Campo oculto para el autor (se llenará automáticamente)
    autor = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    # Campo para elegir si el post es destacado
    destacado = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox h-5 w-5 text-blue-600 transition duration-150 ease-in-out',
        }),
        label='Destacar publicación en página principal',
        help_text='Marcar para mostrar esta publicación en la sección destacada'
    )
    
    # Editor de texto enriquecido para el contenido
    contenido = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
            'rows': 15,
            'id': 'id_contenido_editor',
        }),
        label='Contenido',
        help_text='Usa el editor para dar formato a tu publicación'
    )
    
    class Meta:
        model = BlogPost
        fields = ['titulo', 'categoria', 'resumen', 'imagen_destacada', 
                 'contenido', 'meta_description', 'activo', 'destacado']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
                'placeholder': 'Título de la publicación'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300'
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
                'rows': 3,
                'placeholder': 'Breve resumen de la publicación (opcional)'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300',
                'placeholder': 'Descripción para SEO (máx. 160 caracteres)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600 transition duration-150 ease-in-out'
            }),
        }
    
    def clean_contenido(self):
        """Validar que el contenido no tenga scripts maliciosos"""
        contenido = self.cleaned_data['contenido']
        
        # Lista de patrones sospechosos
        suspicious_patterns = [
            r'<\s*script',  # Etiquetas script
            r'javascript\s*:',  # Javascript en URLs
            r'on\w+\s*=',  # Eventos inline (onclick, onload, etc)
            r'eval\s*\(',  # Funciones eval
            r'document\.cookie',  # Acceso a cookies
            r'localStorage',  # Acceso a localStorage
            r'sessionStorage',  # Acceso a sessionStorage
            r'window\.location',  # Redirecciones
        ]
        
        # Verificar patrones sospechosos
        for pattern in suspicious_patterns:
            if re.search(pattern, contenido, re.IGNORECASE):
                raise forms.ValidationError('El contenido contiene código potencialmente malicioso.')
                
        return contenido
    
    def clean_meta_description(self):
        """Limitar la meta description a 160 caracteres"""
        meta = self.cleaned_data.get('meta_description', '')
        if meta and len(meta) > 160:
            return meta[:157] + '...'
        return meta
    
    def clean_imagen_destacada(self):
        """Validación adicional para imágenes"""
        imagen = self.cleaned_data.get('imagen_destacada')
        if imagen and hasattr(imagen, 'size'):
            # La validación de tamaño y extensión ya está en el modelo,
            # pero podemos agregar más validaciones específicas si es necesario.
            pass
        return imagen
