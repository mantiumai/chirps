"""Custom template tags for the scan app."""
from django import template

register = template.Library()


@register.filter
def format_conversation(text: str) -> list:
    """Format a conversation for display in the UI."""
    lines = text.split('\n')
    formatted_lines = []

    chirps_prefix = 'chirps:'
    asset_prefix = 'asset:'

    for line in lines:
        if line.startswith(chirps_prefix):
            formatted_lines.append({'type': 'chirps', 'text': line[len(chirps_prefix) :]})
        elif line.startswith(asset_prefix):
            formatted_lines.append({'type': 'asset', 'text': line[len(asset_prefix) :]})
        else:
            formatted_lines.append({'type': 'normal', 'text': line})

    return formatted_lines
