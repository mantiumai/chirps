from django import template

register = template.Library()


@register.filter
def surrounding_text_with_preview_size(finding, preview_size):
    """
    Call the surrounding_text method of a finding with the specified preview size.

    Usage:
        {{ finding|surrounding_text_with_preview_size:preview_size }}

    Args:
        finding (Finding): The Finding instance to call surrounding_text method on.
        preview_size (int): The preview size to be passed to the surrounding_text method.

    Returns:
        The result of calling the surrounding_text method with the provided preview size.
    """
    return finding.surrounding_text(preview_size)
