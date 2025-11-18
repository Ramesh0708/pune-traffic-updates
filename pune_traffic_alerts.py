#!/usr/bin/env python3
"""
Pune traffic updater (updated):
- Multi-source RSS
- Freshness filter
- Clickable titles for Teams
- Dedupe using posted_links.txt
- Archive messages to traffic_archive.md
- Baner-specific live map link
- Quick keyword-based summary (generate_quick_summary)
"""

import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re

# ---------- CONFIG ----------
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Pune+Traffic&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.freepressjournal.in/feed/pune-traffic",
    # add other RSS feeds if you like
]
HOURS_FRESH = 24
MAX_ARTICLES = 5
POSTED_LOG = "posted_links.txt"
ARCHIVE_FILE = "traffic_archive.md"

# Baner-specific traffic map (traffic layer enabled, centered on Baner)
PUNE_TRAFFIC_MAP = "https://www.google.com/maps/@18.5590,73.7799,15z/data=!5m1!1e1"
PUNE_TRAFFIC_MAP_LABEL = "Baner Traffic Map"

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# ---------- UTILITIES ----------
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
    for key in ("published", "updated", "pubDate"):
        val = entry.get(key)
        if val:
            try:
                dt = parsedate_to_datetime(val)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    if entry.get("published_parsed"):
        try:
            dt = datetime.fromtimestamp(feedparser.mktime_tz(entry.published_parsed), tz=timezone.utc)
            return dt
        except Exception:
            pass
    return None

def get_severity(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("heavy", "jam", "blocked", "closed", "accident", "collapse", "diversion", "crash")):
        return "🔴"
    if any(k in t for k in ("slow", "congestion", "delay", "waterlogging", "snarl")):
        return "🟡"
    return "🟢"

def fetch_and_merge_feeds(hours_fresh=HOURS_FRESH):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_fresh)
    items = []
    seen_links = set()
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
        except Exception:
            continue
        for e in feed.entries:
            link = e.get("link") or e.get("guid") or e.get("id") or ""
            if not link:
                continue
            if link in seen_links:
                continue
            seen_links.add(link)
            title = e.get("title", "").strip()
            published = parse_entry_date(e) or datetime.now(timezone.utc)
            if published < cutoff:
                continue
            items.append({"title": title, "link": link, "published": published})
    items.sort(key=lambda x: x["published"], reverse=True)
    return items

# ---------- QUICK KEYWORD-BASED SUMMARY ----------
def generate_quick_summary(headlines):
    """
    headlines: list of strings (titles)
    returns a short one-line summary based on keywords.
    """
    text = " ".join(headlines).lower()
    # priority rules
    if any(w in text for w in ["baner", "baner road", "aundh-baner", "balewadi"]):
        return "🔍 Summary: Expect congestion around Baner & Balewadi — plan extra travel time."
    if any(w in text for w in ["navale", "navale bridge", "bridge", "accident", "crash"]):
        return "🔍 Summary: Delays likely near Navale Bridge due to reported incidents."
    if any(w in text for w in ["hinjewadi", "it park", "phase", "traffic police implement"]):
        return "🔍 Summary: Slow-moving traffic expected near Hinjewadi IT Park."
    if any(w in text for w in ["metro", "construction", "roadwork", "work"]):
        return "🔍 Summary: Roadworks/metro construction causing local slowdowns — expect delays."
    if any(w in text for w in ["heavy", "gridlock", "jam", "standstill"]):
        return "🔍 Summary: Heavy congestion reported in multiple locations."
    # default
    return "🔍 Summary: No major bottlenecks reported in the immediate area."

# ---------- MESSAGE PREP & POST ----------
def rotate_message():
    messages = [
        "🚗 Traffic Trivia: Istanbul drivers cross from Europe to Asia daily!",
        "🚦 Driving Tip: Maintain at least a 3-second distance from the car ahead.",
        "🛵 Fun Fact: Pune has more two-wheelers than four-wheelers combined.",
        "🚧 Safety Tip: Always slow down near pedestrian crossings.",
        "🛑 Red light rule: Don’t block zebra crossings — keep them free.",
    ]
    idx = datetime.now().day % len(messages)
    return messages[idx]

def ist_greeting():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    h = now_ist.hour
    if 8 <= h < 9:
        return "🌅 Good morning Pune! Here's the morning traffic pulse."
    if 16 <= h < 17:
        return "🌇 Evening traffic update — plan your commute!"
    return None

def prepare_message(new_items):
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")
    header_parts = [f"🚦 Pune Traffic Updates • {timestamp}"]
    greeting = ist_greeting()
    if greeting:
        header_parts.append(greeting)
    header = "\n".join(header_parts) + "\n\n"

    if not new_items:
        body = "🟢 No major updates found."
        summary = generate_quick_summary([])
        footer = f"\n\n🗺️ Live Map: [{PUNE_TRAFFIC_MAP_LABEL}]({PUNE_TRAFFIC_MAP})\n\n{rotate_message()}"
        return header + body + "\n\n" + summary + footer

    # top headlines, clickable and bulleted
    lines = []
    titles_for_summary = []
    for it in new_items[:MAX_ARTICLES]:
        sev = get_severity(it["title"])
        title_md = f"[{it['title']}]({it['link']})"
        lines.append(f"• {sev} {title_md}")
        titles_for_summary.append(it["title"])

    extra = ""
    if len(new_items) > MAX_ARTICLES:
        extra = f"\n\n...and {len(new_items) - MAX_ARTICLES} more updates. Stay tuned!"

    body = "\n".join(lines)
    summary = generate_quick_summary(titles_for_summary)
    footer = f"\n\n🗺️ Live Map: [{PUNE_TRAFFIC_MAP_LABEL}]({PUNE_TRAFFIC_MAP})\n\n{rotate_message()}"
    return header + body + extra + "\n\n" + summary + footer

def post_to_teams(message):
    if not TEAMS_WEBHOOK_URL:
        print("Warning: TEAMS_WEBHOOK_URL not set — message preview:\n")
        print(message)
        return
    payload = {"text": message}
    try:
        resp = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=15)
        resp.raise_for_status()
        print("Posted to Teams:", resp.status_code)
    except Exception as exc:
        print("Error posting to Teams:", exc)

def archive_message(message):
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write("\n### " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write(message + "\n")

# ---------- MAIN ----------
def main():
    posted = load_posted_links()
    merged = fetch_and_merge_feeds()
    new_items = [it for it in merged if it["link"] not in posted]

    if not new_items:
        message = prepare_message([])
        post_to_teams(message)
        archive_message(message)
        return

    message = prepare_message(new_items)
    post_to_teams(message)
    archive_message(message)

    urls_to_mark = [it["link"] for it in new_items[:MAX_ARTICLES]]
    mark_as_posted(urls_to_mark)
    print("Marked posted links:", len(urls_to_mark))

if __name__ == "__main__":
    main()
