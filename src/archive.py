import time
from datetime import datetime
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.channel_analytics import is_not_active_channels


def run_conversations_list(
    client: WebClient, channel_types="public_channel", cursor=None, is_retry=False
):
    """conversations_list wrapper
    API: https://api.slack.com/methods/conversations.list

    Return:
        SlackResponse
    """
    try:
        response = client.conversations_list(
            types=channel_types, exclude_archived=True, limit=1000, cursor=cursor
        )
        return response
    except SlackApiError as e:
        error = e.response["error"]
        if error == "ratelimited" and not is_retry:
            retry_after = int(e.response.headers.get("Retry-After", 10))
            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            # retry
            run_conversations_list(client, channel_types, cursor, is_retry=True)
        else:
            print(f"Fail to get channels : {e.response['error']}")
            raise e


def list_bot_joined_channels(
    client: WebClient, channel_types="public_channel"
) -> list[dict]:
    """Lists all channels that bot joined

    Return:
        list `{ "id": "channei_id", "name": "channel_name" }`
    """
    request_cnt = 0
    channels = []

    try:
        cursor = None
        while True:
            response = run_conversations_list(
                client, channel_types, cursor, is_retry=False
            )
            for channel in response["channels"]:
                if channel.get("is_member", False):
                    channels.append({"id": channel["id"], "name": channel["name"]})
            cursor = response["response_metadata"].get("next_cursor")
            print(f"run conversations_list {request_cnt + 1}")
            request_cnt += 1
            if not cursor:
                break
            time.sleep(1)

    except SlackApiError as e:
        print(f"Fail to get channels : {e.response['error']}")
        raise e
    return channels


def get_latest_message_ts(
    client: WebClient, channel_id: str, bot_user_id=None
) -> Optional[int]:
    """get timestamp
    if bot_user_id is set, skip this bot message

    Return:
        timestamp
    """
    try:
        response = client.conversations_history(channel=channel_id, limit=10)
        messages = response.get("messages", [])
        for message in messages:
            if (
                bot_user_id
                and message.get("bot_id")
                and message["bot_id"] == bot_user_id
            ):
                continue
            else:
                return int(float(message["ts"]))
        else:
            print(f"Message not found: {channel_id}")
            return None
    except SlackApiError as e:
        print(f"Fail to get message: {channel_id}, {e.response['error']}")
        return None


def archive_channels(
    client: WebClient,
    threshold_days: int,
    target_dt: datetime = None,
    dry_run: bool = True,
):
    """archive channels that bot joined
    If the channel become active, bot leave from it.

    Args:
        client: slack_sdk WebClient
        threshold_days: Days of condition to archive inactive channels
        dry_run: if True, only check if each channel that bot joined is inactive

    Return:
        channel info list
    """
    archived_channels = []
    if target_dt is None:
        target_dt = datetime.now()
    # get bot info
    auth_info = client.auth_test()
    bot_user_id = auth_info.get("user_id", None)

    for channel_info in list_bot_joined_channels(client):
        latest_ts = get_latest_message_ts(
            client, channel_info["id"], bot_user_id=bot_user_id
        )
        if latest_ts is None:
            # todo archive if there are no messages in the channel
            continue
        if is_not_active_channels(latest_ts, threshold_days, target_dt=target_dt):
            if not dry_run:
                # todo list members before archive
                try:
                    client.conversations_archive(channel=channel_info["id"])
                except SlackApiError as e:
                    print(f"Fail to archive: {channel_info}")
                    raise e
            archived_channels.append(channel_info)
        elif not dry_run:
            # todo send message
            client.channels_leave(channel=channel_info["id"])
    return archived_channels


def leave_channels(client: WebClient, dry_run: bool = True):
    """leave all channels that bot joined

    Args:
        client: slack_sdk WebClient
        dry_run: if True, only list joined channels
    Return:
        channel info list
    """
    joined_channels = []
    for channel_info in list_bot_joined_channels(client):
        joined_channels.append(channel_info)
        if dry_run:
            continue
        client.channels_leave(channel=channel_info["id"])
    return joined_channels
