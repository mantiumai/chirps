from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy import Column, Dialect, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from mantium_scanner.models.base import Base

ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)


class EncryptedString(TypeDecorator):
    """Custom encrypted string column type."""

    impl = String

    def process_bind_param(self, value: Any, dialect: Dialect) -> str:
        """Encrypt the value on the way in."""
        if value is not None:
            value = fernet.encrypt(value.encode('utf-8')).decode('utf-8')
        return value

    def process_result_value(self, value: Any, dialect: Dialect) -> str:
        """Decrypt the value on the way out."""
        if value is not None:
            value = fernet.decrypt(value.encode('utf-8')).decode('utf-8')
        return value


class Provider(Base):
    """Provider model"""

    __tablename__ = 'providers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider_type = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='providers')
    configurations = relationship('Configuration', back_populates='provider')


class Configuration(Base):
    """Configuration model"""

    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    app_id = Column(String)
    bearer_token: Column = Column(EncryptedString())
    environment = Column(String)
    api_token: Column = Column(EncryptedString())
    index_name = Column(String)
    provider_id = Column(Integer, ForeignKey('providers.id'))

    provider = relationship('Provider', back_populates='configurations')
