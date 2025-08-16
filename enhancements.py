# enhancements.py
import random
import requests
import os

# -----------------------------
# 1. Random Trivia/Tip Pool
# -----------------------------
TRIVIA_POOL = [
    # Indian Traffic Trivia
    "🚦 The first traffic light in India was installed in Delhi in 1953.",
    "🛣️ India has the second-largest road network in the world, after the USA.",
    "🚗 The Bandra-Worli Sea Link cables can circle the Earth once if placed end-to-end.",
    "🛵 Two-wheelers account for nearly 70% of vehicles on Indian roads.",
    "🚨 Mumbai has the highest number of CCTV cameras per sq km for traffic monitoring.",

    # Driving Tips
    "⚠️ Maintain a 3-second distance from the vehicle in front of you.",
    "🛑 Always slow down near zebra crossings.",
    "💡 Use low-beam headlights during foggy conditions.",
    "🚧 Avoid sudden lane changes in heavy traffic.",
    "🔋 Keep your vehicle well-maintained to reduce breakdown risks.",

    # Fun Global Facts
    "🌉 In Japan, trains have 99.9% punctuality.",
    "🚦 The world’s first traffic light was installed in London in 1868.",
    "🇹🇷 Istanbul drivers cross from Europe to Asia daily!",
    "🇺🇸 Los Angeles is known for having the world’s worst traffic jams.",
    "🚅 China has the largest high-speed rail network in the world."
]

def get_random_trivia():
    return random.choice(TRIVIA_POOL)


# -----------------------------
# 2. Weather-Aware Advisory
# -----------------------------
def get_weather_advisory(city="Pune"):
    api_key = os.getenv("OPENWEATHER_API_KEY")  # keep your API key safe in GitHub secrets
    if not api_key:
        return "🌤️ Stay alert and drive safe!"
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10).json()
        weather = response["weather"][0]["main"].lower()

        if "rain" in weather:
            return "☔ Monsoon Alert: Roads may be slippery — drive cautiously!"
        elif "fog" in weather or "mist" in weather or "haze" in weather:
            return "🌫️ Low visibility — keep headlights on low-beam."
        elif "clear" in weather:
            return "🌞 Clear skies today — stay safe at signals!"
        elif "cloud" in weather:
            return "⛅ Cloudy weather — good time to keep extra patience!"
        else:
            return "🚦 Stay alert on the roads today!"
    except Exception:
        return "🌤️ Stay alert and drive safe!"


# -----------------------------
# 3. Severity Emoji Formatter
# -----------------------------
def format_severity(update_text):
    """
    Example usage:
    Input: "Heavy Traffic On Pune-Mumbai Highway"
    Output: "🔴 Heavy Traffic On Pune-Mumbai Highway"
    """
    text = update_text.lower()
    if "heavy" in text or "jam" in text or "congestion" in text:
        return f"🔴 {update_text}"
    elif "moderate" in text or "slow" in text:
        return f"🟡 {update_text}"
    else:
        return f"🟢 {update_text}"
