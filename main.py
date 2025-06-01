import os
from dotenv import load_dotenv
from slack_sdk import WebClient

from src.channel_analytics import list_not_active_channels

def main():
    load_dotenv() 
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=slack_token)
    result = list_not_active_channels(client, threshold_days=100)


if __name__ == "__main__":
    main()
