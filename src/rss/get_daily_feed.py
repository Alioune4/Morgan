from datetime import datetime, timedelta, timezone
from html import unescape
from time import mktime
from typing import List
import re

import feedparser

from contract_objects.ai_daily_input import RSSEntryEssentials


MAX_TEXT_LENGTH = 1000


def get_daily_feed(links: List[str]):
     daily_feed = []
     since = datetime.now(timezone.utc) - timedelta(days=1)
     for link in links:
          feed = feedparser.parse(link)
          if not feed.entries:
               print(f"Feed unavailable (status {feed.get('status')}): {link}")
               continue

          kept = 0
          for entry in feed.entries:
               published_parsed = entry.get("published_parsed")
               if published_parsed is None:
                    continue
               published_date = datetime.fromtimestamp(mktime(published_parsed), timezone.utc)
               if published_date < since:
                    continue

               summary_for_ai = get_entry_essentials(entry, published_date)
               if summary_for_ai is not None:
                    daily_feed.append(summary_for_ai)
                    kept += 1
          print(f"{kept}/{len(feed.entries)} entries kept from {link}")

     return daily_feed


def get_entry_essentials(entry: feedparser.FeedParserDict, published_date: datetime):
     try:
          content = entry.get("content")
          return RSSEntryEssentials(
               entry.get("id", entry.link),
               entry.link,
               published_date,
               entry.title,
               author=entry.get("author"),
               content=clean_text(content[0].get("value")) if content else None,
               summary=clean_text(entry.get("summary")),
               tags=[tag.term for tag in entry.get("tags", []) if tag.get("term")] or None,
          )
     except AttributeError as e:
          print(f"Skipped (missing field): {e}")
          return None


def clean_text(html: str | None) -> str | None:
     if not html:
          return None
     text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()
     return text[:MAX_TEXT_LENGTH] or None
