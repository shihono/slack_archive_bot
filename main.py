import os
from dotenv import load_dotenv
from slack_sdk import WebClient

from src.channel_analytics import list_not_active_channels


def main():
    load_dotenv()
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    if slack_token is None:
        raise ValueError("SLACK_BOT_TOKEN is not set")
    client = WebClient(token=slack_token)
    result = list_not_active_channels(client, threshold_days=100)
    print(f"Get {len(result)} channels")


if __name__ == "__main__":
    main()
