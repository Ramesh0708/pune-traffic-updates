import os
import requests
import feedparser
import random
from datetime import datetime

# RSS Feed URL for "Pune Traffic" from Google News
RSS_FEED_URL = "https://news.google.com/rss/search?q=Pune+traffic&hl=en-IN&gl=IN&ceid=IN:en"

# Webhook URL from environment variable (GitHub secret)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# File to store posted article links
POSTED_LOG = "posted_links.txt"

# List of traffic trivia
TRAFFIC_TRIVIA = [
    "Delhi has one of the world’s highest car densities!",
    "Bengaluru drivers waste over 243 hours/year in traffic.",
    "Shibuya crossing in Tokyo sees 2,500+ people cross at once!",
    "New York’s Times Square was once a major traffic intersection!",
    "Los Angeles has more cars than people!",
    "Mumbai’s traffic is slower than a walking elephant in peak hours!",
    "The world’s longest traffic jam was over 100 km long in China!",
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
            new_items.append({'title': title, 'link': link})
            mark_as_posted(link)

    return new_items

def get_monsoon_advisory():
    return "☔ *Monsoon Advisory*: Roads may be slippery — drive cautiously and allow extra travel time!"

def get_random_trivia():
    return f"🚗 *Traffic Trivia of the Day*: {random.choice(TRAFFIC_TRIVIA)}"

def send_teams_message(message):
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL is not defined.")
        return

    # Replace single line breaks with double to improve formatting in Teams
    formatted_message = message.replace("\n", "\n\n")

    payload = {"text": formatted_message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print("✅ Message sent successfully.")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")


def main():
    print("🔄 Checking for new traffic updates...")
    updates = get_new_traffic_updates()

    message = "🚦 **Pune Traffic Updates**"

    if updates:
        max_articles = 5
        displayed_updates = updates[:max_articles]

        news_section = "\n".join([f"• [{item['title']}]({item['link']})" for item in displayed_updates])
        message += "\n" + news_section

        if len(updates) > max_articles:
            message += f"\n\n...and {len(updates) - max_articles} more updates. Stay tuned!"
    else:
        message += "\nNo new traffic updates at the moment."

    message += f"\n\n{get_monsoon_advisory()}"
    message += f"\n\n{get_random_trivia()}"

    send_teams_message(message)

if __name__ == "__main__":
    main()
