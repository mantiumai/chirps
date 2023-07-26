"""Admin interface definitions for asset application models."""

from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from .models import BaseAsset
from .providers.mantium import MantiumAsset
from .providers.pinecone import PineconeAsset
from .providers.redis import RedisAsset


class BaseAssetAdmin(PolymorphicParentModelAdmin):
    """Base admin class for the BaseAsset model."""

    base_model = BaseAsset


class PineconeAssetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the PineconeAsset model."""

    base_model = PineconeAsset


class MantiumAssetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the MantiumAsset model."""

    base_model = MantiumAsset


class RedisAssetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the RedisAsset model."""

    base_model = RedisAsset


admin.site.register(RedisAsset)
admin.site.register(MantiumAsset)
admin.site.register(PineconeAsset)
