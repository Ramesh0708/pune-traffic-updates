import os
import requests
import feedparser
import random
import datetime

# RSS Feed URL for "Pune Traffic" from Google News
RSS_FEED_URL = "https://news.google.com/rss/search?q=Pune+traffic&hl=en-IN&gl=IN&ceid=IN:en"

# Webhook URL from GitHub Secrets or local testing\WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# File to store posted article links
POSTED_LOG = "posted_links.txt"

# Sample trivia list (used if trivia API fails)
TRIVIA_LIST = [
    "New York’s Times Square was once a major traffic intersection!",
    "Delhi has one of the world’s highest car densities!",
    "Drivers in Bengaluru waste nearly 243 hours/year in traffic.",
    "In Tokyo, pedestrians cross from all sides at once at Shibuya crossing.",
    "In Venice, traffic is managed on canals, not roads!"
]

def has_been_posted(url):
    if not os.path.exists(POSTED_LOG):
        return False
    with open(POSTED_LOG, "r") as file:
        return url.strip() in file.read().splitlines()

def mark_as_posted(url):
    with open(POSTED_LOG, "a") as file:
        file.write(url + "\n")

def get_new_traffic_updates():
    feed = feedparser.parse(RSS_FEED_URL)
    new_items = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link

        if not has_been_posted(link):
            new_items.append({"title": title, "link": link})
            mark_as_posted(link)

    return new_items

def get_random_trivia():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
        if response.status_code == 200:
            return response.json().get("text", random.choice(TRIVIA_LIST))
    except:
        pass
    return random.choice(TRIVIA_LIST)

def send_teams_message(message):
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL is not set. Cannot send message.")
        return

    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print("✅ Message sent successfully.")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")

def main():
    print("🔄 Checking for new traffic updates...")
    updates = get_new_traffic_updates()

    message = "🚦 **Pune Traffic Updates**\n"

    if updates:
        for item in updates:
            message += f"\n• 📰 [{item['title']}]({item['link']})"
    else:
        message += "\n• No new traffic updates at the moment."

    # Add monsoon advisory
    message += "\n\n☔ **Monsoon Advisory:** Roads may be slippery — drive cautiously and allow extra travel time!"

    # Add traffic trivia
    trivia = get_random_trivia()
    message += f"\n🚗 **Traffic Trivia of the Day:** {trivia}"

    send_teams_message(message)

if __name__ == "__main__":
    main()
