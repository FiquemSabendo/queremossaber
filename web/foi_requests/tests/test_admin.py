import unittest.mock as mock
import pytest

from ..admin import (
    ModerationStatusListFilter,
    ModerationSenderTypeFilter,
)


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
            ModerationStatusListFilter.parameter_name: params_value,
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
            ModerationSenderTypeFilter.parameter_name: params_value,
        }
        return ModerationSenderTypeFilter(
            None,  # request
            params,  # params
            None,  # Model
            None,  # ModelAdmin
        )
