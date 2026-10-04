import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from ai.request_personalized_newsletter import request_personalized_newsletter
from discord_bot.bot import send_newsletter
from user_profile import get_sources, load_profile
from rss.get_daily_feed import get_daily_feed


def main():
    parser = argparse.ArgumentParser(description="Generate the daily tech newsletter and post it on Discord.")
    parser.add_argument("--dry-run", action="store_true", help="print the newsletter instead of posting it")
    args = parser.parse_args()

    profile = load_profile()
    entries = get_daily_feed(get_sources(profile))
    if not entries:
        print("No new articles in the last 24 hours, nothing to send.")
        return

    newsletter = request_personalized_newsletter(entries, profile)
    if args.dry_run:
        print(newsletter)
        return

    asyncio.run(send_newsletter(newsletter))
    print("Newsletter posted on Discord.")


if __name__ == "__main__":
    main()
