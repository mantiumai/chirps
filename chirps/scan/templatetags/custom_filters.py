from django import template

register = template.Library()


@register.filter
def with_args(method, *args):
    """Filter request"""
    return method(*args)
