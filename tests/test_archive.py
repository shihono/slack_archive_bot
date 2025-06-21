from unittest import mock
from datetime import datetime, timedelta

from src.archive import (
    list_bot_joined_channels,
    get_latest_message_ts,
    archive_channels,
)


def test_list_bot_joined_channels():
    mock_client = mock.MagicMock()
    mock_client.conversations_list.return_value = {
        "channels": [
            {"id": "C001", "name": "general", "is_member": True},
            {"id": "C002", "name": "random", "is_member": False},
            {"id": "C003", "name": "dev", "is_member": True},
        ],
        "response_metadata": {"next_cursor": ""},
    }

    result = list_bot_joined_channels(mock_client)

    assert len(result) == 2
    assert {"id": "C001", "name": "general"} in result
    assert {"id": "C003", "name": "dev"} in result
    assert all("id" in ch and "name" in ch for ch in result)
    mock_client.conversations_list.assert_called_once()


def test_get_latest_message_ts():
    with mock.patch("slack_sdk.WebClient") as client:
        client.conversations_history.return_value = {
            "messages": [
                {
                    "type": "message",
                    "user": "U123ABC456",
                    "text": "I find you punny and would like to smell your nose letter",
                    "ts": "1512085950.000216",
                },
                {
                    "type": "message",
                    "user": "U222BBB222",
                    "text": "What, you want to smell my shoes better?",
                    "ts": "1512104434.000490",
                },
            ],
            "has_more": True,
            "pin_count": 0,
            "response_metadata": {"next_cursor": "bmV4dF90czoxNTEyMDg1ODYxMDAwNTQz"},
        }
        result = get_latest_message_ts(client, "channel_id")
        assert result == 1512085950


@mock.patch("src.archive.get_latest_message_ts")
@mock.patch("src.archive.list_bot_joined_channels")
def test_archive_channels_archive(mock_list_channels, mock_latest_message_ts):
    mock_list_channels.return_value = [
        {"id": "C001", "name": "channel01"},
        {"id": "C002", "name": "channel02"},
    ]

    target_dt = datetime(2025, 2, 1)
    mock_latest_message_ts.return_value = (target_dt - timedelta(days=30)).timestamp()

    mock_client = mock.MagicMock()
    mock_client.conversations_archive.return_value = mock.Mock(data={"ok": True})

    result = archive_channels(
        client=mock_client,
        threshold_days=14,
        dry_run=False,
        target_dt=target_dt,
    )

    assert len(result) == 2
    assert {"id": "C001", "name": "channel01"} in result
    assert {"id": "C002", "name": "channel02"} in result
    assert mock_client.conversations_archive.call_count == 2
