import pytest
from src.channel_analytics import (
    is_not_active_channels,
    get_channel_data,
    list_not_active_channels,
)
from datetime import datetime, timedelta
from unittest import mock
import gzip
import json


def test_get_channel_data():
    with mock.patch("slack_sdk.WebClient") as client:
        # https://api.slack.com/methods/admin.analytics.getFile#examples
        mock_response = [
            {
                "enterprise_id": "EJB3MZFLM",
                "team_id": "EJB3MZFLM",
                "originating_team": {"team_id": "T5J3Q04QZ", "name": "postmodernity"},
                "channel_id": "CNGL0KGG1",
                "date_created": 1555111593,
                "date_last_active": 1684820530,
                "total_members_count": 7,
                "full_members_count": 6,
                "guest_member_count": 1,
                "messages_posted_count": 223,
                "messages_posted_by_members_count": 80,
                "members_who_viewed_count": 225,
                "members_who_posted_count": 3,
                "reactions_added_count": 23,
                "visibility": "public",
                "channel_type": "single_workspace_channel",
                "is_shared_externally": False,
                "shared_with": [],
                "externally_shared_with_organizations": [],
                "date": "2020-11-14",
            }
        ]
        # gzip data
        mock_response = gzip.compress(
            b"\n".join([json.dumps(item).encode("utf-8") for item in mock_response])
        )
        client.admin_analytics_getFile.return_value = mock.Mock(
            headers={"content-type": "application/gzip"}, data=mock_response
        )
        result = get_channel_data(client, "2025-01-01", False)
        assert result is not None


def test_get_channel_data_invalid_content_type():
    with mock.patch("slack_sdk.WebClient") as client:
        client.admin_analytics_getFile.return_value = mock.Mock(
            headers={"content-type": "application/json"}, data=b"{}"
        )
        with pytest.raises(ValueError, match="Invalid content-type"):
            get_channel_data(client, "2025-01-01", False)


@pytest.mark.parametrize(
    "date_last_active_dt, days, expected",
    [
        (datetime(2025, 1, 1, 0, 0, 0), 30, False),
        (datetime(2024, 1, 1, 0, 0, 0), 30, True),
        (datetime(2024, 12, 1, 0, 0, 0), 30, True),
        (datetime(2024, 12, 2, 0, 0, 0), 30, False),
        (datetime(2024, 12, 3, 0, 0, 0), 30, False),
        (datetime(2024, 12, 1, 0, 0, 0), 100, False),
        (datetime(2024, 5, 1, 0, 0, 0), 100, True),
    ],
)
def test_is_not_active_channels(date_last_active_dt, days, expected):
    target_dt = datetime(2025, 1, 1, 0, 0, 0)
    date_last_active = date_last_active_dt.timestamp()
    result = is_not_active_channels(date_last_active, days, target_dt=target_dt)
    assert result == expected, (
        f"Expected {expected} but got {result} for date_last_active={date_last_active}, days={days}"
    )


@pytest.mark.parametrize(
    "threshold_days, skip_shared, skip_guest, expected_indexes",
    [
        (30, True, True, [1]),
        (30, True, False, [1, 3]),
        (30, False, True, [1, 2]),
        (30, False, False, [1, 2, 3]),
        (40, False, False, []),
        (5, False, False, [0, 1, 2, 3]),
    ],
)
def test_list_not_active_channels(
    threshold_days, skip_shared, skip_guest, expected_indexes
):
    target_dt = datetime(2025, 1, 1, 0, 0, 0)
    mock_channel_data = [
        {
            "date_last_active": (target_dt - timedelta(days=10)).timestamp(),
            "is_shared_externally": False,
            "guest_members_count": 0,
        },
        {
            "date_last_active": (target_dt - timedelta(days=40)).timestamp(),
            "is_shared_externally": False,
            "guest_members_count": 0,
        },
        {
            "date_last_active": (target_dt - timedelta(days=40)).timestamp(),
            "is_shared_externally": True,
            "guest_members_count": 0,
        },
        {
            "date_last_active": (target_dt - timedelta(days=40)).timestamp(),
            "is_shared_externally": False,
            "guest_members_count": 10,
        },
    ]

    mock_client = mock.Mock()
    with mock.patch("src.channel_analytics.get_channel_data") as mock_get_channel_data:
        mock_get_channel_data.return_value = mock_channel_data
        with mock.patch(
            "src.channel_analytics.is_not_active_channels"
        ) as mock_is_not_active:
            mock_is_not_active.side_effect = lambda date_last_active, days, target_dt: (
                datetime.fromtimestamp(date_last_active) + timedelta(days=days)
                < target_dt
            )
            result = list_not_active_channels(
                client=mock_client,
                threshold_days=threshold_days,
                target_dt=target_dt,
                skip_shared=skip_shared,
                skip_guest=skip_guest,
                dry_run=True,
            )
            assert len(result) == len(expected_indexes)
            for i, channel in enumerate(result):
                assert channel == mock_channel_data[expected_indexes[i]]
