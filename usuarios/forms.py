#plataforma-cursos\usuarios\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'phone', 'password1', 'password2')
    
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