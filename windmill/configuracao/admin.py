from django.contrib import admin

# Register your models here.
from .models import ConfigCambio, ConfigZeragem

admin.site.register(ConfigCambio)
admin.site.register(ConfigZeragem)
