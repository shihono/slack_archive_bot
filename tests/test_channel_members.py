import unittest
from unittest.mock import patch
from slack_sdk import WebClient
from src.channel_members import SlackChannelMembers


class TestSlackChannelMembers(unittest.TestCase):
    def setUp(self):
        mock_client = WebClient()
        self.channel_id = "CHANNEL_ID"
        self.helper = SlackChannelMembers(client=mock_client)

    @patch.object(WebClient, "conversations_members")
    def test_get_user_ids_in_channel(self, mock_conversations_members):
        # モックレスポンスを定義（ページネーションなし）
        mock_conversations_members.return_value = {
            "ok": True,
            "members": ["U111", "U222", "U333"],
            "response_metadata": {"next_cursor": ""},
        }

        user_ids = self.helper.get_user_ids_in_channel(self.channel_id)
        self.assertEqual(user_ids, ["U111", "U222", "U333"])
        mock_conversations_members.assert_called_once_with(
            channel=self.channel_id, cursor=None, limit=200
        )

    def test_convert_id_to_mention(self):
        cases = [["U012AB3CD", "<@U012AB3CD>"], ["U345AB6CD", "<@U345AB6CD>"]]
        for uid, expected in cases:
            with self.subTest(uid=uid, expected=expected):
                result = self.helper.convert_id_to_mention(uid)
                self.assertEqual(result, expected)

    @patch.object(SlackChannelMembers, "get_user_ids_in_channel")
    def test_get_mentions_in_channel(self, mock_get_user_ids):
        mock_get_user_ids.return_value = ["U111", "U222"]
        mentions = self.helper.get_mentions_in_channel(self.channel_id)
        self.assertEqual(mentions, ["<@U111>", "<@U222>"])

    @patch.object(SlackChannelMembers, "get_mentions_in_channel")
    def test_build_mentions_blocks_with_users(self, mock_get_mentions):
        mock_get_mentions.return_value = ["<@U111>", "<@U222>"]

        blocks = self.helper.build_mentions_blocks(self.channel_id)
        self.assertEqual(blocks[0]["type"], "section")
        self.assertDictEqual(
            {"type": "mrkdwn", "text": "<@U111>\n<@U222>"}, blocks[0]["text"]
        )

    @patch.object(SlackChannelMembers, "get_mentions_in_channel")
    def test_build_mentions_blocks_empty(self, mock_get_mentions):
        mock_get_mentions.return_value = []

        blocks = self.helper.build_mentions_blocks(self.channel_id)
        self.assertIn(
            "There are no members in this channel.", blocks[0]["text"]["text"]
        )


if __name__ == "__main__":
    unittest.main()
