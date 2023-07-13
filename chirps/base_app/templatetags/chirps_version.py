"""Helper template tag to get the version of the chirps app."""
from pathlib import Path

from django import template

register = template.Library()

# Build the path to the VERSION file
version_path = Path(__file__).parent.resolve() / Path('../../../VERSION')


@register.simple_tag
def chirps_version():
    """Return the current version of the chirps application."""
    return open(version_path, encoding='utf-8').read().strip()
