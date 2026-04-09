#!/usr/bin/env python3
"""
Pune traffic updater (enhanced):
- Multi-source RSS
- Freshness filter
- Clickable bullet links
- Baner-specific live traffic map
- Quick keyword summary
- 50 rotating Pune traffic facts (non-repeating)
- Archived output
"""

import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# ---------- CONFIG ----------
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Pune+Traffic&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.freepressjournal.in/feed/pune-traffic",
]

YOUTUBE_LINK = "https://youtube.com/@rawbyshivam?si=6Il6jMcUBHqIjWSY"

HOURS_FRESH = 24
MAX_ARTICLES = 5
POSTED_LOG = "posted_links.txt"
ARCHIVE_FILE = "traffic_archive.md"

# Baner Traffic Map (centered)
PUNE_TRAFFIC_MAP = "https://www.google.com/maps/@18.5590,73.7799,15z/data=!5m1!1e1"
PUNE_TRAFFIC_MAP_LABEL = "Baner Traffic Map"

TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# ---------- BREAKING ALERT CONFIG ----------
ALERT_KEYWORDS = [
    "heavy rain", "flood", "waterlogging",
    "accident", "crash", "collision",
    "road closed", "diversion",
    "traffic jam", "gridlock",
    "protest", "cyclist", "event"
]

ALERT_COOLDOWN_MINUTES = 90
LAST_ALERT_FILE = "last_alert.txt"

def is_regular_run_time():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)

    return now_ist.hour in [8, 16]
    
# ---------- 50-Piece Pune Fun Facts / Trivia ----------
PUNE_FACTS = [
    "🛵 Pune has more two-wheelers than any other Indian city per capita.",
    "🚴 Pune was once known as the 'Bicycle City of India'.",
    "🚦 Pune introduced India’s first smart traffic signal system.",
    "🛣 Baner Road sees peak congestion between 8:45–9:30 AM.",
    "🚗 Hinjewadi IT Park witnesses over 3 lakh commuter movements daily.",
    "🚆 Pune Metro Phase 1 will reduce heavy corridor congestion.",
    "🚧 Katraj–Dehu Bypass is Maharashtra’s busiest stretch.",
    "🏍 Pune’s two-wheeler density is among the highest in India.",
    "🌉 Holkar Bridge is one of Pune’s oldest bridges still in use.",
    "🚨 Drones help Pune Police monitor festival crowds.",
    "🅿 FC Road enforces strict no-parking zones to ease jams.",
    "🚍 PMPML runs 2000+ buses daily across Pune & PCMC.",
    "🚘 Baner–Balewadi traffic grew 40% in just 3 years.",
    "🏞 Traffic relaxes on Sinhagad Road during weekday afternoons.",
    "🚧 Metro barricades shift traffic patterns every 3–6 weeks.",
    "🚦 Pune has 260+ synchronized traffic lights.",
    "🚗 Baner Road spikes heavily during school timings.",
    "🚧 Hinjewadi–Shivajinagar Metro will cut major congestion.",
    "🛣 Pashan–Baner belt saw 30% rise in vehicles recently.",
    "🚙 Balewadi High Street jams peak after 7 PM weekends.",
    "🚓 Pune Traffic Police issue over 10,000 challans a day.",
    "🚌 Pune’s BRT was India’s first successful bus corridor system.",
    "🚗 Rickshaw peak demand is 9–11 AM & 6–8 PM.",
    "🚨 University Circle handles 1.2 lakh vehicles/day.",
    "🛣 Nal Stop flyover reduced Karve Road congestion.",
    "🚦 Traffic is lowest on Sunday mornings.",
    "🚲 Pune is building protected cycling tracks.",
    "🛵 Baner Road is among Pune’s top 10 busiest corridors.",
    "🚗 Hinjewadi Phase 3 sees surge every Monday morning.",
    "🌧 Balewadi reports the highest monsoon waterlogging.",
    "🛣 Hadapsar flyover widening will reduce jams massively.",
    "🚘 Pune-Mumbai Expressway crowds spike on Friday evenings.",
    "🚨 Ganeshotsav increases commute time by 40%.",
    "🛣 Airport Road is Pune’s fastest-growing traffic corridor.",
    "🚌 PMPML's electric bus fleet is rapidly expanding.",
    "🚗 Stadium events increase Balewadi traffic by 60%.",
    "🚧 Palkhi route diversions affect 100+ roads annually.",
    "🚨 Wakad–Shivajinagar is a high accident zone.",
    "🅿 Illegal parking is a major cause of micro-jams.",
    "🚦 Pune is testing adaptive real-time smart signals.",
    "🛵 Many Pune local lanes still follow British layouts.",
    "🚗 Deccan area traffic spikes after 6:30 PM.",
    "🌉 Karve Road’s bridges handle huge peak hour loads.",
    "🚲 More Punekars cycle on Sundays than any other day.",
    "🚌 Nagar Road is among Pune’s busiest east–west connectors.",
    "🚧 Swargate remains Pune’s most complicated junction.",
    "🚙 Commute time reduces 25% during school holidays.",
    "🚨 PMC removes over 200 encroachments monthly to ease traffic.",
    "🛵 SB Road sees early-morning jogging & cycling peak hours.",
]

# ---------- HELPERS ----------
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
        ts = entry.get(key)
        if ts:
            try:
                dt = parsedate_to_datetime(ts)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    return None

def get_severity(title):
    t = title.lower()
    if any(k in t for k in ("heavy", "jam", "blocked", "closed", "accident", "crash", "diversion")):
        return "🔴"
    if any(k in t for k in ("slow", "delay", "snarl", "congestion", "waterlogging")):
        return "🟡"
    return "🟢"

