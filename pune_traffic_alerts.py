import os
import requests
import feedparser
import random
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# RSS Feed URL for "Pune Traffic" from Google News
RSS_FEED_URL = "https://news.google.com/rss/search?q=Pune+traffic&hl=en-IN&gl=IN&ceid=IN:en"

# Replace with your actual webhook URL
WEBHOOK_URL = "https://sasoffice365.webhook.office.com/webhookb2/8d876413-4bc7-4abd-b61a-8abfa60d7f05@b1c14d5c-3625-45b3-a430-9552373a0c2f/IncomingWebhook/c8475f982a214f8ea90e0b9ec0eb6fef/78155421-4474-4cfc-8a9f-2e54ba3c6e6b/V2NZOweqKq1eRhYiezPQyvFFg6mTHzqS-yiqYmy1-JaWY1"

# File to store posted article links
POSTED_LOG = "posted_links.txt"

# Limit the number of updates to prevent long messages
MAX_UPDATES = 5

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
            formatted = f"[{title}]({link})"
            new_items.append(formatted)
            mark_as_posted(link)

        if len(new_items) >= MAX_UPDATES:
            break

    return new_items

def get_random_trivia():
    trivia_list = [
        "Shibuya crossing in Tokyo sees 2,500+ people cross at once!",
        "The world’s longest traffic jam lasted 12 days in China!",
        "Red light cameras were first introduced in the Netherlands.",
        "Delhi has one of the world’s highest car densities!",
        "New York’s Times Square was once a major traffic intersection!",
        "Drivers in Bengaluru waste nearly 243 hours/year in traffic.",
        "Women blink nearly twice as much as men.",
        "London was the first city to enforce congestion charges.",
    ]
    return random.choice(trivia_list)

def send_teams_message(message):
    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        print("✅ Message sent successfully.")
    else:
        print(f"❌ Failed to send message. Status code: {response.status_code}")

def main():
    print("🔄 Checking for new traffic updates...")
    updates = get_new_traffic_updates()
    trivia = get_random_trivia()

    if updates:
        message = "🚦 **Pune Traffic Updates**\n\n" + "\n".join([f"📰 {item}" for item in updates])
    else:
        message = "🚦 **Pune Traffic Updates**\n\nNo new traffic updates at the moment. Stay safe and drive smart! 🚗"

    # Add Monsoon Advisory
    message += "\n\n☔ **Monsoon Advisory:** Roads may be slippery — drive cautiously and allow extra travel time!"

    # Add Trivia
    message += f"\n\n🚗 **Traffic Trivia of the Day**\n_{trivia}_"

    send_teams_message(message)


if __name__ == "__main__":
    main()
