# slack archive bot

TBD

## Set up


Create slack APP: https://api.slack.com/apps

- Set scope (TBD)
- Install to your workspace


Create `.env` file

```
# User OAuth Token
SLACK_USER_TOKEN="xoxp-XXXX"
# Bot User OAuth Token
SLACK_BOT_TOKEN="xoxb-XXXX"
```

## Usage

```bash
uv run python main.py --help
```


## Development

format with ruff

```bash
uv run ruff format | uv run ruff check
```

test

```bash
uv run pytest
```