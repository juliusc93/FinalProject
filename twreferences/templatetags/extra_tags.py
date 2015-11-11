from django import template
from django.template.defaultfilters import urlize

register = template.Library()


@register.filter(needs_autoescape=True)
def urlize_list(array, autoescape=True):
    return [urlize(elem, autoescape=autoescape).encode("utf-8") for elem in array]
