import os
import requests
from datetime import datetime
import feedparser

# File to store posted article links
POSTED_LOG = "posted_links.txt"
ARCHIVE_FILE = "traffic_archive.md"

# Secrets
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# RSS Source
RSS_FEED = "https://www.freepressjournal.in/feed/pune-traffic"

def fetch_traffic_news():
    """Fetch traffic news and assign severity"""
    try:
        feed = feedparser.parse(RSS_FEED)
        news_items = []
        for entry in feed.entries[:2]:
            severity = get_severity(entry.title)
            news_items.append(f"{severity} {entry.title} ({entry.link})")
        return "\n".join(news_items) if news_items else "🟢 No major updates found."
    except Exception:
        return "⚠️ Unable to fetch traffic updates."

def get_severity(title):
    """Return emoji severity based on keywords"""
    title_lower = title.lower()
    if "heavy" in title_lower or "jam" in title_lower or "closed" in title_lower:
        return "🔴"
    elif "slow" in title_lower or "congestion" in title_lower or "delay" in title_lower:
        return "🟡"
    return "🟢"

def get_weather_advisory(city="Pune"):
    """Fetch weather advisory using OpenWeather"""
    if not OPENWEATHER_API_KEY:
        return "🌤️ Weather info not available."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=10)
        data = res.json()
        condition = data["weather"][0]["main"]
        temp = data["main"]["temp"]

        if "rain" in condition.lower():
            return "☔ Monsoon Advisory: Roads may be slippery — drive cautiously!"
        elif temp > 35:
            return "🔥 Heatwave Alert: Carry water, avoid long idling in traffic."
        elif "fog" in condition.lower():
            return "🌫️ Low Visibility Advisory: Use fog lights and keep safe distance."
        else:
            return f"🌤️ Current Weather in {city}: {condition}, {temp}°C."
    except Exception:
        return "🌤️ Weather info not available."

def rotate_message():
    """Rotate between trivia, driving tips, and fun facts"""
    messages = [
        "🚗 Traffic Trivia: Istanbul drivers cross from Europe to Asia daily!",
        "🚦 Driving Tip: Maintain at least a 3-second distance from the car ahead.",
        "🛵 Fun Fact: Pune has more two-wheelers than four-wheelers combined.",
        "🚍 Public Transport Fact: London buses carry 6 million passengers daily!",
        "🚧 Safety Tip: Always slow down near pedestrian crossings.",
        "🛑 Red light rule: Don’t block zebra crossings — keep them free.",
    ]
    return messages[datetime.now().day % len(messages)]

def post_to_teams(message):
    payload = {"text": message}
    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error posting to Teams: {e}")

def archive_message(message):
    """Save to archive log (Markdown for GitHub Pages later)"""
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{message}\n")

def main():
    traffic_updates = fetch_traffic_news()
    weather_advisory = get_weather_advisory("Pune")
    trivia = rotate_message()

    message = f"""🚦 Pune Traffic Updates  
{traffic_updates}  

{weather_advisory}  
{trivia}  

📊 How was your commute today?  
🟢 Smooth | 🟡 Moderate | 🔴 Nightmare
"""

    post_to_teams(message)
    archive_message(message)

if __name__ == "__main__":
    main()
