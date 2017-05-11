
from django.template import Library

register = Library()


@register.filter
def is_false(arg):
    return arg is False

