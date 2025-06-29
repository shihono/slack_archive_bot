# slack archive bot

slack bot を利用して、一定期間 active でないチャンネルをまとめてアーカイブする

- active でないチャンネル一覧を取得
- botがアーカイブするチャンネルに参加
- botがアーカイブを実行

## Set up

Create slack APP: https://api.slack.com/apps

- Set scope like [manifest_sample.yml](manifest_sample.yml)
- Install to your workspace


Create `.env` file

```
# User OAuth Token
SLACK_USER_TOKEN="xoxp-XXXX"
# Bot User OAuth Token
SLACK_BOT_TOKEN="xoxb-XXXX"
```

チャンネル一覧の取得に
admin権限 ([admin.analytics.getFile](https://api.slack.com/scopes/admin.analytics:read)) を利用するため、
`SLACK_USER_TOKEN` が必要

## Usage

```bash
uv run python main.py --help
```

#### list

- 指定期間activeでないチャンネル一覧を取得
- botがチャンネルに参加

#### archive 

- botが参加しているチャンネルをアーカイブ
- 指定期間内にアクティビティがあった場合はアーカイブせずチャンネルから抜ける

#### reset

- botが参加しているチャンネルから抜ける

## Development

format with ruff

```bash
uv run ruff format | uv run ruff check
```

test

```bash
uv run pytest
```