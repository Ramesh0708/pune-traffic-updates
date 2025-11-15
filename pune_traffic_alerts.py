#!/usr/bin/env python3
"""
Improved Pune traffic updater:
- Multi-source RSS
- Freshness filter (last N hours)
- Clickable titles for Teams
- Dedupe using posted_links.txt
- Archive messages to traffic_archive.md
"""

import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# Config
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Pune+Traffic&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.freepressjournal.in/feed/pune-traffic",
    # Add more RSS URLs here if you want
]
HOURS_FRESH = 24          # consider only articles published in the last N hours
MAX_ARTICLES = 5          # how many headlines to show in Teams
POSTED_LOG = "posted_links.txt"
ARCHIVE_FILE = "traffic_archive.md"

# Teams webhook (set as GitHub secret TEAMS_WEBHOOK_URL and passed into the workflow)
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

if not TEAMS_WEBHOOK_URL:
    print("ERROR: TEAMS_WEBHOOK_URL is not set. Add the webhook URL as an environment variable / secret.")
    # continue so local runs can still be tested if user wants; but exits to avoid exceptions
    # exit(1)

def load_posted_links():
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def mark_as_posted(urls):
    if not urls:
        return
    with open(POSTED_LOG, "a", encoding="utf-8") as f:
        for u in urls:
            f.write(u.strip() + "\n")

def parse_entry_date(entry):
    """Return a timezone-aware datetime for the entry if available, otherwise None."""
    # try common fields in order
    for key in ("published", "updated", "pubDate"):
        val = entry.get(key)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None:
                    # assume UTC if no tz
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    # feedparser provides published_parsed often
    if entry.get("published_parsed"):
        try:
            dt = datetime.fromtimestamp(feedparser.mktime_tz(entry.published_parsed), tz=timezone.utc)
            return dt
        except Exception:
            pass
    return None

def get_severity(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("heavy", "jam", "blocked", "closed", "accident", "collapse", "diversion")):
        return "🔴"
    if any(k in t for k in ("slow", "congestion", "delay", "waterlogging", "snarl")):
        return "🟡"
    return "🟢"

def fetch_and_merge_feeds(hours_fresh=HOURS_FRESH):
    """Fetch multiple feeds, merge, filter by recency and return sorted list of unique entries."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_fresh)
    items = []
    seen_links = set()
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue
        for e in feed.entries:
            link = e.get("link") or e.get("guid") or ""
            if not link:
                # try id or alternate
                link = e.get("id", "")
            if not link:
                continue
            if link in seen_links:
                continue
            seen_links.add(link)

            title = e.get("title", "").strip()
            published = parse_entry_date(e) or datetime.now(timezone.utc)
            # filter by recency
            if published < cutoff:
                continue
            items.append({
                "title": title,
                "link": link,
                "published": published
            })

    # sort newest first
    items.sort(key=lambda x: x["published"], reverse=True)
    return items

def prepare_message(new_items):
    """Create a Markdown-friendly Teams message from the list of items."""
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")
    header = f"🚦 Pune Traffic Updates • {timestamp}\n\n"

    if not new_items:
        return header + "🟢 No major updates found."

    lines = []
    for i, it in enumerate(new_items[:MAX_ARTICLES], start=1):
        sev = get_severity(it["title"])
        # use markdown link so titles are clickable in Teams
        title_md = f"[{it['title']}]({it['link']})"
        lines.append(f"{sev} {title_md}")

    extra = ""
    if len(new_items) > MAX_ARTICLES:
        extra = f"\n\n...and {len(new_items) - MAX_ARTICLES} more updates. Stay tuned!"

    # Rotate message (trivia/tip)
    tip = rotate_message()

    body = "\n\n".join(lines)
    message = f"{header}{body}{extra}\n\n{tip}"
    return message

def rotate_message():
    messages = [
        "🚗 Traffic Trivia: Istanbul drivers cross from Europe to Asia daily!",
        "🚦 Driving Tip: Maintain at least a 3-second distance from the car ahead.",
        "🛵 Fun Fact: Pune has more two-wheelers than four-wheelers combined.",
        "🚍 Public Transport Fact: London buses carry 6 million passengers daily!",
        "🚧 Safety Tip: Always slow down near pedestrian crossings.",
        "🛑 Red light rule: Don’t block zebra crossings — keep them free.",
    ]
    idx = datetime.now().day % len(messages)
    return messages[idx]

def post_to_teams(message):
    if not TEAMS_WEBHOOK_URL:
        print("Warning: TEAMS_WEBHOOK_URL not set — would have posted:\n")
        print(message)
        return

    payload = {"text": message}
    try:
        resp = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=15)
        resp.raise_for_status()
        print("Posted to Teams (status):", resp.status_code)
    except Exception as exc:
        print("Error posting to Teams:", exc)
        # do not raise, so archive still happens

def archive_message(message):
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write("\n### " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write(message + "\n")

def main():
    posted = load_posted_links()
    merged = fetch_and_merge_feeds()
    # remove items that were posted already
    new_items = [it for it in merged if it["link"] not in posted]

    if not new_items:
        message = f"🚦 Pune Traffic Updates • {datetime.now().strftime('%d %b %Y • %I:%M %p')}\n\n🟢 No major updates found."
        post_to_teams(message)
        archive_message(message)
        return

    message = prepare_message(new_items)
    post_to_teams(message)
    archive_message(message)

    # mark top MAX_ARTICLES URLs as posted (so they won't repeat)
    urls_to_mark = [it["link"] for it in new_items[:MAX_ARTICLES]]
    mark_as_posted(urls_to_mark)
    print("Marked posted links:", len(urls_to_mark))

if __name__ == "__main__":
    main()
