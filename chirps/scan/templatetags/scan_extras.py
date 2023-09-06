from django import template

register = template.Library()


@register.filter
def format_conversation(text: str) -> list:
    """Format a conversation for display in the UI."""
    lines = text.split('\n')
    formatted_lines = []

    for line in lines:
        if line.startswith('chirps:'):
            formatted_lines.append({'type': 'chirps', 'text': line[7:]})
        elif line.startswith('asset:'):
            formatted_lines.append({'type': 'asset', 'text': line[6:]})
        else:
            formatted_lines.append({'type': 'normal', 'text': line})

    return formatted_lines
