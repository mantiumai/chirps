"""Models for the asset application."""
from dataclasses import dataclass
from logging import getLogger
from typing import Any

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from polymorphic.models import PolymorphicModel

logger = getLogger(__name__)


@dataclass
class SearchResult:
    """Dataclass for a search result."""

    data: str
    source_id: Any | None = None


@dataclass
class PingResult:
    """Dataclass for a ping result."""

    success: bool
    error: str | None = None


class BaseAsset(PolymorphicModel):
    """Base class that all assets will inherit from."""

    name = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    html_logo = None
    REQUIRES_EMBEDDINGS = False
    HAS_PING = False

    def scan_is_active(self) -> bool:
        """Return True if the asset is currently being scanned."""
        return self.scan_run_assets.filter(
            ~Q(scan__status='Complete') & ~Q(scan__status='Failed') & ~Q(scan__status='Canceled')
        ).exists()

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Perform a query against the specified asset, returning the max_results number of matches."""

    def test_connection(self) -> PingResult:
        """Verify that the asset can be connected to."""

    def logo_url(self) -> str:
        """Fetch the logo URL for the asset."""
        return static(self.html_logo)

    def __str__(self) -> str:
        """Stringify the model's name."""
        return str(self.name)
