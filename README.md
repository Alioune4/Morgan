# Morgan

**English** | [Français](README.fr.md)

Morgan is a personalized daily tech newsletter, posted to Discord.

Every day, Morgan fetches the last 24 hours of articles from RSS feeds, asks an LLM to pick and summarize the ones relevant to you, and posts the result to a Discord channel.

Your preferences (who you are, your topics, the format, your sources) live in a plain text file, `profile.md`, written however you like.

## Requirements

- Python 3.10 or newer
- A Gemini API key (free): <https://aistudio.google.com/apikey>
- A Discord server where you can add a bot

## Installation

```bash
git clone git@github.com:Alioune4/Morgan.git
cd Morgan
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
cp profile.example.md profile.md
```

## Create the Discord bot

1. Go to <https://discord.com/developers/applications> and click **New Application**.
2. In the **Bot** tab, click **Reset Token** and copy the token: this is your `DISCORD_TOKEN`.
3. In the **OAuth2 → URL Generator** tab, check the `bot` scope, then the **View Channels** and **Send Messages** permissions.
4. Open the generated URL and add the bot to your server.
5. In Discord, enable developer mode (**Settings → Advanced → Developer Mode**), then right-click the channel you want → **Copy Channel ID**: this is your `DISCORD_CHANNEL_ID`.

## Configuration

### `.env`

```
GEMINI_API_KEY=your-gemini-key
DISCORD_TOKEN=your-bot-token
DISCORD_CHANNEL_ID=your-channel-id
```

Options:

- `LLM_MODEL`: the model to use, in [LiteLLM](https://docs.litellm.ai/docs/providers) format (default `gemini/gemini-3.5-flash`). For another provider, also add its API key to `.env`.
- `PROFILE_PATH`: path to the profile (default `profile.md` at the project root).

Never commit `.env`: it is already in `.gitignore`.

### `profile.md`

This is where you personalize your newsletter. Write it freely: it is passed as-is to the LLM.

- Describe who you are (job, level, stack): the LLM uses it to judge what matters to you.
- List what interests you and what you don't want to see.
- Describe the format you want (language, length, layout).
- In the `## Sources` section, put one RSS feed URL per line. You can add a comment after the URL.

To follow a YouTube channel, use `https://www.youtube.com/feeds/videos.xml?channel_id=<channel ID>`.

`profile.md` is ignored by git, so it stays private.

## Run

To print the newsletter in the terminal without posting anything:

```bash
venv/bin/python src/main.py --dry-run
```

To post it to Discord:

```bash
venv/bin/python src/main.py
```

## Daily delivery

### With GitHub Actions (recommended)

No need to keep a machine running: the `.github/workflows/newsletter.yml` workflow runs Morgan every day at 8:00 Paris time.

1. Fork the repository.
2. In **Settings → Secrets and variables → Actions**, create these secrets, or use the `gh` CLI:

   ```bash
   gh secret set GEMINI_API_KEY
   gh secret set DISCORD_TOKEN
   gh secret set DISCORD_CHANNEL_ID
   gh secret set PROFILE < profile.md
   ```

   `PROFILE` holds your whole `profile.md`. Run the same command again whenever you change your profile.
3. Optional: to change the model, create a variable (not a secret) named `LLM_MODEL`.
4. In the **Actions** tab, enable workflows if they are disabled on your fork.
5. To test, run **Daily newsletter → Run workflow**: the `dry_run` option is checked by default, so the newsletter is printed in the logs without being posted.

GitHub may start scheduled runs a few minutes late. On a public repository with no activity for 60 days, GitHub disables scheduled workflows: re-enable them from the **Actions** tab.

To use another time zone or time, edit the `cron` lines and the `TZ` / hour check in the workflow.

### With cron

With cron (Linux, macOS or WSL), to send it every day at 8:00:

```bash
crontab -e
```

then add this line, adjusting the path:

```
0 8 * * * cd /path/to/Morgan && { echo "=== $(date)"; venv/bin/python src/main.py; } >> logs/morgan.log 2>&1
```

Create the `logs/` folder first (`mkdir logs`). Any errors will be in `logs/morgan.log`.

The time follows the machine's time zone. The machine must be on at 8:00, otherwise that day's newsletter is skipped. On WSL, the distribution must also be running, with systemd enabled (`systemd=true` in `/etc/wsl.conf`).

## Structure

```
src/
  main.py                  entry point: RSS → LLM → Discord
  user_profile.py          reads the profile and its sources
  rss/get_daily_feed.py    fetches and cleans the last 24 hours of articles
  ai/                      generates the newsletter through LiteLLM
  discord_bot/bot.py       posts to the channel, split into 2000-character messages
  contract_objects/        article data structure
```
