"""Models for the account application."""
from django.contrib.auth.models import User
from django.db import models
from fernet_fields import EncryptedCharField


class Profile(models.Model):
    """Custom profile model for users."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_key = EncryptedCharField(max_length=100, blank=True)
    cohere_key = EncryptedCharField(max_length=100, blank=True)
    finding_preview_size = models.IntegerField(default=20)

    @property
    def masked_openai_key(self):
        """Return the masked OpenAI key."""
        return self._masked_key(self.openai_key)

    @property
    def masked_cohere_key(self):
        """Return the masked Cohere key."""
        return self._masked_key(self.cohere_key)

    @staticmethod
    def _masked_key(key: str) -> str:
        """Return the masked version of the key."""
        if key:
            masked_key = key[:6] + '*' * (len(key) - 6)
            return masked_key
        return None
