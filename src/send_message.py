"""send notice message to archive"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_text(client: WebClient, channel_id: str, blocks: list):
    """https://api.slack.com/methods/chat.postMessage

    send message with blocks (JSON based-array)
    """
    try:
        result = client.chat_postMessage(channel=channel_id, blocks=blocks)
        print("Success:", result)
    except SlackApiError as e:
        print("Slack Error", e)
        raise e


def format_notice_message(channel_name: str, days: int) -> list:
    """create massege
    todo set template text
    """
    message = (
        f"#{channel_name}は{days}日間投稿がありません。アーカイブ対象になっています。"
    )
    return [
        {"type": "markdown", "text": "# Notice"},
        {
            "type": "markdown",
            "text": message,
        },
    ]


def join_channels(
    client: WebClient, channel_list: list[str], send_message: bool, days: int
):
    """join inactive channel and send message"""
    joined_channels = []
    for channel_id in channel_list:
        try:
            response = client.conversations_join(channel=channel_id)
            joined_channels.append(
                {"channel_name": response["channel"]["name"], "channel_id": channel_id}
            )
        except SlackApiError as e:
            error_message = e.response.get("error", "")
            print(f"Fail to join {channel_id}, {error_message}")
            print(e)
            # if authorization or authentication error, stop processing
            if error_message in [
                "invalid_auth",
                "missing_scope",
                "not_authed",
                "token_expired",
            ]:
                print("Processing stopped due to token problems")
                return
            continue

    print(f"End: {len(joined_channels)} channels joined")
    if not send_message or len(joined_channels) == 0:
        return
    for channel_item in joined_channels:
        channel_name = channel_item["channel_name"]
        channel_id = channel_item["channei_id"]
        message_block = format_notice_message(channel_name, days)
        send_message(client, channel_name, message_block)
    return joined_channels
