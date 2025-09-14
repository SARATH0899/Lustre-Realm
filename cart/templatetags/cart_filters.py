from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return ''

@register.filter(name='floatformat')
def floatformat_filter(value, arg):
    """
    Custom floatformat filter that handles None and empty values
    """
    if value is None or value == '':
        return '0.00'
    try:
        return f"{float(value):.{int(arg)}f}"
    except (ValueError, TypeError):
        return value
