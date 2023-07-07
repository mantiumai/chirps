"""Admin interface definitions for target application models."""

from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicParentModelAdmin

from .models import BaseTarget
from .providers.mantium import MantiumTarget
from .providers.pinecone import PineconeTarget
from .providers.redis import RedisTarget


class BaseTargetAdmin(PolymorphicParentModelAdmin):
    """Base admin class for the BaseTarget model."""

    base_model = BaseTarget


class PineconeTargetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the PineconeTarget model."""

    base_model = PineconeTarget


class MantiumTargetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the MantiumTarget model."""

    base_model = MantiumTarget


class RedisTargetAdmin(PolymorphicChildModelAdmin):
    """Admin class for the RedisTarget model."""

    base_model = RedisTarget


admin.site.register(RedisTarget)
admin.site.register(MantiumTarget)
