from django.contrib import admin
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import PublicBody, Esic, FOIRequest, Message


class ModerationStatusListFilter(admin.SimpleListFilter):
    title = _("moderation status")
    parameter_name = "moderation_status"

    def lookups(self, request, model_admin):
        return (
            ("pending", _("Pending")),
            ("approved", _("Approved")),
            ("rejected", _("Rejected")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        moderation_status = {
            "approved": True,
            "rejected": None,
        }

        if value is not None:
            return queryset.filter(moderation_status=moderation_status[value])


class ModerationSenderTypeFilter(admin.SimpleListFilter):
    title = _("sender type")
    parameter_name = "sender_type"

    def lookups(self, request, model_admin):
        return (
            ("user", _("User")),
            ("government", _("Government")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            sender_is_null = value == "government"
            return queryset.exclude(sender_id__isnull=sender_is_null)


class MessageInline(admin.StackedInline):
    model = Message

    list_display = ("moderation_status",)
    list_filter = (ModerationStatusListFilter,)

    readonly_fields = ("moderated_at",)
    fieldsets = (
        (
            "Message",
            {
                "fields": (
                    "foi_request",
                    "sender",
                    "receiver",
                    "summary",
                    "body",
                    "attached_file",
                    "sent_at",
                ),
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "moderation_status",
                    "moderation_message",
                    "moderated_at",
                )
            },
        ),
    )
    ordering = ["created_at"]
    autocomplete_fields = ("sender", "receiver")


class FOIRequestStatusFilter(admin.SimpleListFilter):
    title = "Status do pedido"
    parameter_name = "request_status"
    template = "admin/foi_requests/foirequest/status_filter.html"

    def lookups(self, request, model_admin):
        return (
            (Message.STATUS.pending.name, "Aguardando moderação"),
            (Message.STATUS.ready.name, "Prontos para envio"),
            (FOIRequest.STATUS.waiting_government.name, "Aguardando órgão"),
            (FOIRequest.STATUS.delayed.name, "Atrasados"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value not in dict(self.lookup_choices):
            return queryset

        latest_message = Message.objects.filter(foi_request=OuterRef("pk")).order_by(
            "-created_at"
        )
        queryset = queryset.alias(
            latest_message_id=Subquery(latest_message.values("pk")[:1]),
            latest_sender_id=Subquery(latest_message.values("sender_id")[:1]),
            latest_sent_at=Subquery(latest_message.values("sent_at")[:1]),
            latest_moderation_status=Subquery(
                latest_message.values("moderation_status")[:1]
            ),
        ).filter(latest_message_id__isnull=False, latest_sender_id__isnull=True)

        if value == Message.STATUS.pending.name:
            return queryset.filter(
                latest_sent_at__isnull=True, latest_moderation_status__isnull=True
            )
        if value == Message.STATUS.ready.name:
            return queryset.filter(
                latest_sent_at__isnull=True, latest_moderation_status=True
            )

        reply_deadline = timezone.now() - timezone.timedelta(days=FOIRequest.REPLY_DAYS)
        if value == FOIRequest.STATUS.delayed.name:
            return queryset.filter(latest_sent_at__lte=reply_deadline)
        return queryset.filter(latest_sent_at__gt=reply_deadline)


@admin.register(FOIRequest)
class FOIRequestAdmin(admin.ModelAdmin):
    list_display = (
        "protocol",
        "esic_protocol",
        "public_body",
        "esic",
        "status_label",
        "can_publish",
    )

    readonly_fields = (
        "protocol",
        "created_at",
        "updated_at",
    )

    inlines = (MessageInline,)
    list_filter = (FOIRequestStatusFilter,)
    change_list_template = "admin/foi_requests/foirequest/change_list.html"

    @admin.display(description="Status")
    def status_label(self, obj):
        return obj.status.value


def approve_messages(modeladmin, request, queryset):
    queryset.update(moderation_status=True)


approve_messages.short_description = "Approve selected messages"


class ModerationStatusListFilter(admin.SimpleListFilter):
    title = _("status")

    parameter_name = "moderation_status"

    def lookups(self, request, model_admin):
        # Need to replace None with 'pending' to differentiate between "disable
        # filter" and "filter None values"

        return (
            ("pending", _("Pending")),
            ("approved_not_sent", _("Approved (not sent)")),
            ("sent", _("Sent")),
            ("rejected", _("Rejected")),
        )

    def queryset(self, request, queryset):
        filters = {}

        value = self.value()
        if value is not None:
            param = self.parameter_name

            value_to_filters = {
                "pending": {param: None},
                "approved_not_sent": {param: True, "sent_at__isnull": True},
                "sent": {param: True, "sent_at__isnull": False},
                "rejected": {param: False},
            }

            filters = value_to_filters[value]

        return queryset.filter(**filters)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    actions = (approve_messages,)

    list_display = (
        "foi_request_link",
        "sender_type",
        "receiver",
        "summary",
        "body",
        "sent_at",
        "created_at",
    )

    # We change the messages on the FOIRequest change page instead
    list_display_links = None

    list_filter = (
        ModerationStatusListFilter,
        ModerationSenderTypeFilter,
    )

    fieldsets = (
        (
            "Message",
            {
                "fields": (
                    "foi_request",
                    "sender",
                    "receiver",
                    "summary",
                    "body",
                    "attached_file",
                    "created_at",
                    "updated_at",
                    "sent_at",
                ),
            },
        ),
    )

    readonly_fields = (
        "moderated_at",
        "created_at",
        "updated_at",
    )

    class Meta:
        ordering = ["created_at"]

    def get_fieldsets(self, request, obj=None):
        extra_fieldsets = ()
        sender_is_user = obj and obj.sender is None

        if sender_is_user:
            extra_fieldsets = (
                (
                    "Moderation",
                    {
                        "fields": (
                            "moderation_status",
                            "moderation_message",
                            "moderated_at",
                        ),
                    },
                ),
            )

        return self.fieldsets + extra_fieldsets

    def get_readonly_fields(self, request, obj=None):
        extra_readonly_fields = ()

        if obj:
            # Disallow editing fields
            extra_readonly_fields = (
                "foi_request",
                "sender",
                "receiver",
            )

        return self.readonly_fields + extra_readonly_fields

    def foi_request_link(self, obj):
        foi_request = obj.foi_request
        url = reverse(
            f"admin:{foi_request._meta.app_label}_{foi_request._meta.model_name}_change",
            args=(foi_request.pk,),
        )
        return mark_safe(f'<a href="{url}">{foi_request.protocol}</a>')

    foi_request_link.short_description = _("FOI Request")


admin.site.register(PublicBody, search_fields=["name"])
admin.site.register(Esic)
