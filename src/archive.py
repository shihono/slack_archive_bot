from datetime import datetime
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.channel_analytics import is_not_active_channels


def list_bot_joined_channels(
    client: WebClient, channel_types="public_channel"
) -> list[dict]:
    """Lists all channels that bot joined"""
    channels = []

    try:
        cursor = None
        while True:
            response = client.conversations_list(
                types=channel_types, exclude_archived=True, limit=100, cursor=cursor
            )
            for channel in response["channels"]:
                if channel.get("is_member", False):
                    channels.append({"id": channel["id"], "name": channel["name"]})
            cursor = response["response_metadata"].get("next_cursor")
            if not cursor:
                break

    except SlackApiError as e:
        print(f"Fail to get channels : {e.response['error']}")
        raise e
    return channels


def get_latest_message_ts(client: WebClient, channel_id: str) -> Optional[str]:
    """get timestamp"""
    try:
        response = client.conversations_history(channel=channel_id, limit=1)
        messages = response.get("messages", [])
        if messages:
            return messages[0]["ts"]
        else:
            print(f"Message not found: {channel_id}")
            return None
    except SlackApiError as e:
        print(f"Fail to get message: {channel_id}, {e.response['error']}")
        return None


def archive_channels(client: WebClient, threshold_days: int, dry_run: bool = True):
    """archive channels that bot joined
    If the channel become active, bot leave from it.

    Args:
        client: slack_sdk WebClient
        threshold_days: Days of condition to archive inactive channels
        dry_run: if True, only check if each channel that bot joined is inactive
    """
    archived_channels = []
    target_dt = datetime.now()
    for channel_info in list_bot_joined_channels(client):
        latest_ts = get_latest_message_ts(client, channel_info["id"])
        if latest_ts is None:
            continue
        if is_not_active_channels(int(latest_ts), threshold_days, target_dt=target_dt):
            if not dry_run:
                # todo list members before archive
                try:
                    client.conversations_archive(channel_info["id"])
                except SlackApiError as e:
                    print(f"Fail to archive: {channel_info}")
                    raise e
            archived_channels.append(channel_info)
        elif not dry_run:
            # todo send message
            client.channels_leave(channel_info["id"])
    return archived_channels
