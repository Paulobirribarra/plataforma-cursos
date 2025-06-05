from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide el valor por el argumento"""
    try:
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def discount_calc(base_price, discount_percentage):
    """Calcula el descuento en base a un porcentaje"""
    try:
        return (Decimal(str(base_price)) * Decimal(str(discount_percentage))) / 100
    except (ValueError, TypeError):
        return 0


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
            return f"{int(number)}%"
        else:
            return f"{number:.2f}%"
    except (ValueError, TypeError):
        return "0%"
