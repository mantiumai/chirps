"""Custom fields for encrypting and decrypting data."""

from cryptography.fernet import Fernet
from django.conf import settings
from fernet_fields import EncryptedCharField


class CustomEncryptedCharField(EncryptedCharField):
    """Custom encrypted char field that uses the fernet key from settings."""
    def __init__(self, *args, **kwargs):
        """Initialize the field."""
        self.fernet = Fernet(settings.FERNET_KEY)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, *args):
        """Decrypt the value from the database."""
        if value is not None:
            value = super().from_db_value(value, expression, connection, args)
            if isinstance(value, bytes):
                return value.decode('utf-8')

            return value
        return None
