<p align="center">
  <img src="https://telegra.ph/file/014d967eab622032e2b46.jpg" alt="Get Chat ID Bot" width="100" height="100">
</p>

# Get Chat ID Bot

Find Telegram IDs for users, bots, groups, and channels — through shared chats,
forwarded messages, usernames, contacts, and replies.

**[Try the bot](https://t.me/GetChatID_IL_BOT)** ·
[Updates](https://t.me/GetChatID_Updates) ·
[Community](https://t.me/GetChatID_Chat)

## Features

- Share users, bots, groups, or channels using the bot's selection buttons.
- Look up a username or Telegram link, and extract embedded user IDs from text,
  captions, and rich messages.
- Get IDs from forwarded messages, contacts, stories, and message replies.
- Use group commands, inline queries, guest mode, and Telegram Business integrations.
- Copy IDs and open chats through reply buttons, with configurable preferences.
- Choose from nine languages: English, Hebrew, Arabic, Russian, Simplified Chinese,
  Hindi, Spanish, French, and Azerbaijani.

The bot can only return IDs that Telegram makes available. For example, a
forwarded message with a hidden sender does not expose that sender's ID.

## Using the bot

Open the bot and send `/start`. Use the selection buttons, forward a message, or
send a username such as `@username` or a link such as `https://t.me/username`.

| Command | Purpose |
| --- | --- |
| `/start` | Show the chat and user selection buttons |
| `/me` | Get your own user ID |
| `/id` | Get the group ID, or reply to a message to identify its sender |
| `/admin` | Select a group or channel you manage |
| `/settings` | Change preferences, including copy buttons |
| `/lang` | Choose the bot's language |
| `/help` | Explore the supported ways to retrieve IDs |

## Self-hosting

Use **Python 3.13** for a local installation, or **Docker with Compose**.
The application uses [Kurigram](https://github.com/kurigram-org/kurigram) and stores
its data in SQLite.

### 1. Clone and configure

```bash
git clone https://github.com/yehuda-lev/Get_Chat_ID_Bot.git
cd Get_Chat_ID_Bot
cp .env.example .env
```

Edit `.env` and replace the placeholders. All settings below are required.

| Variable | Description |
| --- | --- |
| `TELEGRAM_API_ID` | Numeric API ID from [my.telegram.org](https://my.telegram.org) |
| `TELEGRAM_API_HASH` | API hash from the same Telegram application |
| `TELEGRAM_BOT_TOKEN` | Main bot token from [BotFather](https://t.me/BotFather) |
| `TELEGRAM_BOT_TOKEN_2` | Token for a second bot used for username searches and rate-limit fallback |
| `ADMINS` | JSON array of numeric administrator IDs, for example `[123456789, 987654321]` |
| `LIMIT_SPAM` | Per-user request threshold within a rolling 60-second window |
| `ADMIN_TO_UPDATE_OF_PAYMENT` | Numeric administrator ID that receives payment notifications |

### 2. Run locally

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, create the environment with `py -3.13 -m venv .venv` and activate it
in PowerShell with `.venv\Scripts\Activate.ps1`.

### Or run with Docker

From the configured repository directory:

```bash
docker compose up --build -d
```

View logs or stop the bot:

```bash
docker compose logs -f
docker compose down
```

The Compose configuration mounts the repository into the container. The SQLite
database (`bot_db.sqlite`), Telegram session files, and logs remain in that
folder when the container stops. Keep the database and session files when
moving or backing up an installation; do not commit them or `.env`.

## Development and checks

After setting up the Python environment, install the development tools and both
Git hooks:

```bash
python -m pip install -r requirements-dev.txt
pre-commit install
```

| When | What runs |
| --- | --- |
| Before a commit | Ruff applies safe lint fixes and formats staged Python files |
| Before a push | Ruff and pytest check the committed code in a temporary directory; failures block the push |
| On GitHub pushes and pull requests | CI runs the lint and test jobs |

If Ruff edits a file during a commit, review the changes, stage the file again,
and retry. Debug prints and debugger statements fail lint; prints are not
automatically deleted. Commit messages have no enforced format.

Run the checks manually:

```bash
# Check and format tracked files.
pre-commit run --all-files

# Check committed code in isolation, with dummy Telegram settings.
pre-commit run --hook-stage pre-push --all-files

# Test current changes using your configured development environment.
python -m pytest -q
```

Install the hooks in each clone. To require passing checks before merging for
all contributors, enable branch protection with the `Ruff` and `Pytest` checks.
See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and translation
guidelines.

## Support and license

Created by [@yehudalev](https://t.me/yehudalev).
Questions and feedback are welcome in the [community chat](https://t.me/GetChatID_Chat).

Released under the [MIT License](LICENSE).
