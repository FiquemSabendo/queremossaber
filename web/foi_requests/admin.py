from django.contrib import admin

from .models import PublicBody, FOIRequest

admin.site.register(PublicBody)
admin.site.register(FOIRequest)
