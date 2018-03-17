from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PublicBody, FOIRequest, Message


class MessageInline(admin.StackedInline):
    model = Message
    readonly_fields = (
        'created_at',
        'updated_at',
    )


class ModerationStatusListFilter(admin.SimpleListFilter):
    title = _('moderation status')
    parameter_name = 'moderation_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', _('Pending')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        moderation_status = None
        if self.value() == 'approved':
            moderation_status = True
        elif self.value() == 'rejected':
            moderation_status = False

        if value is not None:
            return queryset.filter(moderation_status=moderation_status)


@admin.register(FOIRequest)
class FOIRequestAdmin(admin.ModelAdmin):
    list_display = (
        'protocol',
        'moderation_status',
    )
    list_filter = (
        ModerationStatusListFilter,
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
