from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def format_clp(value):
    """Formatea números con puntos como separador de miles (formato chileno)"""
    try:
        # Convertir a entero para eliminar decimales
        number = int(float(value))
        # Formatear con puntos como separador de miles
        return f"{number:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


@register.filter
def format_percentage(value):
    """Formatea porcentajes eliminando decimales innecesarios"""
    try:
        number = float(value)
        if number == int(number):
            return f"{int(number)}"
        else:
            return f"{number:.1f}"
    except (ValueError, TypeError):
        return "0"


@register.filter
def add_class(field, css_class):
    """Agrega una clase CSS a un campo de formulario"""
    try:
        return field.as_widget(attrs={'class': css_class})
    except AttributeError:
        return field
