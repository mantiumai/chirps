"""Models for the account appliation."""
from django.contrib.auth.models import User
from django.db import models
from fernet_fields import EncryptedCharField


class Profile(models.Model):
    """Custom profile model for users."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openai_key = EncryptedCharField(max_length=100, blank=True)

    @property
    def masked_openai_key(self):
        """Return the masked OpenAI key."""
        if self.openai_key:
            masked_key = self.openai_key[:6] + '*' * (len(self.openai_key) - 6)
            return masked_key
        return None
