from django.contrib import admin

from .models import ApiClient


@admin.register(ApiClient)
class ApiClientAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    readonly_fields = ("token", "created_at")
