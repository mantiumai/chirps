"""Models for the target appliation."""
from logging import getLogger

from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static
from polymorphic.models import PolymorphicModel

logger = getLogger(__name__)


class BaseTarget(PolymorphicModel):
    """Base class that all targets will inherit from."""

    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    html_logo = None

    def search(self, query: str, max_results: int) -> list[str]:
        """Perform a query against the specified target, returning the max_results number of matches."""

    def test_connection(self) -> bool:
        """Verify that the target can be connected to."""

    def logo_url(self) -> str:
        """Fetch the logo URL for the target."""
        return static(self.html_logo)

    def __str__(self) -> str:
        """String representation of this model."""
        return str(self.name)
