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
    "The first electric traffic light was installed in Cleveland, Ohio, in 1914!",
    "In Jakarta, people once hired ‘jockeys’ to pretend to be passengers so they could use carpool lanes!",
    "London introduced a congestion charge in 2003 to ease central city traffic.",
    "Singapore uses electronic tolling to manage rush-hour traffic automatically.",
    "Bangkok commuters can spend over 60% more time in traffic during peak hours.",
    "São Paulo, Brazil, can experience traffic jams over 180 km long on Fridays!",
    "Beijing drivers can only use their cars on certain days to control congestion.",
    "Istanbul drivers cross from Europe to Asia daily — but rush hour can double travel time.",
    "The Netherlands has ‘bicycle highways’ to help cut car traffic.",
    "Mexico City limits driving days based on your license plate to reduce jams and pollution.",
    "Manila’s famous Jeepneys are a major contributor to chaotic traffic.",
    "In Mumbai, the traffic police run a ‘Traffic Awareness Park’ for citizens.",
    "Germany’s Autobahn has no speed limit but jams can still happen in rush hour.",
    "In Los Angeles, drivers lose 100+ hours a year to traffic delays!",
    "London drivers pay a fee to enter central areas during peak hours to reduce jams."
    "Mumbai’s famous Dabbawalas use local trains and bikes to deliver 200,000 lunchboxes daily — beating the city’s traffic!",
    "The Bandra-Worli Sea Link in Mumbai cuts travel time by up to 30 minutes during peak traffic.",
    "Bengaluru is often nicknamed the 'Traffic Capital of India' due to its chronic jams.",
    "Hyderabad’s Outer Ring Road is one of India’s longest expressways — easing city congestion.",
    "Delhi’s Connaught Place area once had the country’s first automatic traffic lights!",
    "During Ganesh Chaturthi, Mumbai traffic diversions cover over 3,000 roads in the city.",
    "India’s Golden Quadrilateral highway network connects Delhi, Mumbai, Chennai, and Kolkata — covering 5,846 km!",
    "Pune was among the first Indian cities to launch Smart Traffic Signals for smoother flow.",
    "In Chennai, Marina Beach Road sees huge traffic during festival seasons like Pongal.",
    "The Delhi Metro helps remove over 7 lakh vehicles daily from the city’s roads!",
    "Kolkata’s Howrah Bridge handles over 100,000 vehicles and countless pedestrians daily.",
    "Pune’s Hinjewadi IT Park sees traffic jams so long, many companies encourage remote work during monsoon chaos.",
    "India’s longest flyover — the PV Narasimha Rao Expressway in Hyderabad — is 11.6 km long!",
    "The Eastern Peripheral Expressway diverts heavy traffic around Delhi to cut pollution and jams.",
    "In Pune, Palkhi processions require unique traffic curbs each year, rerouting thousands of vehicles."
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
