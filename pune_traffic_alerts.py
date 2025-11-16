#!/usr/bin/env python3
"""
Pune traffic updater — enhanced:
- multi-source RSS
- freshness filter
- clickable titles
- lightweight article summary (1-2 sentences) using BeautifulSoup
- Pune traffic map link in footer
- time-based greeting for morning/evening (IST)
- dedupe & archive
"""

import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
import re

# ---------- CONFIG ----------
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Pune+Traffic&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.freepressjournal.in/feed/pune-traffic",
    # add more feeds if desired
]
HOURS_FRESH = 24
MAX_ARTICLES = 5
MAX_SUMMARIES = 2         # number of top articles to fetch a short summary for
POSTED_LOG = "posted_links.txt"
ARCHIVE_FILE = "traffic_archive.md"

# Map link (users can click for a live traffic view)
PUNE_TRAFFIC_MAP = "https://www.google.com/maps/search/traffic+Pune"  # simple helpful link

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

# lightweight text cleaning
def clean_text(s):
    return re.sub(r"\s+", " ", s).strip()

# fetch a short summary (1-2 sentences) by reading the article <p> text
def fetch_short_summary(url, max_sentences=2):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; PuneTrafficBot/1.0)"}
        r = requests.get(url, headers=headers, timeout=8)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # prefer article tag paragraphs if present
        article_text = []
        article_tag = soup.find("article")
        if article_tag:
            ps = article_tag.find_all("p")
        else:
            ps = soup.find_all("p")
        for p in ps:
            txt = p.get_text(separator=" ", strip=True)
            if txt:
                article_text.append(txt)
        if not article_text:
            return None
        joined = " ".join(article_text)
        joined = clean_text(joined)
        # split into sentences (naive)
        sentences = re.split(r'(?<=[.!?])\s+', joined)
        # return first max_sentences non-empty sentences
        selected = [s for s in sentences if s][:max_sentences]
        summary = " ".join(selected).strip()
        # limit length to keep Teams message tidy
        if len(summary) > 350:
            summary = summary[:347].rsplit(" ", 1)[0] + "..."
        return summary
    except Exception:
        return None

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

def ist_greeting():
    # IST is UTC+5:30
    now_utc = datetime.now(timezone.utc)
    now_ist = (now_utc + timedelta(hours=5, minutes=30))
    h = now_ist.hour
    # morning window 08:00-09:00, evening 16:00-17:00 (adjustable)
    if 8 <= h < 9:
        return "🌅 Good morning Pune! Here's the morning traffic pulse."
    if 16 <= h < 17:
        return "🌇 Evening traffic update — plan your commute!"
    return None

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

def prepare_message(new_items):
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")
    header_parts = [f"🚦 Pune Traffic Updates • {timestamp}"]
    greeting = ist_greeting()
    if greeting:
        header_parts.append(greeting)
    header = "\n".join(header_parts) + "\n\n"

    if not new_items:
        body = "🟢 No major updates found."
        footer = f"\n\n🗺️ Live Map: {PUNE_TRAFFIC_MAP}\n\n{rotate_message()}"
        return header + body + footer

    lines = []
    # include summaries only for top N articles to limit message size
    summaries = {}
    for it in new_items[:MAX_SUMMARIES]:
        s = fetch_short_summary(it["link"], max_sentences=2)
        if s:
            summaries[it["link"]] = s

    for it in new_items[:MAX_ARTICLES]:
        sev = get_severity(it["title"])
        title_md = f"[{it['title']}]({it['link']})"
        line = f"{sev} {title_md}"
        # attach tiny summary inline (italic) if available
        summary = summaries.get(it["link"])
        if summary:
            line += f"\n_ {summary} _"
        lines.append(line)

    extra = ""
    if len(new_items) > MAX_ARTICLES:
        extra = f"\n\n...and {len(new_items) - MAX_ARTICLES} more updates. Stay tuned!"

    body = "\n\n".join(lines)
    footer = f"\n\n🗺️ Live Map: {PUNE_TRAFFIC_MAP}\n\n{rotate_message()}"
    return header + body + extra + footer

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
    # mark top MAX_ARTICLES URLs as posted
    urls_to_mark = [it["link"] for it in new_items[:MAX_ARTICLES]]
    mark_as_posted(urls_to_mark)
    print("Marked posted links:", len(urls_to_mark))

if __name__ == "__main__":
    main()
