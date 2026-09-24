import unittest.mock as mock
import pytest
from django.urls import reverse
from django.utils import timezone

from ..admin import (
    ModerationStatusListFilter,
    ModerationSenderTypeFilter,
    FOIRequestStatusFilter,
)
from ..models import FOIRequest, Message, PublicBody


@pytest.mark.django_db
class TestFOIRequestStatusFilter:
    @pytest.fixture
    def requests_by_status(self):
        now = timezone.now()
        deadline = now - timezone.timedelta(days=FOIRequest.REPLY_DAYS)
        just_inside_deadline = deadline + timezone.timedelta(microseconds=1)
        public_body = PublicBody.objects.create(name="Órgão de teste", level="Federal")
        scenarios = (
            ("pending", None, None, None),
            ("ready", True, None, None),
            ("rejected", False, None, None),
            ("waiting_government", True, just_inside_deadline, None),
            ("delayed", True, deadline, None),
            ("waiting_user", True, now, public_body),
            ("finished", True, deadline, public_body),
        )
        requests = {}
        for status, moderation, sent_at, sender in scenarios:
            foi_request = FOIRequest.objects.create()
            # A mensagem anterior não deve determinar o filtro.
            previous = Message.objects.create(
                foi_request=foi_request, receiver=public_body, body="Pedido anterior"
            )
            Message.objects.filter(pk=previous.pk).update(created_at=deadline)
            Message.objects.create(
                foi_request=foi_request,
                sender=sender,
                receiver=public_body if sender is None else None,
                body="Última mensagem",
                moderation_status=moderation,
                moderation_message="Justificativa de moderação",
                sent_at=sent_at,
            )
            requests[status] = foi_request
        requests["empty"] = FOIRequest.objects.create()
        with mock.patch("django.utils.timezone.now", return_value=now):
            yield requests

    @pytest.mark.parametrize(
        "value", ("pending", "ready", "waiting_government", "delayed", None, "invalid")
    )
    def test_filter_matches_current_status(self, requests_by_status, value):
        params = (
            {} if value is None else {FOIRequestStatusFilter.parameter_name: [value]}
        )
        status_filter = FOIRequestStatusFilter(None, params, FOIRequest, None)
        result = status_filter.queryset(None, FOIRequest.objects.all())
        if value in dict(status_filter.lookup_choices):
            expected = {
                item.pk
                for item in requests_by_status.values()
                if item.status.name == value
            }
        else:
            expected = {item.pk for item in requests_by_status.values()}
        assert set(result.values_list("pk", flat=True)) == expected

    def test_buttons_and_filtered_results(self, admin_client, requests_by_status):
        url = reverse("admin:foi_requests_foirequest_changelist")
        response = admin_client.get(url, {"request_status": "ready"}, secure=True)
        assert response.status_code == 200
        content = response.content.decode()
        for label in (
            "Todos",
            "Aguardando moderação",
            "Prontos para envio",
            "Aguardando órgão",
            "Atrasados",
        ):
            assert label in content
        assert 'aria-current="true">Prontos para envio</a>' in content
        assert "STATUS.ready" not in content
        assert list(response.context["cl"].result_list) == [requests_by_status["ready"]]


class TestModerationStatusListFilter:
    def test_lookups_are_as_expected(self):
        list_filter = self._create_list_filter()
        lookup_keys = [lookup[0] for lookup in list_filter.lookups(None, None)]
        assert lookup_keys == [
            "pending",
            "approved_not_sent",
            "sent",
            "rejected",
        ]

    @pytest.mark.parametrize(
        "value,filters",
        (
            (None, {}),
            ("pending", {"moderation_status": None}),
            ("approved_not_sent", {"moderation_status": True, "sent_at__isnull": True}),
            ("sent", {"moderation_status": True, "sent_at__isnull": False}),
            ("rejected", {"moderation_status": False}),
        ),
    )
    def test_queryset(self, value, filters):
        list_filter = self._create_list_filter(value)
        queryset = mock.Mock()
        list_filter.queryset(None, queryset)

        queryset.filter.assert_called_with(**filters)

    def _create_list_filter(self, params_value=None):
        params = {
            ModerationStatusListFilter.parameter_name: [params_value],
        }
        return ModerationStatusListFilter(
            None,  # request
            params,  # params
            None,  # Model
            None,  # ModelAdmin
        )


class TestModerationSenderTypeFilter:
    @pytest.mark.parametrize(
        "value,filters",
        (
            ("user", {"sender_id__isnull": False}),
            ("government", {"sender_id__isnull": True}),
        ),
    )
    def test_queryset(self, value, filters):
        list_filter = self._create_list_filter(value)
        queryset = mock.Mock()
        list_filter.queryset(None, queryset)

        queryset.exclude.assert_called_with(**filters)

    def test_queryset_doesnt_filter_if_value_is_none(self):
        list_filter = self._create_list_filter()
        queryset = mock.Mock()
        list_filter.queryset(None, queryset)

        queryset.exclude.assert_not_called()

    def _create_list_filter(self, params_value=None):
        params = {
            ModerationSenderTypeFilter.parameter_name: [params_value],
        }
        return ModerationSenderTypeFilter(
            None,  # request
            params,  # params
            None,  # Model
            None,  # ModelAdmin
        )
