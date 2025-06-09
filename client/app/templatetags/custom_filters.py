from django import template
import locale

register = template.Library()

@register.filter
def currency_format(value):
    """Format number as currency"""
    try:
        locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    try:
        return locale.currency(value, grouping=True)
    except:
        return value

@register.filter
def split_and_upper(value):
    """Split string by comma and convert to uppercase"""
    if value:
        return [tag.strip().upper() for tag in value.split(',')]
    return []

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_dots(value):
    """Add dots as thousand separators"""
    try:
        # Convert to int first to remove decimal places
        num = int(float(value))
        # Format with dots as thousand separators
        return "{:,}".format(num).replace(',', '.')
    except (ValueError, TypeError):
        return value