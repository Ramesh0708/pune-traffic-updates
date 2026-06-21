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

ALERT_COOLDOWN_MINUTES = 240
LAST_ALERT_FILE = "last_alert.txt"

def is_regular_run_time():
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    return now_ist.hour in [9, 13, 17, 21]
    
# ---------- 50-Piece Pune Fun Facts / Trivia ----------
PUNE_FACTS = [
"Pune traffic slows down significantly near IT hubs during shift change hours.",
"Hinjewadi Phase 1 sees peak congestion between 9 AM and 11 AM on weekdays.",
"Baner Road traffic increases sharply during evening office return hours.",
"Wakad junction is one of the most congestion-prone areas in Pune.",
"Kharadi IT Park contributes heavily to peak-hour traffic density.",
"University Circle handles one of the highest vehicle volumes daily.",
"Heavy rainfall often leads to waterlogging near Balewadi High Street.",
"Pune’s road infrastructure struggles to keep pace with rapid vehicle growth.",
"Metro construction zones frequently cause temporary traffic diversions.",
"School zones contribute significantly to morning traffic spikes.",
"Weekend traffic near malls and cafes increases in areas like Viman Nagar.",
"Hadapsar experiences major traffic buildup during industrial shift hours.",
"Pune’s narrow internal roads add to congestion in old city areas.",
"Traffic near Pune Railway Station remains heavy throughout the day.",
"Airport Road sees increased traffic during early morning and late evening flights.",
"Signal synchronization issues often contribute to delays at major junctions.",
"Two-wheelers dominate Pune traffic, especially during peak hours.",
"Traffic police frequently manage congestion manually at busy intersections.",
"Unauthorized parking is a leading cause of traffic slowdowns.",
"Pune’s ring road project aims to reduce city congestion in future.",
"Swargate remains one of Pune’s busiest and most complex junctions.",
"Karve Road sees consistent traffic pressure throughout the day.",
"SB Road experiences high traffic due to commercial activity.",
"Deccan area traffic peaks during evening leisure hours.",
"Pashan-Sus Road traffic has increased due to rapid urbanization.",
"Balewadi Stadium events significantly impact nearby traffic flow.",
"Pune’s public transport usage is still lower than private vehicle usage.",
"Metro Phase 1 aims to ease congestion on key city corridors.",
"Traffic congestion increases by up to 30% during monsoon season.",
"Auto-rickshaw demand peaks during office commute hours.",
"Pune traffic is heavily influenced by IT park shift timings.",
"Camp area roads experience high pedestrian and vehicle interaction.",
"Nal Stop junction is a critical traffic point in west Pune.",
"Warje bridge handles heavy inbound traffic during mornings.",
"Traffic near Magarpatta City increases during corporate hours.",
"Pune roads often face bottlenecks at signal-heavy stretches.",
"Illegal U-turns are a common cause of traffic disruption.",
"Pune traffic flow reduces significantly during festival processions.",
"Vehicle density in Pune is among the highest in India.",
"Pune experiences traffic surges during long weekends.",
"Expressway traffic spillover affects city routes during peak travel days.",
"Traffic diversions during roadwork create temporary congestion hotspots.",
"High vehicle ownership contributes to daily traffic challenges.",
"Pune traffic is less dense on Sunday mornings compared to weekdays.",
"Morning joggers and cyclists occupy lanes in certain areas early in the day.",
"Traffic increases sharply during school reopening periods.",
"Public transport delays sometimes add to road congestion.",
"Traffic signals at major junctions often experience overload.",
"Peak hour traffic speeds can drop below 20 km/h.",
"Traffic congestion impacts fuel consumption significantly.",
"Construction activities often reduce usable road width.",
"Pune’s road network includes many legacy narrow streets.",
"Traffic near IT hubs is highly time-dependent.",
"Parking violations are common in commercial areas.",
"Traffic police interventions help manage sudden congestion spikes.",
"Road accidents often lead to temporary traffic disruptions.",
"Traffic increases near shopping areas during festive seasons.",
"Pune’s urban growth continues to pressure road infrastructure.",
"Traffic congestion varies significantly by time of day.",
"Even minor incidents can cause ripple effects in traffic flow.",
"Traffic near bus depots increases during departure times.",
"Pune’s outer areas are seeing rising traffic due to expansion.",
"Traffic congestion is lower during major holidays.",
"Traffic signals play a key role in regulating flow.",
"Metro expansion is expected to ease traffic in coming years.",
"Heavy vehicles contribute to congestion during daytime.",
"Traffic diversions are common during infrastructure upgrades.",
"Pune traffic conditions can change rapidly within hours.",
"Traffic near educational institutions spikes during entry and exit times.",
"Congestion levels vary across different city zones.",
"Traffic patterns differ significantly between weekdays and weekends.",
"Peak congestion zones are mostly near commercial hubs.",
"Traffic flow improves during late-night hours.",
"Pune’s road capacity is often exceeded during peak times.",
"Traffic density increases during rainy weather conditions.",
"Traffic near industrial areas peaks during shift changes.",
"Traffic bottlenecks are common at flyover entry and exit points.",
"Traffic signals sometimes cause backlogs during peak hours.",
"Pune traffic is influenced by both local and highway movements.",
"Traffic congestion impacts daily commute times significantly.",
"Traffic flow improves during school vacation periods.",
"Traffic near hospitals increases during visiting hours.",
"Traffic congestion is a major urban challenge in Pune.",
"Traffic delays are common during infrastructure upgrades.",
"Traffic near markets increases during evening hours.",
"Traffic in Pune varies greatly across different zones.",
"Traffic congestion is highest in central Pune areas.",
"Traffic slows down significantly during heavy rainfall.",
"Traffic near malls increases during weekends.",
"Traffic congestion affects overall productivity.",
"Traffic patterns are constantly evolving with city growth.",
"Traffic near tech parks is highly predictable.",
"Traffic congestion peaks during office commute hours.",
"Traffic density reduces during early morning hours.",
"Traffic near flyovers can become bottleneck points.",
"Traffic is lighter during late-night hours.",
"Traffic congestion in Baner increases significantly during peak office hours.",
"Wakad experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Hinjewadi during monsoon conditions.",
"Kharadi sees improved traffic flow during early morning hours.",
"Evening rush hours in Hadapsar often lead to extended travel times.",
"Viman Nagar roads are heavily impacted during festival days.",
"Traffic near Aundh slows down due to signal-heavy intersections.",
"Pashan witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Balewadi is influenced by shopping and dining activity.",
"Swargate often faces congestion due to ongoing infrastructure work.",
"Traffic in Deccan becomes unpredictable during sudden weather changes.",
"Karve Road junctions are key congestion points during daily commutes.",
"Road capacity in Hinjewadi is often exceeded during rush hours.",
"Kharadi experiences slower traffic speeds during school timings.",
"Traffic congestion in Hadapsar impacts fuel efficiency for commuters.",
"Viman Nagar roads are prone to temporary jams due to parking violations.",
"Traffic density in Aundh has increased with urban expansion.",
"Pashan experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Balewadi increases significantly during peak office hours.",
"Swargate experiences frequent bottlenecks due to high vehicle density.",
"Aundh experiences traffic fluctuations based on IT park schedules."
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
    for it in items[:1]:
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
    seen_titles = set()
    breaking_items = []

    for it in merged:
        key = it["title"].lower().split(" - ")[0].strip()

        if (
            key not in seen_titles and
            is_breaking_news(it["title"]) and
            it["link"] not in posted
        ):
            seen_titles.add(key)
            breaking_items.append(it)

    if breaking_items and can_send_alert():
        alert_msg = prepare_alert_message(breaking_items)
        post_to_teams(alert_msg)
        update_last_alert_time()

        mark_as_posted([it["link"] for it in breaking_items[:1]])

    # DEBUG LOGS
    print("Current IST hour:", datetime.now(timezone.utc) + timedelta(hours=5, minutes=30))
    print("Regular update allowed:", is_regular_run_time())
    print("Breaking items found:", len(breaking_items))
    print("New items found:", len(new_items))

    # ✅ REGULAR UPDATE
    if is_regular_run_time():
        message = prepare_message(new_items)
        post_to_teams(message)
        archive_message(message)

        mark_as_posted([it["link"] for it in new_items[:MAX_ARTICLES]])

if __name__ == "__main__":
    main()

   if __name__ == "__main__":
     main()
