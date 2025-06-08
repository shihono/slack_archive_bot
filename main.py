import os
import json
import click
from dotenv import load_dotenv
from slack_sdk import WebClient

from src.channel_analytics import list_not_active_channels


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
    click.echo(
        f"threshold_days: {threshold_days}, send_message: {send_message}, save_path: {save_path}, dry-run: {dry_run}"
    )
    load_dotenv(override=True)
    slack_token = os.getenv("SLACK_USER_TOKEN")
    if not slack_token:
        raise ValueError(f"SLACK_USER_TOKEN is not set {slack_token}")
    client = WebClient(token=slack_token)
    result = list_not_active_channels(client, threshold_days=100, dry_run=dry_run)
    print(f"Get {len(result)} channels")
    if save_path:
        with open(save_path, "w") as f:
            json.dump({"result": result}, f, indent=4)
        print(f"Save file: {save_path}")


@cli.command("archive")
def archive_channel():
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN is not set")
    raise NotImplementedError()


if __name__ == "__main__":
    cli()
