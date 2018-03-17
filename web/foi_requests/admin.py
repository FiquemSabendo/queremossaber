from django.contrib import admin

from .models import PublicBody, FOIRequest


@admin.register(FOIRequest)
class FOIRequestAdmin(admin.ModelAdmin):
    list_display = (
        'protocol',
        'moderation_status',
    )
    readonly_fields = (
        'protocol',
        'moderated_at',
        'created_at',
        'updated_at',
    )


admin.site.register(PublicBody)
