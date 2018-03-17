from django.contrib import admin

from .models import PublicBody, FOIRequest, Message


class MessageInline(admin.StackedInline):
    model = Message
    readonly_fields = (
        'created_at',
        'updated_at',
    )


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
    inlines = (
        MessageInline,
    )


admin.site.register(PublicBody)
