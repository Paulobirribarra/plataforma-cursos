#cursos/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Course, CourseResource, DiscountCode

class CourseForm(forms.ModelForm):
    duration_minutes = forms.IntegerField(
        min_value=0,
        required=False,
        help_text="Ingrese la duración en minutos (ejemplo: 120 para 2 horas)"
    )
    special_discount_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=15,
        required=False,
        label="Descuento Especial (%)",
        help_text="Este descuento se aplica automáticamente a usuarios con membresía activa que cumplan ciertos requisitos (e.g., completar cursos gratuitos)."
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'base_price', 'is_free',
            'is_available', 'is_visible', 'duration_minutes', 'tags',
            'special_discount_percentage'
        ]
        widgets = {
            'is_free': forms.CheckboxInput(),
            'is_available': forms.CheckboxInput(),
            'is_visible': forms.CheckboxInput(),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'tags': forms.SelectMultiple(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800'}),
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'category': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white text-gray-800'}),
            'base_price': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'step': '1', 'min': '0'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 0, 'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'step': '1'}),
            'special_discount_percentage': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        base_price = cleaned_data.get('base_price')
        special_discount_percentage = cleaned_data.get('special_discount_percentage')
        duration_minutes = cleaned_data.get('duration_minutes')

        # Si el curso es gratuito, forzamos base_price a 0
        if is_free:
            cleaned_data['base_price'] = 0
        else:
            # Si no es gratuito, base_price debe ser mayor a 0
            if base_price is None or base_price <= 0:
                raise forms.ValidationError("Un curso no gratuito debe tener un precio base mayor a 0.")

        # Asegurarnos de que special_discount_percentage no sea None
        if special_discount_percentage is None:
            cleaned_data['special_discount_percentage'] = 0.00

        # Asegurarnos de que duration_minutes no sea None
        if duration_minutes is None:
            cleaned_data['duration_minutes'] = 0

        return cleaned_data

class CourseResourceForm(forms.ModelForm):
    class Meta:
        model = CourseResource
        fields = ['title', 'file', 'url', 'type']
        widgets = {
            'type': forms.Select(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'url': forms.URLInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if not file and not url:
            raise ValidationError("Debe proporcionar un archivo o una URL.")
        if file and url:
            raise ValidationError("No puede proporcionar tanto un archivo como una URL.")

        return cleaned_data

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ['code', 'discount_percentage']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-gray-400 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500', 'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def clean_discount_percentage(self):
        discount_percentage = self.cleaned_data.get('discount_percentage')
        if discount_percentage is None:
            raise ValidationError("El porcentaje de descuento es obligatorio.")
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValidationError("El porcentaje de descuento debe estar entre 0 y 100.")
        return discount_percentage