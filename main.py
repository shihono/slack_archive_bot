import os
import json
import click
from dotenv import load_dotenv
from slack_sdk import WebClient

from src.channel_analytics import list_not_active_channels
from src.send_message import join_channels
from src.archive import archive_channels


@click.group()
def cli():
    click.echo("Starting...")
    pass


@cli.command("list")
@click.option(
    "--threshold-days",
    required=False,
    default=100,
    help="Days of condition to archive inactive channels",
)
@click.option(
    "--send-message",
    is_flag=True,
    help="Flag to send notice message to inactive channels",
)
@click.option(
    "--save-path", required=False, help="Save inactive channel list as json file"
)
@click.option("--dry-run", is_flag=True)
def list_channel(threshold_days, send_message, save_path, dry_run):
    """list channel and prepare to archive channels

    * Get inactive channels by executing `admin.analytics.getFile`

    * App join inactive channels
    """
    click.echo(
        f"threshold_days: {threshold_days}, send_message: {send_message}, save_path: {save_path}, dry-run: {dry_run}"
    )
    load_dotenv(override=True)
    slack_user_token = os.getenv("SLACK_USER_TOKEN")
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    if not (slack_user_token and slack_bot_token):
        raise ValueError("SLACK_USER_TOKEN or SLACK_BOT_TOKEN is not set")
    user_client = WebClient(token=slack_user_token)
    result = list_not_active_channels(
        user_client, threshold_days=threshold_days, dry_run=dry_run
    )
    print(f"Get {len(result)} channels")
    if len(result) == 0:
        print("No channels were found that should be archived")
        return
    if save_path:
        with open(save_path, "w") as f:
            json.dump({"result": result}, f, indent=4)
        print(f"Save file: {save_path}")

    bot_client = WebClient(token=slack_bot_token)
    channel_list = [data["channel_id"] for data in result]
    # Join channels that should be archived
    join_channels(bot_client, channel_list, send_message, threshold_days)
    print("Ready to archive channels by executing archive command.")


@click.option(
    "--threshold-days",
    required=False,
    default=100,
    help="Days of condition to archive inactive channels",
)
@click.option("--dry-run", is_flag=True)
@cli.command("archive")
def archive_channel(threshold_days, dry_run):
    slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
    if not slack_bot_token:
        raise ValueError("SLACK_BOT_TOKEN is not set")
    bot_client = WebClient(token=slack_bot_token)
    result = archive_channels(bot_client, threshold_days, dry_run)
    print(f"End archive channels: {len(result)} channels")


if __name__ == "__main__":
    cli()
