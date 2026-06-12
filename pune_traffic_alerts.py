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

    return now_ist.hour in [8, 12, 16]

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
"Traffic conditions vary across different seasons."
    "Pune traffic around Baner tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Viman Nagar tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Aundh tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Pashan tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Balewadi tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Swargate tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Deccan tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Karve Road tends to increase during weekends, impacting commute times significantly.",
"Pune traffic around SB Road tends to increase during office commute, impacting commute times significantly.",
"Pune traffic around Magarpatta tends to increase during school hours, impacting commute times significantly.",
"Pune traffic around Warje tends to increase during festival days, impacting commute times significantly.",
"Pune traffic around Baner tends to increase during late evenings, impacting commute times significantly.",
"Pune traffic around Wakad tends to increase during morning peak hours, impacting commute times significantly.",
"Pune traffic around Hinjewadi tends to increase during evening rush, impacting commute times significantly.",
"Pune traffic around Kharadi tends to increase during monsoon season, impacting commute times significantly.",
"Pune traffic around Hadapsar tends to increase during weekends, impacting commute times significantly."
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
"Traffic flow in SB Road improves late at night.",
"Magarpatta sees heavy two-wheeler movement during peak hours.",
"Road capacity in Warje is often exceeded during rush hours.",
"Kothrud experiences slower traffic speeds during school timings.",
"Traffic congestion in Shivajinagar impacts fuel efficiency for commuters.",
"Baner roads are prone to temporary jams due to parking violations.",
"Traffic density in Wakad has increased with urban expansion.",
"Hinjewadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Kharadi increases significantly during peak office hours.",
"Hadapsar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Viman Nagar during monsoon conditions.",
"Aundh sees improved traffic flow during early morning hours.",
"Evening rush hours in Pashan often lead to extended travel times.",
"Balewadi roads are heavily impacted during festival days.",
"Traffic near Swargate slows down due to signal-heavy intersections.",
"Deccan witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Karve Road is influenced by shopping and dining activity.",
"SB Road often faces congestion due to ongoing infrastructure work.",
"Traffic in Magarpatta becomes unpredictable during sudden weather changes.",
"Warje junctions are key congestion points during daily commutes.",
"Traffic flow in Kothrud improves late at night.",
"Shivajinagar sees heavy two-wheeler movement during peak hours.",
"Road capacity in Baner is often exceeded during rush hours.",
"Wakad experiences slower traffic speeds during school timings.",
"Traffic congestion in Hinjewadi impacts fuel efficiency for commuters.",
"Kharadi roads are prone to temporary jams due to parking violations.",
"Traffic density in Hadapsar has increased with urban expansion.",
"Viman Nagar experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Aundh increases significantly during peak office hours.",
"Pashan experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Balewadi during monsoon conditions.",
"Swargate sees improved traffic flow during early morning hours.",
"Evening rush hours in Deccan often lead to extended travel times.",
"Karve Road roads are heavily impacted during festival days.",
"Traffic near SB Road slows down due to signal-heavy intersections.",
"Magarpatta witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Warje is influenced by shopping and dining activity.",
"Kothrud often faces congestion due to ongoing infrastructure work.",
"Traffic in Shivajinagar becomes unpredictable during sudden weather changes.",
"Baner junctions are key congestion points during daily commutes.",
"Traffic flow in Wakad improves late at night.",
"Hinjewadi sees heavy two-wheeler movement during peak hours.",
"Road capacity in Kharadi is often exceeded during rush hours.",
"Hadapsar experiences slower traffic speeds during school timings.",
"Traffic congestion in Viman Nagar impacts fuel efficiency for commuters.",
"Aundh roads are prone to temporary jams due to parking violations.",
"Traffic density in Pashan has increased with urban expansion.",
"Balewadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Swargate increases significantly during peak office hours.",
"Deccan experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Karve Road during monsoon conditions.",
"SB Road sees improved traffic flow during early morning hours.",
"Evening rush hours in Magarpatta often lead to extended travel times.",
"Warje roads are heavily impacted during festival days.",
"Traffic near Kothrud slows down due to signal-heavy intersections.",
"Shivajinagar witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Baner is influenced by shopping and dining activity.",
"Wakad often faces congestion due to ongoing infrastructure work.",
"Traffic in Hinjewadi becomes unpredictable during sudden weather changes.",
"Kharadi junctions are key congestion points during daily commutes.",
"Traffic flow in Hadapsar improves late at night.",
"Viman Nagar sees heavy two-wheeler movement during peak hours.",
"Road capacity in Aundh is often exceeded during rush hours.",
"Pashan experiences slower traffic speeds during school timings.",
"Traffic congestion in Balewadi impacts fuel efficiency for commuters.",
"Swargate roads are prone to temporary jams due to parking violations.",
"Traffic density in Deccan has increased with urban expansion.",
"Karve Road experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in SB Road increases significantly during peak office hours.",
"Magarpatta experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Warje during monsoon conditions.",
"Kothrud sees improved traffic flow during early morning hours.",
"Evening rush hours in Shivajinagar often lead to extended travel times.",
"Baner roads are heavily impacted during festival days.",
"Traffic near Wakad slows down due to signal-heavy intersections.",
"Hinjewadi witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Kharadi is influenced by shopping and dining activity.",
"Hadapsar often faces congestion due to ongoing infrastructure work.",
"Traffic in Viman Nagar becomes unpredictable during sudden weather changes.",
"Aundh junctions are key congestion points during daily commutes.",
"Traffic flow in Pashan improves late at night.",
"Balewadi sees heavy two-wheeler movement during peak hours.",
"Road capacity in Swargate is often exceeded during rush hours.",
"Deccan experiences slower traffic speeds during school timings.",
"Traffic congestion in Karve Road impacts fuel efficiency for commuters.",
"SB Road roads are prone to temporary jams due to parking violations.",
"Traffic density in Magarpatta has increased with urban expansion.",
"Warje experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Kothrud increases significantly during peak office hours.",
"Shivajinagar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Baner during monsoon conditions.",
"Wakad sees improved traffic flow during early morning hours.",
"Evening rush hours in Hinjewadi often lead to extended travel times.",
"Kharadi roads are heavily impacted during festival days.",
"Traffic near Hadapsar slows down due to signal-heavy intersections.",
"Viman Nagar witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Aundh is influenced by shopping and dining activity.",
"Pashan often faces congestion due to ongoing infrastructure work.",
"Traffic in Balewadi becomes unpredictable during sudden weather changes.",
"Swargate junctions are key congestion points during daily commutes.",
"Traffic flow in Deccan improves late at night.",
"Karve Road sees heavy two-wheeler movement during peak hours.",
"Road capacity in SB Road is often exceeded during rush hours.",
"Magarpatta experiences slower traffic speeds during school timings.",
"Traffic congestion in Warje impacts fuel efficiency for commuters.",
"Kothrud roads are prone to temporary jams due to parking violations.",
"Traffic density in Shivajinagar has increased with urban expansion.",
"Baner experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Wakad increases significantly during peak office hours.",
"Hinjewadi experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Kharadi during monsoon conditions.",
"Hadapsar sees improved traffic flow during early morning hours.",
"Evening rush hours in Viman Nagar often lead to extended travel times.",
"Aundh roads are heavily impacted during festival days.",
"Traffic near Pashan slows down due to signal-heavy intersections.",
"Balewadi witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Swargate is influenced by shopping and dining activity.",
"Deccan often faces congestion due to ongoing infrastructure work.",
"Traffic in Karve Road becomes unpredictable during sudden weather changes.",
"SB Road junctions are key congestion points during daily commutes.",
"Traffic flow in Magarpatta improves late at night.",
"Warje sees heavy two-wheeler movement during peak hours.",
"Road capacity in Kothrud is often exceeded during rush hours.",
"Shivajinagar experiences slower traffic speeds during school timings.",
"Traffic congestion in Baner impacts fuel efficiency for commuters.",
"Wakad roads are prone to temporary jams due to parking violations.",
"Traffic density in Hinjewadi has increased with urban expansion.",
"Kharadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Hadapsar increases significantly during peak office hours.",
"Viman Nagar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Aundh during monsoon conditions.",
"Pashan sees improved traffic flow during early morning hours.",
"Evening rush hours in Balewadi often lead to extended travel times.",
"Swargate roads are heavily impacted during festival days.",
"Traffic near Deccan slows down due to signal-heavy intersections.",
"Karve Road witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in SB Road is influenced by shopping and dining activity.",
"Magarpatta often faces congestion due to ongoing infrastructure work.",
"Traffic in Warje becomes unpredictable during sudden weather changes.",
"Kothrud junctions are key congestion points during daily commutes.",
"Traffic flow in Shivajinagar improves late at night.",
"Baner sees heavy two-wheeler movement during peak hours.",
"Road capacity in Wakad is often exceeded during rush hours.",
"Hinjewadi experiences slower traffic speeds during school timings.",
"Traffic congestion in Kharadi impacts fuel efficiency for commuters.",
"Hadapsar roads are prone to temporary jams due to parking violations.",
"Traffic density in Viman Nagar has increased with urban expansion.",
"Aundh experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Pashan increases significantly during peak office hours.",
"Balewadi experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Swargate during monsoon conditions.",
"Deccan sees improved traffic flow during early morning hours.",
"Evening rush hours in Karve Road often lead to extended travel times.",
"SB Road roads are heavily impacted during festival days.",
"Traffic near Magarpatta slows down due to signal-heavy intersections.",
"Warje witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Kothrud is influenced by shopping and dining activity.",
"Shivajinagar often faces congestion due to ongoing infrastructure work.",
"Traffic in Baner becomes unpredictable during sudden weather changes.",
"Wakad junctions are key congestion points during daily commutes.",
"Traffic flow in Hinjewadi improves late at night.",
"Kharadi sees heavy two-wheeler movement during peak hours.",
"Road capacity in Hadapsar is often exceeded during rush hours.",
"Viman Nagar experiences slower traffic speeds during school timings.",
"Traffic congestion in Aundh impacts fuel efficiency for commuters.",
"Pashan roads are prone to temporary jams due to parking violations.",
"Traffic density in Balewadi has increased with urban expansion.",
"Swargate experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Deccan increases significantly during peak office hours.",
"Karve Road experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in SB Road during monsoon conditions.",
"Magarpatta sees improved traffic flow during early morning hours.",
"Evening rush hours in Warje often lead to extended travel times.",
"Kothrud roads are heavily impacted during festival days.",
"Traffic near Shivajinagar slows down due to signal-heavy intersections.",
"Baner witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Wakad is influenced by shopping and dining activity.",
"Hinjewadi often faces congestion due to ongoing infrastructure work.",
"Traffic in Kharadi becomes unpredictable during sudden weather changes.",
"Hadapsar junctions are key congestion points during daily commutes.",
"Traffic flow in Viman Nagar improves late at night.",
"Aundh sees heavy two-wheeler movement during peak hours.",
"Road capacity in Pashan is often exceeded during rush hours.",
"Balewadi experiences slower traffic speeds during school timings.",
"Traffic congestion in Swargate impacts fuel efficiency for commuters.",
"Deccan roads are prone to temporary jams due to parking violations.",
"Traffic density in Karve Road has increased with urban expansion.",
"SB Road experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Magarpatta increases significantly during peak office hours.",
"Warje experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Kothrud during monsoon conditions.",
"Shivajinagar sees improved traffic flow during early morning hours.",
"Evening rush hours in Baner often lead to extended travel times.",
"Wakad roads are heavily impacted during festival days.",
"Traffic near Hinjewadi slows down due to signal-heavy intersections.",
"Kharadi witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Hadapsar is influenced by shopping and dining activity.",
"Viman Nagar often faces congestion due to ongoing infrastructure work.",
"Traffic in Aundh becomes unpredictable during sudden weather changes.",
"Pashan junctions are key congestion points during daily commutes.",
"Traffic flow in Balewadi improves late at night.",
"Swargate sees heavy two-wheeler movement during peak hours.",
"Road capacity in Deccan is often exceeded during rush hours.",
"Karve Road experiences slower traffic speeds during school timings.",
"Traffic congestion in SB Road impacts fuel efficiency for commuters.",
"Magarpatta roads are prone to temporary jams due to parking violations.",
"Traffic density in Warje has increased with urban expansion.",
"Kothrud experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Shivajinagar increases significantly during peak office hours.",
"Baner experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Wakad during monsoon conditions.",
"Hinjewadi sees improved traffic flow during early morning hours.",
"Evening rush hours in Kharadi often lead to extended travel times.",
"Hadapsar roads are heavily impacted during festival days.",
"Traffic near Viman Nagar slows down due to signal-heavy intersections.",
"Aundh witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Pashan is influenced by shopping and dining activity.",
"Balewadi often faces congestion due to ongoing infrastructure work.",
"Traffic in Swargate becomes unpredictable during sudden weather changes.",
"Deccan junctions are key congestion points during daily commutes.",
"Traffic flow in Karve Road improves late at night.",
"SB Road sees heavy two-wheeler movement during peak hours.",
"Road capacity in Magarpatta is often exceeded during rush hours.",
"Warje experiences slower traffic speeds during school timings.",
"Traffic congestion in Kothrud impacts fuel efficiency for commuters.",
"Shivajinagar roads are prone to temporary jams due to parking violations.",
"Traffic density in Baner has increased with urban expansion.",
"Wakad experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Hinjewadi increases significantly during peak office hours.",
"Kharadi experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Hadapsar during monsoon conditions.",
"Viman Nagar sees improved traffic flow during early morning hours.",
"Evening rush hours in Aundh often lead to extended travel times.",
"Pashan roads are heavily impacted during festival days.",
"Traffic near Balewadi slows down due to signal-heavy intersections.",
"Swargate witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Deccan is influenced by shopping and dining activity.",
"Karve Road often faces congestion due to ongoing infrastructure work.",
"Traffic in SB Road becomes unpredictable during sudden weather changes.",
"Magarpatta junctions are key congestion points during daily commutes.",
"Traffic flow in Warje improves late at night.",
"Kothrud sees heavy two-wheeler movement during peak hours.",
"Road capacity in Shivajinagar is often exceeded during rush hours.",
"Baner experiences slower traffic speeds during school timings.",
"Traffic congestion in Wakad impacts fuel efficiency for commuters.",
"Hinjewadi roads are prone to temporary jams due to parking violations.",
"Traffic density in Kharadi has increased with urban expansion.",
"Hadapsar experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Viman Nagar increases significantly during peak office hours.",
"Aundh experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Pashan during monsoon conditions.",
"Balewadi sees improved traffic flow during early morning hours.",
"Evening rush hours in Swargate often lead to extended travel times.",
"Deccan roads are heavily impacted during festival days.",
"Traffic near Karve Road slows down due to signal-heavy intersections.",
"SB Road witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Magarpatta is influenced by shopping and dining activity.",
"Warje often faces congestion due to ongoing infrastructure work.",
"Traffic in Kothrud becomes unpredictable during sudden weather changes.",
"Shivajinagar junctions are key congestion points during daily commutes.",
"Traffic flow in Baner improves late at night.",
"Wakad sees heavy two-wheeler movement during peak hours.",
"Road capacity in Hinjewadi is often exceeded during rush hours.",
"Kharadi experiences slower traffic speeds during school timings.",
"Traffic congestion in Hadapsar impacts fuel efficiency for commuters.",
"Viman Nagar roads are prone to temporary jams due to parking violations.",
"Traffic density in Aundh has increased with urban expansion.",
"Pashan experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Balewadi increases significantly during peak office hours.",
"Swargate experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Deccan during monsoon conditions.",
"Karve Road sees improved traffic flow during early morning hours.",
"Evening rush hours in SB Road often lead to extended travel times.",
"Magarpatta roads are heavily impacted during festival days.",
"Traffic near Warje slows down due to signal-heavy intersections.",
"Kothrud witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Shivajinagar is influenced by shopping and dining activity.",
"Baner often faces congestion due to ongoing infrastructure work.",
"Traffic in Wakad becomes unpredictable during sudden weather changes.",
"Hinjewadi junctions are key congestion points during daily commutes.",
"Traffic flow in Kharadi improves late at night.",
"Hadapsar sees heavy two-wheeler movement during peak hours.",
"Road capacity in Viman Nagar is often exceeded during rush hours.",
"Aundh experiences slower traffic speeds during school timings.",
"Traffic congestion in Pashan impacts fuel efficiency for commuters.",
"Balewadi roads are prone to temporary jams due to parking violations.",
"Traffic density in Swargate has increased with urban expansion.",
"Deccan experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Karve Road increases significantly during peak office hours.",
"SB Road experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Magarpatta during monsoon conditions.",
"Warje sees improved traffic flow during early morning hours.",
"Evening rush hours in Kothrud often lead to extended travel times.",
"Shivajinagar roads are heavily impacted during festival days.",
"Traffic near Baner slows down due to signal-heavy intersections.",
"Wakad witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Hinjewadi is influenced by shopping and dining activity.",
"Kharadi often faces congestion due to ongoing infrastructure work.",
"Traffic in Hadapsar becomes unpredictable during sudden weather changes.",
"Viman Nagar junctions are key congestion points during daily commutes.",
"Traffic flow in Aundh improves late at night.",
"Pashan sees heavy two-wheeler movement during peak hours.",
"Road capacity in Balewadi is often exceeded during rush hours.",
"Swargate experiences slower traffic speeds during school timings.",
"Traffic congestion in Deccan impacts fuel efficiency for commuters.",
"Karve Road roads are prone to temporary jams due to parking violations.",
"Traffic density in SB Road has increased with urban expansion.",
"Magarpatta experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Warje increases significantly during peak office hours.",
"Kothrud experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Shivajinagar during monsoon conditions.",
"Baner sees improved traffic flow during early morning hours.",
"Evening rush hours in Wakad often lead to extended travel times.",
"Hinjewadi roads are heavily impacted during festival days.",
"Traffic near Kharadi slows down due to signal-heavy intersections.",
"Hadapsar witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Viman Nagar is influenced by shopping and dining activity.",
"Aundh often faces congestion due to ongoing infrastructure work.",
"Traffic in Pashan becomes unpredictable during sudden weather changes.",
"Balewadi junctions are key congestion points during daily commutes.",
"Traffic flow in Swargate improves late at night.",
"Deccan sees heavy two-wheeler movement during peak hours.",
"Road capacity in Karve Road is often exceeded during rush hours.",
"SB Road experiences slower traffic speeds during school timings.",
"Traffic congestion in Magarpatta impacts fuel efficiency for commuters.",
"Warje roads are prone to temporary jams due to parking violations.",
"Traffic density in Kothrud has increased with urban expansion.",
"Shivajinagar experiences traffic fluctuations based on IT park schedules.",
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
"Traffic flow in SB Road improves late at night.",
"Magarpatta sees heavy two-wheeler movement during peak hours.",
"Road capacity in Warje is often exceeded during rush hours.",
"Kothrud experiences slower traffic speeds during school timings.",
"Traffic congestion in Shivajinagar impacts fuel efficiency for commuters.",
"Baner roads are prone to temporary jams due to parking violations.",
"Traffic density in Wakad has increased with urban expansion.",
"Hinjewadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Kharadi increases significantly during peak office hours.",
"Hadapsar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Viman Nagar during monsoon conditions.",
"Aundh sees improved traffic flow during early morning hours.",
"Evening rush hours in Pashan often lead to extended travel times.",
"Balewadi roads are heavily impacted during festival days.",
"Traffic near Swargate slows down due to signal-heavy intersections.",
"Deccan witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Karve Road is influenced by shopping and dining activity.",
"SB Road often faces congestion due to ongoing infrastructure work.",
"Traffic in Magarpatta becomes unpredictable during sudden weather changes.",
"Warje junctions are key congestion points during daily commutes.",
"Traffic flow in Kothrud improves late at night.",
"Shivajinagar sees heavy two-wheeler movement during peak hours.",
"Road capacity in Baner is often exceeded during rush hours.",
"Wakad experiences slower traffic speeds during school timings.",
"Traffic congestion in Hinjewadi impacts fuel efficiency for commuters.",
"Kharadi roads are prone to temporary jams due to parking violations.",
"Traffic density in Hadapsar has increased with urban expansion.",
"Viman Nagar experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Aundh increases significantly during peak office hours.",
"Pashan experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Balewadi during monsoon conditions.",
"Swargate sees improved traffic flow during early morning hours.",
"Evening rush hours in Deccan often lead to extended travel times.",
"Karve Road roads are heavily impacted during festival days.",
"Traffic near SB Road slows down due to signal-heavy intersections.",
"Magarpatta witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Warje is influenced by shopping and dining activity.",
"Kothrud often faces congestion due to ongoing infrastructure work.",
"Traffic in Shivajinagar becomes unpredictable during sudden weather changes.",
"Baner junctions are key congestion points during daily commutes.",
"Traffic flow in Wakad improves late at night.",
"Hinjewadi sees heavy two-wheeler movement during peak hours.",
"Road capacity in Kharadi is often exceeded during rush hours.",
"Hadapsar experiences slower traffic speeds during school timings.",
"Traffic congestion in Viman Nagar impacts fuel efficiency for commuters.",
"Aundh roads are prone to temporary jams due to parking violations.",
"Traffic density in Pashan has increased with urban expansion.",
"Balewadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Swargate increases significantly during peak office hours.",
"Deccan experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Karve Road during monsoon conditions.",
"SB Road sees improved traffic flow during early morning hours.",
"Evening rush hours in Magarpatta often lead to extended travel times.",
"Warje roads are heavily impacted during festival days.",
"Traffic near Kothrud slows down due to signal-heavy intersections.",
"Shivajinagar witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Baner is influenced by shopping and dining activity.",
"Wakad often faces congestion due to ongoing infrastructure work.",
"Traffic in Hinjewadi becomes unpredictable during sudden weather changes.",
"Kharadi junctions are key congestion points during daily commutes.",
"Traffic flow in Hadapsar improves late at night.",
"Viman Nagar sees heavy two-wheeler movement during peak hours.",
"Road capacity in Aundh is often exceeded during rush hours.",
"Pashan experiences slower traffic speeds during school timings.",
"Traffic congestion in Balewadi impacts fuel efficiency for commuters.",
"Swargate roads are prone to temporary jams due to parking violations.",
"Traffic density in Deccan has increased with urban expansion.",
"Karve Road experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in SB Road increases significantly during peak office hours.",
"Magarpatta experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Warje during monsoon conditions.",
"Kothrud sees improved traffic flow during early morning hours.",
"Evening rush hours in Shivajinagar often lead to extended travel times.",
"Baner roads are heavily impacted during festival days.",
"Traffic near Wakad slows down due to signal-heavy intersections.",
"Hinjewadi witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Kharadi is influenced by shopping and dining activity.",
"Hadapsar often faces congestion due to ongoing infrastructure work.",
"Traffic in Viman Nagar becomes unpredictable during sudden weather changes.",
"Aundh junctions are key congestion points during daily commutes.",
"Traffic flow in Pashan improves late at night.",
"Balewadi sees heavy two-wheeler movement during peak hours.",
"Road capacity in Swargate is often exceeded during rush hours.",
"Deccan experiences slower traffic speeds during school timings.",
"Traffic congestion in Karve Road impacts fuel efficiency for commuters.",
"SB Road roads are prone to temporary jams due to parking violations.",
"Traffic density in Magarpatta has increased with urban expansion.",
"Warje experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Kothrud increases significantly during peak office hours.",
"Shivajinagar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Baner during monsoon conditions.",
"Wakad sees improved traffic flow during early morning hours.",
"Evening rush hours in Hinjewadi often lead to extended travel times.",
"Kharadi roads are heavily impacted during festival days.",
"Traffic near Hadapsar slows down due to signal-heavy intersections.",
"Viman Nagar witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Aundh is influenced by shopping and dining activity.",
"Pashan often faces congestion due to ongoing infrastructure work.",
"Traffic in Balewadi becomes unpredictable during sudden weather changes.",
"Swargate junctions are key congestion points during daily commutes.",
"Traffic flow in Deccan improves late at night.",
"Karve Road sees heavy two-wheeler movement during peak hours.",
"Road capacity in SB Road is often exceeded during rush hours.",
"Magarpatta experiences slower traffic speeds during school timings.",
"Traffic congestion in Warje impacts fuel efficiency for commuters.",
"Kothrud roads are prone to temporary jams due to parking violations.",
"Traffic density in Shivajinagar has increased with urban expansion.",
"Baner experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Wakad increases significantly during peak office hours.",
"Hinjewadi experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Kharadi during monsoon conditions.",
"Hadapsar sees improved traffic flow during early morning hours.",
"Evening rush hours in Viman Nagar often lead to extended travel times.",
"Aundh roads are heavily impacted during festival days.",
"Traffic near Pashan slows down due to signal-heavy intersections.",
"Balewadi witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in Swargate is influenced by shopping and dining activity.",
"Deccan often faces congestion due to ongoing infrastructure work.",
"Traffic in Karve Road becomes unpredictable during sudden weather changes.",
"SB Road junctions are key congestion points during daily commutes.",
"Traffic flow in Magarpatta improves late at night.",
"Warje sees heavy two-wheeler movement during peak hours.",
"Road capacity in Kothrud is often exceeded during rush hours.",
"Shivajinagar experiences slower traffic speeds during school timings.",
"Traffic congestion in Baner impacts fuel efficiency for commuters.",
"Wakad roads are prone to temporary jams due to parking violations.",
"Traffic density in Hinjewadi has increased with urban expansion.",
"Kharadi experiences traffic fluctuations based on IT park schedules.",
"Traffic congestion in Hadapsar increases significantly during peak office hours.",
"Viman Nagar experiences frequent bottlenecks due to high vehicle density.",
"Commute delays are common in Aundh during monsoon conditions.",
"Pashan sees improved traffic flow during early morning hours.",
"Evening rush hours in Balewadi often lead to extended travel times.",
"Swargate roads are heavily impacted during festival days.",
"Traffic near Deccan slows down due to signal-heavy intersections.",
"Karve Road witnesses increased traffic due to nearby commercial hubs.",
"Weekend traffic in SB Road is influenced by shopping and dining activity.",
"Magarpatta often faces congestion due to ongoing infrastructure work.",
"Traffic in Warje becomes unpredictable during sudden weather changes.",
"Kothrud junctions are key congestion points during daily commutes.",
"Traffic flow in Shivajinagar improves late at night.",
"Baner sees heavy two-wheeler movement during peak hours.",
"Road capacity in Wakad is often exceeded during rush hours.",
"Hinjewadi experiences slower traffic speeds during school timings.",
"Traffic congestion in Kharadi impacts fuel efficiency for commuters.",
"Hadapsar roads are prone to temporary jams due to parking violations.",
"Traffic density in Viman Nagar has increased with urban expansion.",
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
    if is_regular_run_time() and new_items:
    message = prepare_message(new_items)
    post_to_teams(message)


if __name__ == "__main__":
    main()
