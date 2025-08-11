from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackChannelMembers:
    def __init__(self, client: WebClient):
        self.client = client

    def get_user_ids_in_channel(self, channel_id: str) -> list[str]:
        """get user ids in channel"""
        try:
            members_list = []
            cursor = None
            while True:
                response = self.client.conversations_members(
                    channel=channel_id, cursor=cursor, limit=200
                )
                members = response.get("members")
                if members:
                    members_list.extend(members)
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            return sorted(members_list)
        except SlackApiError as e:
            print(f"Error fetching members: {e.response['error']}")
            return []

    @staticmethod
    def convert_id_to_mention(user_id: str) -> str:
        return f"<@{user_id}>"

    def get_mentions_in_channel(self, channel_id: str) -> list[str]:
        """get user ID list with format

        Return:
            mention syntaxed user id list
            e.g. ["<@U012AB3CD>","<@U345AB6CD>"]
        """
        user_ids = self.get_user_ids_in_channel(channel_id)
        return [self.convert_id_to_mention(user_id) for user_id in user_ids]

    def build_mentions_blocks(self, channel_id: str) -> list[dict]:
        """create mention list as Slack Blocks"""
        mentions = self.get_mentions_in_channel(channel_id)
        if not mentions:
            text = "There are no members in this channel."
        else:
            text = "\n".join(mentions)
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]
        return blocks
