import pytest
from unittest import mock
from slack_sdk.errors import SlackApiError
from src.send_message import send_text, join_channels


def test_send_text_success():
    with mock.patch("slack_sdk.WebClient") as client:
        # https://api.slack.com/methods/chat.postMessage#examples
        mock_response = {
            "ok": True,
            "channel": "C123ABC456",
            "ts": "1503435956.000247",
            "message": {
                "text": "Here's a message for you",
                "username": "ecto1",
                "bot_id": "B123ABC456",
                "attachments": [
                    {
                        "text": "This is an attachment",
                        "id": 1,
                        "fallback": "This is an attachment's fallback",
                    }
                ],
                "type": "message",
                "subtype": "bot_message",
                "ts": "1503435956.000247",
            },
        }
        client.chat_postMessage.return_value = mock.Mock(data=mock_response)
        result = send_text(client, "test_channel_id", ["test_message"])
        assert result is None


def test_send_text_error():
    with mock.patch("slack_sdk.WebClient") as client:
        mock_response = {"ok": False, "error": "too_many_attachments"}
        client.chat_postMessage.side_effect = SlackApiError(
            message="Error", response=mock_response
        )
        with pytest.raises(SlackApiError):
            send_text(client, "test_channel_id", ["test_message"])


def test_join_channels_error_join(capsys):
    with mock.patch("slack_sdk.WebClient") as client:
        response = mock.Mock()
        response.get.return_value = "not_authed"
        client.conversations_join.side_effect = SlackApiError(
            message="Error", response=response
        )
        join_channels(client, ["channel_id1", "channel_id2"], True, 100)
        captured = capsys.readouterr()
        assert "Processing stopped due to token problems" in captured.out
