from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PublicBody, FOIRequest, Message


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


class MessageInline(admin.StackedInline):
    model = Message

    list_display = (
        'moderation_status',
    )
    list_filter = (
        ModerationStatusListFilter,
    )


@admin.register(FOIRequest)
class FOIRequestAdmin(admin.ModelAdmin):
    list_display = (
        'protocol',
    )

    readonly_fields = (
        'protocol',
        'created_at',
        'updated_at',
    )
    inlines = (
        MessageInline,
    )


def approve_messages(modeladmin, request, queryset):
    queryset.update(moderation_status=True)


approve_messages.short_description = 'Approve selected messages'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    actions = (
        approve_messages,
    )

    list_display = (
        'foi_request',
        'sender_type',
        'title',
        'body',
        'moderation_status',
        'created_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'foi_request',
                'sender',
                'receiver',
                'title',
                'body',
                'attached_file',
                'created_at',
                'updated_at',
                'sent_at',
            ),
        }),
    )

    readonly_fields = (
        'moderated_at',
        'created_at',
        'updated_at',
    )

    def get_fieldsets(self, request, obj=None):
        extra_fieldsets = ()
        sender_is_user = (obj and obj.sender is None)

        if sender_is_user:
            extra_fieldsets = (
                ('Moderation', {
                    'fields': (
                        'moderation_status',
                        'moderation_message',
                        'moderated_at',
                    ),
                }),
            )

        return self.fieldsets + extra_fieldsets

    def get_readonly_fields(self, request, obj=None):
        extra_readonly_fields = ()

        if obj:
            # Disallow editing fields
            extra_readonly_fields = (
                'foi_request',
                'sender',
                'receiver',
            )

        return self.readonly_fields + extra_readonly_fields


admin.site.register(PublicBody)
