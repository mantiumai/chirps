"""Register Embedding model with admin site."""
from django.contrib import admin

from .models import Embedding

admin.site.register(Embedding)
