# Anime Notify Bot

A Python Discord bot that watches airing anime and posts episode notifications to your server. It uses the AniList GraphQL API for anime data, MongoDB for subscriptions, and Discord slash commands for setup and day-to-day use.

## Features

- Subscribe a Discord channel to anime episode notifications.
- Search AniList by title or subscribe directly with an AniList anime ID.
- Automatically checks for new episodes every 30 minutes.
- Shows currently airing TV anime with scores, episode counts, next episode times, and AniList IDs.
- Lists subscribed anime per server, including the next scheduled episode.
- Tracks the latest aired episode to avoid duplicate alerts.
- Supports per-anime release offsets when an episode appears later than AniList's airing time.
- Runs a small HTTP keep-alive server for hosted environments such as Render.

## Tech Stack

- Python
- discord.py
- AniList GraphQL API
- MongoDB / PyMongo
- APScheduler
- aiohttp
- python-dotenv

## Requirements

- Python 3.10 or newer
- A Discord bot token
- A MongoDB connection string
- Internet access for Discord, MongoDB, and AniList API calls

## Setup

### 1. Clone the project

```bash
git clone https://github.com/yourusername/anime-notify-bot.git
cd anime-notify-bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a Discord bot

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application.
3. Open the **Bot** tab and create or reset the bot token.
4. Copy the token.
5. Open **OAuth2 > URL Generator**.
6. Select these scopes:
   - `bot`
   - `applications.commands`
7. Select permissions such as:
   - `Send Messages`
   - `Embed Links`
   - `Mention Everyone`
8. Open the generated URL and invite the bot to your server.

## Environment Variables

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token_here
MONGO_URI=your_mongodb_connection_string_here
```

Important: the code currently reads `MONGO_URI`, so use that exact name in your environment.

## Run the Bot

```bash
python bot.py
```

When the bot starts successfully, it syncs slash commands and starts the episode checker. The scheduler checks subscriptions every 30 minutes.

The app also starts a keep-alive web server on `PORT` if that environment variable is set, or `8080` by default.

## Slash Commands

| Command | Description |
| --- | --- |
| `/subscribe query:<title>` | Search AniList and choose an anime from a dropdown. Notifications are sent to the current channel. |
| `/subscribe anime_id:<id>` | Subscribe directly by AniList anime ID. |
| `/unsubscribe anime_id:<id>` | Remove an anime subscription from the current server. |
| `/list` | Show all anime subscriptions for the current server. |
| `/onair limit:<number>` | Show currently airing anime. Defaults to 10 and caps at 25. |
| `/episodes anime_id:<id>` | Show episode progress for an anime. |
| `/setoffset anime_id:<id> offset_minutes:<minutes>` | Delay notification checks for an anime by a set number of minutes. |

## Usage Examples

Subscribe by search:

```text
/subscribe query:Demon Slayer
```

Subscribe directly with an AniList ID:

```text
/subscribe anime_id:52991
```

See airing anime and use an ID from the result:

```text
/onair limit:10
/episodes anime_id:52991
```

Delay notifications by 30 minutes for a specific anime:

```text
/setoffset anime_id:52991 offset_minutes:30
```

Unsubscribe:

```text
/unsubscribe anime_id:52991
```

## Project Structure

```text
.
|-- bot.py              # Discord bot, slash commands, scheduler, notifications
|-- anime_checker.py    # AniList GraphQL API client and anime lookup helpers
|-- database.py         # MongoDB subscription storage
|-- keep_alive.py       # Small HTTP server for hosted deployments
|-- requirements.txt    # Python dependencies
|-- .env.example        # Example environment variables
|-- .gitignore
`-- README.md
```

## Data Storage

Subscriptions are stored in MongoDB in:

- Database: `anime_bot_db`
- Collection: `subscriptions`

Each subscription is scoped by Discord guild ID and AniList anime ID. The bot stores the Discord channel ID, anime title, latest episode seen, and offset minutes.

## Deployment Notes

- Keep `.env` private. Never commit your Discord token or MongoDB URI.
- If a token leaks, reset it immediately in the Discord Developer Portal.
- Hosted platforms should provide `DISCORD_TOKEN`, `MONGO_URI`, and optionally `PORT` as environment variables.
- The bot relies on AniList airing schedule data, so notifications may depend on how quickly AniList updates a show.
