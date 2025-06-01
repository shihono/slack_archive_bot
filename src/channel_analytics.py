"""get analytics file"""
from datetime import datetime, date, timedelta
import gzip
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_channel_data(client, date)-> list[dict]:
    """Retrieve public_channel list

    API https://api.slack.com/methods/admin.analytics.getFile/
    """
    try:
        result = client.admin_analytics_getFile(type="public_channel", date=date)
        if result.headers.get("content-type") == "application/gzip":
            data = gzip.decompress(result.data)
            return [json.loads(d) for d in data.splitlines()]
        else:
            print("Invalid content-type", result.headers.get("content-type"))
            return None
    except SlackApiError as e:
        print("Slack Error", e)
        raise e
    
def is_not_active_channels(date_last_active: int, days: int) -> bool:
    # date_last_active is UNIX time
    last_active_dt = datetime.fromtimestamp(date_last_active)
    if last_active_dt + timedelta(days=days) < datetime.today():
        return True
    return False

def list_not_active_channels(
        client: WebClient, 
        threshold_days: int,
        target_date: date = None,
        skip_shared: bool = True,
        skip_guest: bool = False,
    ):
    """get not active channels

    Args:

    """
    if target_date is None:
        # get last week date
        date = date.today() - timedelta(days=7)
    channel_list = get_channel_data(client, date=target_date.isoformat())
    if not channel_list:
        return None
    
    not_active_channel_list = []
    for channel in channel_list:
        date_last_active = channel["date_last_active"]
        if skip_shared and channel["is_shared_externally"] == True:
            continue
        if skip_guest and channel["guest_members_count"] > 0:
            continue
        if is_not_active_channels(date_last_active, threshold_days):
            not_active_channel_list.append(channel)
    return not_active_channel_list
