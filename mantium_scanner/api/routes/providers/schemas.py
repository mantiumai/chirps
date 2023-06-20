from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ProviderType(str, Enum):
    """Provider types enum."""

    MANTIUM = 'mantium'
    REDIS = 'redis'
    PINECONE = 'pinecone'


class BaseProvider(BaseModel):
    """Base Provider Schema."""

    name: str
    provider_type: ProviderType


class ProviderCreate(BaseProvider):
    """Provider create request schema."""


class Provider(BaseProvider):
    """Provider response schema."""

    id: int
    name: str
    user_id: int

    class Config:
        orm_mode = True


class ConfigurationBase(BaseModel):
    """Base Configuration Schema."""

    name: str
    app_id: Optional[str]
    bearer_token: Optional[str]
    environment: Optional[str]
    api_token: Optional[str]
    index_name: Optional[str]


class ConfigurationCreate(ConfigurationBase):
    """Configuration create request schema."""


class Configuration(ConfigurationBase):
    """Configuration response schema."""

    id: int
    provider_id: int

    class Config:
        orm_mode = True
