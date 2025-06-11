#plataforma-cursos\usuarios\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # Campo para suscripción al newsletter
    suscrito_newsletter = forms.BooleanField(
        label="📧 Quiero recibir el newsletter",
        help_text="Recibe noticias, promociones y contenido exclusivo en tu email",
        required=False,
        initial=True,  # Marcado por defecto (opt-out)
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
            'id': 'newsletter-checkbox'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'phone', 'suscrito_newsletter', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar mensajes de ayuda para la contraseña
        self.fields['password1'].help_text = """
        La contraseña debe:
        • Tener al menos 8 caracteres
        • Contener al menos una letra mayúscula
        • Contener al menos una letra minúscula
        • Contener al menos un número
        • Contener al menos un carácter especial (!, @, #, etc.)
        """

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            try:
                from .models import validate_strong_password
                validate_strong_password(password)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password

class NewsletterPreferencesForm(forms.ModelForm):
    """Formulario para gestionar las preferencias de newsletter del usuario"""
    
    class Meta:
        model = CustomUser
        fields = ['suscrito_newsletter']
        widgets = {
            'suscrito_newsletter': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded',
                'id': 'newsletter-toggle'
            })
        }
        labels = {
            'suscrito_newsletter': '📧 Suscrito al Newsletter'
        }
        help_texts = {
            'suscrito_newsletter': 'Recibe actualizaciones, noticias y contenido exclusivo'
        }

class UserProfileForm(forms.ModelForm):
    """Formulario para editar el perfil completo del usuario"""
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone', 'suscrito_newsletter']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Nombre completo'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': '+56 9 XXXX XXXX'
            }),
            'suscrito_newsletter': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        }
        labels = {
            'full_name': 'Nombre Completo',
            'phone': 'Teléfono',
            'suscrito_newsletter': '📧 Newsletter'
        }
        help_texts = {
            'suscrito_newsletter': 'Recibe noticias y promociones por email'
        }