from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return the given key from a dictionary."""
    return dictionary.get(key)
