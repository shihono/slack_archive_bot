"""get analytics file"""

from datetime import datetime, timedelta
import gzip
import json
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_channel_data(client: WebClient, target_date: str, dry_run: bool) -> list[dict]:
    """Retrieve public_channel list

    API https://api.slack.com/methods/admin.analytics.getFile/

    Args:
        client: slack_sdk WebClient
        target_date: date to get channel data in "YYYY-MM-DD" format
        dry_run: if True, do not send API request
    """
    if dry_run:
        return []
    try:
        result = client.admin_analytics_getFile(type="public_channel", date=target_date)
        if result.headers.get("content-type") == "application/gzip":
            data = gzip.decompress(result.data)
            return [json.loads(d) for d in data.splitlines()]
        else:
            msg = "Invalid content-type", result.headers.get("content-type")
            print(msg)
            raise ValueError(msg)
    except SlackApiError as e:
        print("Slack Error", e)
        raise e


def is_not_active_channels(
    date_last_active: int, days: int, target_dt: Optional[datetime] = None
) -> bool:
    if target_dt is None:
        target_dt = datetime.now()
    # date_last_active is UNIX time
    last_active_dt = datetime.fromtimestamp(date_last_active)
    if last_active_dt + timedelta(days=days) < target_dt:
        return True
    return False


def list_not_active_channels(
    client: WebClient,
    threshold_days: int,
    target_dt: Optional[datetime] = None,
    skip_shared: bool = True,
    skip_guest: bool = False,
    dry_run: bool = False,
):
    """get not active channels

    Args:
        client: slack_sdk WebClient
        threshold_days: days to archive inactive channels
        target_date: datetime to get channel data
        skip_shared: skip shared channels
        skip_guest: skip channels with guest members
        dry_run: if True, do not send API request
    """
    if target_dt is None:
        # analytics data is not available for today
        target_dt = datetime.today() - timedelta(days=7)
    channel_list = get_channel_data(
        client, target_date=target_dt.strftime("%Y-%m-%d"), dry_run=dry_run
    )
    print(f"Get {len(channel_list)} channels")
    if not channel_list:
        return []

    not_active_channel_list = []
    for channel in channel_list:
        date_last_active = channel["date_last_active"]
        if skip_shared and channel["is_shared_externally"]:
            continue
        if skip_guest and channel["guest_members_count"] > 0:
            continue
        if is_not_active_channels(date_last_active, threshold_days, target_dt):
            not_active_channel_list.append(channel)
    return not_active_channel_list
