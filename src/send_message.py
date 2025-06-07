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