def fetch_and_merge_feeds():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_FRESH)
    items, seen = [], set()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            link = e.get("link")
            if not link or link in seen:
                continue
            seen.add(link)

            title = e.get("title", "").strip()
            published = parse_entry_date(e) or datetime.now(timezone.utc)
            if published < cutoff:
                continue

            items.append({"title": title, "link": link, "published": published})

    return sorted(items, key=lambda x: x["published"], reverse=True)

def is_breaking_news(title):
    t = title.lower()
    return any(k in t for k in ALERT_KEYWORDS)

def can_send_alert():
    if not os.path.exists(LAST_ALERT_FILE):
        return True

    try:
        with open(LAST_ALERT_FILE, "r") as f:
            last_time = datetime.fromisoformat(f.read().strip())
        now = datetime.now()
        diff = (now - last_time).total_seconds() / 60
        return diff > ALERT_COOLDOWN_MINUTES
    except:
        return True

def update_last_alert_time():
    with open(LAST_ALERT_FILE, "w") as f:
        f.write(datetime.now().isoformat())

def prepare_alert_message(items):
    header = "🚨 BREAKING TRAFFIC ALERT 🚨\n\n"

    lines = []
    for it in items[:3]:
        link = f"[{it['title']}]({it['link']})"
        lines.append(f"• 🔴 {link}")

    footer = "\n\n⚠️ Please plan your travel accordingly."

    return header + "\n".join(lines) + footer

# ---------- SUMMARY ----------
def generate_quick_summary(headlines):
    text = " ".join(headlines).lower()

    if any(w in text for w in ("baner", "balewadi", "aundh")):
        return "🔍 Summary: Expect congestion around Baner–Balewadi area."
    if any(w in text for w in ("navale", "bridge", "accident", "crash")):
        return "🔍 Summary: Possible delays near Navale Bridge."
    if any(w in text for w in ("metro", "construction", "work", "repair")):
        return "🔍 Summary: Roadwork/metro construction slowing traffic."
    if any(w in text for w in ("jam", "standstill", "gridlock")):
        return "🔍 Summary: Heavy congestion reported at multiple points."

    return "🔍 Summary: No major bottlenecks this hour."

# ---------- ROTATION ----------
def rotate_message():
    idx = datetime.now().day % len(PUNE_FACTS)
    return PUNE_FACTS[idx]

def creator_spotlight():
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    h = now_ist.hour

    # Only show in morning update (8–9 AM IST)
    if 8 <= h < 9:
        return f"🎥 Creator Spotlight: Support Pune-based YouTube creator!\n{YOUTUBE_LINK}"

    return ""


# ---------- GREETING ----------
def ist_greeting():
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    if 8 <= now.hour < 9:
        return "🌅 Good morning Pune!"
    if 16 <= now.hour < 17:
        return "🌇 Evening traffic update — plan ahead!"
    return None

# ---------- MESSAGE ----------
def prepare_message(new_items):
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")

    header = f"🚦 Pune Traffic Updates • {timestamp}\n"
    greet = ist_greeting()
    if greet:
        header += f"{greet}\n\n"
    else:
        header += "\n"

    if not new_items:
        summary = generate_quick_summary([])
        return (
            f"{header}🟢 No major updates found.\n\n"
            f"{summary}\n\n"
            f"🗺️ Live Map: [{PUNE_TRAFFIC_MAP_LABEL}]({PUNE_TRAFFIC_MAP})\n\n"
            f"{rotate_message()}"
        )

    titles = []
    lines = []
    for it in new_items[:MAX_ARTICLES]:
        sev = get_severity(it["title"])
        link = f"[{it['title']}]({it['link']})"
        lines.append(f"• {sev} {link}")
        titles.append(it["title"])

    extra = ""
    if len(new_items) > MAX_ARTICLES:
        extra = f"\n\n...and {len(new_items) - MAX_ARTICLES} more updates. Stay tuned!"

    summary = generate_quick_summary(titles)

    # -------- FIXED INDENTATION BELOW --------
    footer = (
        f"\n\n🗺️ Live Map: [{PUNE_TRAFFIC_MAP_LABEL}]({PUNE_TRAFFIC_MAP})"
        f"\n\n{rotate_message()}"
    )

    creator_msg = creator_spotlight()
    if creator_msg:
        footer += f"\n\n{creator_msg}"

    return header + "\n".join(lines) + extra + "\n\n" + summary + footer



# ---------- SEND ----------
def post_to_teams(message):
    if not TEAMS_WEBHOOK_URL:
        print("TEAMS_WEBHOOK_URL missing — printing message:")
        print(message)
        return

    formatted = message.replace("\n", "\n\n")  # 👈 Fix Teams formatting

    try:
        resp = requests.post(TEAMS_WEBHOOK_URL, json={"text": formatted}, timeout=10)
        resp.raise_for_status()
        print("Posted to Teams:", resp.status_code)
    except Exception as e:
        print("Error posting:", e)

# ---------- ARCHIVE ----------
def archive_message(message):
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write("\n### " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write(message + "\n")

# ---------- MAIN ----------
def main():
    posted = load_posted_links()
    merged = fetch_and_merge_feeds()

    new_items = [it for it in merged if it["link"] not in posted]

    # 🚨 BREAKING ALERT
    breaking_items = [it for it in new_items if is_breaking_news(it["title"])]

    if breaking_items and can_send_alert():
        alert_msg = prepare_alert_message(breaking_items)
        post_to_teams(alert_msg)
        update_last_alert_time()

    # ✅ REGULAR UPDATE
    if is_regular_run_time():
        message = prepare_message(merged)
        post_to_teams(message)
        archive_message(message)

        mark_as_posted([it["link"] for it in merged[:MAX_ARTICLES]])


if __name__ == "__main__":
    main()



