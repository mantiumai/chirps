"""Template tags for the policy app."""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary: dict, key: str) -> str | None:
    """Return the given key from a dictionary."""
    return dictionary.get(key)
