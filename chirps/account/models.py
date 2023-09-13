"""Models for the account application."""
from django.contrib.auth.models import User
from django.db import models
from fernet_fields import EncryptedCharField


class Profile(models.Model):
    """Custom profile model for users."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    anthropic_api_key = EncryptedCharField(max_length=100, blank=True)
    cohere_key = EncryptedCharField(max_length=100, blank=True)
    openai_api_key = EncryptedCharField(max_length=100, blank=True)
    finding_preview_size = models.IntegerField(default=20, null=True)

    # Deprecating this field
    openai_key = EncryptedCharField(max_length=100, blank=True)

    def _get_masked_key(self, key: str) -> str:
        """Return the masked version of the key."""
        if not key:
            return 'Not Configured'
        return self._masked_key(key)

    @property
    def masked_anthropic_api_key(self):
        """Return the masked Anthropic API key."""
        return self._get_masked_key(self.anthropic_api_key)

    @property
    def masked_cohere_key(self):
        """Return the masked Cohere key."""
        return self._get_masked_key(self.cohere_key)

    @property
    def masked_openai_api_key(self):
        """Return the masked OpenAI key."""
        return self._get_masked_key(self.openai_api_key)

    @staticmethod
    def _masked_key(key: str) -> str:
        """Return the masked version of the key."""
        if key:
            masked_key = key[:6] + '*' * (len(key) - 6)
            return masked_key
        return None
