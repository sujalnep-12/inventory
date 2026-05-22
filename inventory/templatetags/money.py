from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def money(value):
    if value in (None, ''):
        return '0'

    try:
        amount = Decimal(str(value)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return value

    text = format(amount, 'f')
    return text.rstrip('0').rstrip('.') if '.' in text else text
