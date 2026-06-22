"""Paul John Group of Hotels — Operations Dashboard"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Paul John Group — Operations",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="collapsed",
)

# ── STYLES — Sage & Amber on Cream palette ────────────────────────────────────
# Palette: sage #4a6b52, amber #c8814a, parchment #f5ede0, sand #e0c4a8

st.html("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
<style>
  /* Global */
  html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    background-color: #f5ede0;
  }

  /* Header */
  .pj-header {
    background: linear-gradient(135deg, #4a6b52 0%, #2d4a35 100%);
    color: #f5ede0;
    padding: 22px 32px;
    border-radius: 0 0 12px 12px;
    margin-bottom: 24px;
    border-bottom: 3px solid #c8814a;
  }
  .pj-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    margin: 0;
    letter-spacing: 1.5px;
    color: #f5ede0;
  }
  .pj-header .gold { color: #c8814a; }
  .pj-header p {
    font-size: 12px;
    margin: 6px 0 0;
    color: #b8d4bc;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }

  /* Section headers */
  .section-hdr {
    font-family: 'Playfair Display', serif;
    font-size: 13px;
    font-weight: 600;
    color: #4a6b52;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    border-bottom: 1px solid #c8814a;
    padding-bottom: 5px;
    margin: 22px 0 12px;
  }

  /* Hotel subtitle */
  .hotel-sub {
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    color: #4a6b52;
    border-left: 3px solid #c8814a;
    padding-left: 12px;
    margin-bottom: 16px;
  }
  .hotel-sub span { font-size: 11px; color: #7a9e82; font-family: 'Lato', sans-serif; display: block; letter-spacing: 0.5px; }

  /* Streamlit metric tweaks */
  [data-testid="stMetricValue"] { font-family: 'Playfair Display', serif; color: #4a6b52; }
  [data-testid="stMetricLabel"] { font-family: 'Lato', sans-serif; color: #6b8c72; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }

  /* Tabs — spaced out */
  [data-baseweb="tab-list"] { background: #4a6b52; border-radius: 10px; padding: 6px 8px; gap: 6px; flex-wrap: nowrap; overflow-x: auto; }
  [data-baseweb="tab"] { color: #c8dfc8 !important; font-family: 'Lato', sans-serif; font-size: 13px; letter-spacing: 0.3px; border-radius: 7px; padding: 10px 22px !important; white-space: nowrap; }
  [aria-selected="true"][data-baseweb="tab"] { background: #c8814a !important; color: #2d4a35 !important; font-weight: 700 !important; }

  /* Dataframe */
  [data-testid="stDataFrame"] { border: 1px solid #e0c4a8; border-radius: 6px; }

  /* Expander */
  [data-testid="stExpander"] { border: 1px solid #e0c4a8; border-radius: 6px; background: #fffaf5; }

  /* House status badges */
  .badge-green { background:#eaf3ec; color:#2d4a35; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; border:1px solid #7aaa82; }
  .badge-red   { background:#fce8e6; color:#7f1d1d; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; border:1px solid #e8a09a; }
  .badge-gold  { background:#fef3e2; color:#7a4500; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; border:1px solid #c8814a; }
  .badge-blue  { background:#eaf0f5; color:#1a3a6b; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; border:1px solid #8ab0d0; }

  /* Footer */
  .cw-footer { text-align:center; color:#7a9e82; font-size:11px; margin-top:30px; padding:16px; border-top:1px solid #e0c4a8; letter-spacing:0.5px; }
</style>
""")

# ── STATIC DATA ───────────────────────────────────────────────────────────────

HOTELS = {
    "Coorg Wilderness": {
        "full_name": "Coorg Wilderness Resort & Spa",
        "location": "Coorg, Karnataka",
        "rooms": 104,
        "color": "#8b4513",
        "date": "10-06-2026",
    },
    "The Paul, Bengaluru": {
        "full_name": "The Paul, Bengaluru",
        "location": "Bengaluru, Karnataka",
        "rooms": 120,
        "color": "#a0522d",
        "date": "10-06-2026",
    },
    "Fort Kochi": {
        "full_name": "Fort Kochi — A Paul John Hotel",
        "location": "Kochi, Kerala",
        "rooms": 65,
        "color": "#c8814a",
        "date": "10-06-2026",
    },
    "Kumarakom Lake Resort": {
        "full_name": "Kumarakom Lake Resort",
        "location": "Kumarakom, Kerala",
        "rooms": 90,
        "color": "#b5651d",
        "date": "10-06-2026",
    },
}

# June 2026 occupancy — Coorg Wilderness (from screenshots)
COORG_JUNE = [
    ("01-06", "Mon", 102, 98), ("02-06", "Tue", 96, 92), ("03-06", "Wed", 88, 85),
    ("04-06", "Thu", 104, 100), ("05-06", "Fri", 98, 94), ("06-06", "Sat", 104, 100),
    ("07-06", "Sun", 89, 86), ("08-06", "Mon", 104, 100), ("09-06", "Tue", 62, 60),
    ("10-06", "Wed", 81, 78), ("11-06", "Thu", 85, 82), ("12-06", "Fri", 95, 91),
    ("13-06", "Sat", 100, 96), ("14-06", "Sun", 72, 69), ("15-06", "Mon", 60, 58),
    ("16-06", "Tue", 43, 41), ("17-06", "Wed", 34, 33), ("18-06", "Thu", 92, 88),
    ("19-06", "Fri", 80, 77), ("20-06", "Sat", 64, 62), ("21-06", "Sun", 42, 40),
    ("22-06", "Mon", 37, 36), ("23-06", "Tue", 37, 36), ("24-06", "Wed", 23, 22),
    ("25-06", "Thu", 42, 40), ("26-06", "Fri", 88, 85), ("27-06", "Sat", 86, 83),
    ("28-06", "Sun", 29, 28), ("29-06", "Mon", 20, 19), ("30-06", "Tue", 16, 15),
]

# Test occupancy for other hotels
def gen_occ(seed_occ, rooms):
    import random; random.seed(rooms)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"] * 5
    result = []
    occ = seed_occ
    for i in range(30):
        occ = max(10, min(rooms, occ + random.randint(-10, 12)))
        pct = round(occ / rooms * 100)
        result.append((f"{i+1:02d}-06", days[i], occ, pct))
    return result

PAUL_BLR_JUNE = gen_occ(100, 120)
FORT_KOCHI_JUNE = gen_occ(52, 65)
PAUL_KOL_JUNE = gen_occ(75, 90)

HOTEL_OCC_DATA = {
    "Coorg Wilderness": COORG_JUNE,
    "The Paul, Bengaluru": PAUL_BLR_JUNE,
    "Fort Kochi": FORT_KOCHI_JUNE,
    "Kumarakom Lake Resort": PAUL_KOL_JUNE,
}

# House status
HOUSE_STATUS = {
    "Coorg Wilderness":     {"Arrivals": 39, "Departures": 20, "Stayovers": 42, "Closing": 81},
    "The Paul, Bengaluru":  {"Arrivals": 45, "Departures": 28, "Stayovers": 67, "Closing": 112},
    "Fort Kochi":            {"Arrivals": 22, "Departures": 15, "Stayovers": 28, "Closing": 50},
    "Kumarakom Lake Resort":      {"Arrivals": 31, "Departures": 20, "Stayovers": 52, "Closing": 83},
}

# Meal plan breakdown
MEAL_PLANS = {
    "Coorg Wilderness": {
        "EP":  {"Stayover RM": 0,  "Arrival RM": 0},
        "CP":  {"Stayover RM": 24, "Arrival RM": 22},
        "MAP": {"Stayover RM": 9,  "Arrival RM": 14},
        "AP":  {"Stayover RM": 9,  "Arrival RM": 3},
    },
    "The Paul, Bengaluru": {
        "EP":  {"Stayover RM": 5,  "Arrival RM": 3},
        "CP":  {"Stayover RM": 38, "Arrival RM": 28},
        "MAP": {"Stayover RM": 14, "Arrival RM": 10},
        "AP":  {"Stayover RM": 10, "Arrival RM": 4},
    },
    "Fort Kochi": {
        "EP":  {"Stayover RM": 2,  "Arrival RM": 1},
        "CP":  {"Stayover RM": 16, "Arrival RM": 12},
        "MAP": {"Stayover RM": 6,  "Arrival RM": 5},
        "AP":  {"Stayover RM": 4,  "Arrival RM": 4},
    },
    "Kumarakom Lake Resort": {
        "EP":  {"Stayover RM": 3,  "Arrival RM": 2},
        "CP":  {"Stayover RM": 30, "Arrival RM": 20},
        "MAP": {"Stayover RM": 12, "Arrival RM": 6},
        "AP":  {"Stayover RM": 7,  "Arrival RM": 3},
    },
}

# Revenue — Day (actual vs budget) from screenshots for Coorg; test data for others
REV_CATEGORIES = ["Room Revenue", "F&B Revenue", "Spa/Nikaay Revenue", "Activities Revenue",
                  "Curio Shop Revenue", "Travel Desk Revenue", "Other Revenue"]

REVENUE_DAY = {
    "Coorg Wilderness": {
        "actual":  [1216524, 969345, 58690, 25400, 42031, 58700, 47049],
        "budget":  [1343245, 561492, 73099, 18145,  8608, 25858,  1273],
    },
    "The Paul, Bengaluru": {
        "actual":  [2100000, 1400000, 0, 95000, 55000, 200000, 0],
        "budget":  [2200000, 1100000, 0, 80000, 40000, 180000, 0],
    },
    "Fort Kochi": {
        "actual":  [780000, 380000, 45000, 20000, 15000, 10000, 0],
        "budget":  [820000, 200000, 40000, 18000, 12000, 10000, 0],
    },
    "Kumarakom Lake Resort": {
        "actual":  [1300000, 680000, 30000, 40000, 25000, 25000, 0],
        "budget":  [1400000, 500000, 30000, 35000, 20000, 15000, 0],
    },
}

REVENUE_MTD = {
    "Coorg Wilderness": {
        "actual":  [13358627, 7068121, 616424, 202700, 86453, 198700, 79766],
        "budget":  [12089205, 5053430, 657888, 163301, 77470, 232724, 11456],
    },
    "The Paul, Bengaluru": {
        "actual":  [22000000, 14500000, 0, 950000, 480000, 1800000, 0],
        "budget":  [21000000, 12000000, 0, 800000, 400000, 1600000, 0],
    },
    "Fort Kochi": {
        "actual":  [7800000, 3800000, 450000, 200000, 150000, 100000, 0],
        "budget":  [8200000, 3200000, 400000, 180000, 120000, 100000, 0],
    },
    "Kumarakom Lake Resort": {
        "actual":  [13000000, 6800000, 300000, 400000, 250000, 250000, 0],
        "budget":  [14000000, 5500000, 300000, 350000, 200000, 180000, 0],
    },
}

# KPIs per hotel
KPIS = {
    "Coorg Wilderness":    {"Occ%": 78, "ARR": 19621, "RevPAR": 11697, "Closing": 81,  "Paid Rooms": 62},
    "The Paul, Bengaluru": {"Occ%": 93, "ARR": 25800, "RevPAR": 24000, "Closing": 112, "Paid Rooms": 108},
    "Fort Kochi":           {"Occ%": 77, "ARR": 16200, "RevPAR": 12000, "Closing": 50,  "Paid Rooms": 48},
    "Kumarakom Lake Resort":       {"Occ%": 92, "ARR": 21500, "RevPAR": 19800, "Closing": 83,  "Paid Rooms": 80},
}

# Reservation pace
PACE = {
    "Coorg Wilderness": {
        "Budgeted RN": 2670, "Actual BOB RN": 2073, "Budgeted ARR": 15092,
        "Actual ARR BOB": 15633, "Budgeted Revenue": 40297350, "Actual Revenue": 32407149,
        "Budgeted Pace": 86, "Current Pace": 29, "Required Pace": 27, "Required ARR": 13216,
    },
    "The Paul, Bengaluru": {
        "Budgeted RN": 3200, "Actual BOB RN": 2950, "Budgeted ARR": 22000,
        "Actual ARR BOB": 23100, "Budgeted Revenue": 70400000, "Actual Revenue": 68145000,
        "Budgeted Pace": 105, "Current Pace": 98, "Required Pace": 95, "Required ARR": 20000,
    },
    "Fort Kochi": {
        "Budgeted RN": 1500, "Actual BOB RN": 1280, "Budgeted ARR": 14500,
        "Actual ARR BOB": 13800, "Budgeted Revenue": 21750000, "Actual Revenue": 17664000,
        "Budgeted Pace": 52, "Current Pace": 38, "Required Pace": 42, "Required ARR": 14000,
    },
    "Kumarakom Lake Resort": {
        "Budgeted RN": 2400, "Actual BOB RN": 2210, "Budgeted ARR": 19000,
        "Actual ARR BOB": 19800, "Budgeted Revenue": 45600000, "Actual Revenue": 43758000,
        "Budgeted Pace": 82, "Current Pace": 75, "Required Pace": 73, "Required ARR": 18000,
    },
}

# Arrivals — Coorg Wilderness (from screenshots)
COORG_ARRIVALS = [
    {"Room": "418,519", "Guest": "Mr. Harish Baluja",       "ETA": "15:00", "Rooms/Pax": "2/4 Pax", "Meal": "AP",  "Checkout": "13-Jun", "Source": "Simmi Delhi",    "SPL": "Pure veg"},
    {"Room": "102,202", "Guest": "Mr. Niraj Thakkar",       "ETA": "15:00", "Rooms/Pax": "2/4 Pax", "Meal": "CP",  "Checkout": "13-Jun", "Source": "Gujarat Sales",  "SPL": "—"},
    {"Room": "103,203", "Guest": "Ms. Bhagya Chikani",      "ETA": "15:00", "Rooms/Pax": "2/4 Pax", "Meal": "MAP", "Checkout": "14-Jun", "Source": "Praveen Cochin", "SPL": "Long Stay 4N"},
    {"Room": "602,702", "Guest": "Mr. Sandeep",             "ETA": "15:00", "Rooms/Pax": "2/5+1",   "Meal": "MAP", "Checkout": "12-Jun", "Source": "Zach BSO",       "SPL": "—"},
    {"Room": "121,221,115","Guest": "Mr. Ankit Gupta",      "ETA": "13:00", "Rooms/Pax": "3/8+1",   "Meal": "CP",  "Checkout": "13-Jun", "Source": "Voiz Tele",      "SPL": "Mixed veg / egg allergy"},
    {"Room": "717",     "Guest": "Mr. Ashish Gupta",        "ETA": "15:00", "Rooms/Pax": "1/3 Pax", "Meal": "MAP", "Checkout": "12-Jun", "Source": "Hemant Delhi",   "SPL": "—"},
    {"Room": "610",     "Guest": "Mr. Karan Kanal",         "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "MakeMyTrip",     "SPL": "—"},
    {"Room": "611",     "Guest": "Mr. Ryaan Konwar",        "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "Booking.com",    "SPL": "—"},
    {"Room": "614",     "Guest": "Ms. Puru Mittal",         "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "MAP", "Checkout": "12-Jun", "Source": "MakeMyTrip",     "SPL": "—"},
    {"Room": "710",     "Guest": "Ms. Swathi Vemula",       "ETA": "15:00", "Rooms/Pax": "1/2+1",   "Meal": "CP",  "Checkout": "12-Jun", "Source": "Booking.com",    "SPL": "—"},
    {"Room": "104",     "Guest": "Mr. Rahul Varadareddi",   "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "13-Jun", "Source": "Brand Website",  "SPL": "—"},
    {"Room": "516,517", "Guest": "Ms. Anita Cheryl Miller", "ETA": "15:00", "Rooms/Pax": "2/3 Pax", "Meal": "CP",  "Checkout": "11-Jun", "Source": "Spandana Tele",  "SPL": "—"},
    {"Room": "511",     "Guest": "Mr. Amal Rastogi",        "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "MAP", "Checkout": "12-Jun", "Source": "Praveen Cochin", "SPL": "—"},
    {"Room": "205",     "Guest": "Mr. Jaydeep Sinh Rathod", "ETA": "15:00", "Rooms/Pax": "1/3+1",   "Meal": "MAP", "Checkout": "13-Jun", "Source": "Sudeena Tele",   "SPL": "—"},
    {"Room": "701",     "Guest": "Mr. Suman Routray",       "ETA": "12:00", "Rooms/Pax": "1/3 Pax", "Meal": "MAP", "Checkout": "11-Jun", "Source": "Booking.com",    "SPL": "ETA 12pm"},
    {"Room": "223",     "Guest": "Mr. Gurmesh Sabharwal",   "ETA": "15:00", "Rooms/Pax": "1/2+2",   "Meal": "MAP", "Checkout": "14-Jun", "Source": "MakeMyTrip",     "SPL": "Long Stay 4N / Non veg"},
    {"Room": "510",     "Guest": "Mr. Prashant Goel",       "ETA": "15:00", "Rooms/Pax": "1/2+1",   "Meal": "CP",  "Checkout": "11-Jun", "Source": "MakeMyTrip",     "SPL": "—"},
    {"Room": "224",     "Guest": "Mr. Madhav Trivedi",      "ETA": "17:00", "Rooms/Pax": "1/2+1",   "Meal": "CP",  "Checkout": "14-Jun", "Source": "MakeMyTrip",     "SPL": "Pure veg / Long Stay 4N"},
    {"Room": "720",     "Guest": "Mr. Amit Divaker",        "ETA": "15:00", "Rooms/Pax": "1/3 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "Cleartrip",      "SPL": "—"},
    {"Room": "201",     "Guest": "Mr. Anuj Narula",         "ETA": "15:00", "Rooms/Pax": "1/2+1",   "Meal": "CP",  "Checkout": "13-Jun", "Source": "Sudeena Tele",   "SPL": "—"},
    {"Room": "601,705", "Guest": "Ms. Ashwini Nikam",       "ETA": "16:00", "Rooms/Pax": "2/4 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "Booking.com",    "SPL": "No pork"},
    {"Room": "101",     "Guest": "Mr. Prakash Pagaria",     "ETA": "14:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "13-Jun", "Source": "Joseph Mumbai",  "SPL": "Pure veg / 75th Bday"},
    {"Room": "310,311", "Guest": "Mr. Hasmukh Parmar",      "ETA": "12:00", "Rooms/Pax": "1/2+1",   "Meal": "MAP", "Checkout": "12-Jun", "Source": "MakeMyTrip",     "SPL": "Family vacation"},
    {"Room": "714",     "Guest": "Mr. Vikas Pathak",        "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "Booking.com",    "SPL": "—"},
    {"Room": "214",     "Guest": "Mr. Praveen Patil",       "ETA": "15:00", "Rooms/Pax": "1/1+1",   "Meal": "AP",  "Checkout": "12-Jun", "Source": "Joseph Mumbai",  "SPL": "—"},
    {"Room": "215",     "Guest": "Ms. Chari P.L",           "ETA": "15:00", "Rooms/Pax": "1/3+2",   "Meal": "MAP", "Checkout": "13-Jun", "Source": "Praveen Cochin", "SPL": "—"},
    {"Room": "204",     "Guest": "Ms. Shikha Bhatia",       "ETA": "15:00", "Rooms/Pax": "1/1 Pax", "Meal": "CP",  "Checkout": "12-Jun", "Source": "Brand Website",  "SPL": "—"},
    {"Room": "617",     "Guest": "Ms. Srivathsan Balaguru", "ETA": "15:00", "Rooms/Pax": "1/2+1",   "Meal": "CP",  "Checkout": "11-Jun", "Source": "Booking.com",    "SPL": "—"},
    {"Room": "411",     "Guest": "Mr. Aditi Warnoolkar",    "ETA": "15:00", "Rooms/Pax": "1/2 Pax", "Meal": "CP",  "Checkout": "13-Jun", "Source": "Brand Website",  "SPL": "—"},
]

# Room rates
ROOM_RATES = {
    "Coorg Wilderness": {
        "Wilderness Grove View Suite": 25500,
        "Wilderness Hill View Suite":  28500,
        "Grand Grove View Suite":      31500,
        "Grand Hill View Suite":       36500,
        "Extra Adult":                  6000,
        "Extra Child":                  4500,
    },
    "The Paul, Bengaluru": {
        "Luxury Room":      18000,
        "Deluxe Suite":     28000,
        "Premier Suite":    38000,
        "Presidential":     65000,
        "Extra Adult":       5000,
        "Extra Child":       3500,
    },
    "Fort Kochi": {
        "Heritage Room":     14000,
        "Superior Room":     18000,
        "Lagoon Suite":      24000,
        "Extra Adult":        4500,
        "Extra Child":        3000,
    },
    "Kumarakom Lake Resort": {
        "Deluxe Room":       15000,
        "Superior Room":     20000,
        "Grand Suite":       32000,
        "Presidential Suite":55000,
        "Extra Adult":        5000,
        "Extra Child":        3500,
    },
}

# Weekly data — Coorg Wilderness (from screenshot)
WEEKLY = {
    "Coorg Wilderness": {
        "Fri 11": (85, 81.73), "Sat 12": (95, 91.35), "Sun 13": (100, 96.15),
        "Mon 14": (72, 69.23), "Tue 15": (60, 57.69), "Tue 16": (43, 41.35), "Wed 17": (34, 32.69),
    },
    "The Paul, Bengaluru": {
        "Fri 11": (110, 91.7), "Sat 12": (117, 97.5), "Sun 13": (112, 93.3),
        "Mon 14": (108, 90.0), "Tue 15": (100, 83.3), "Tue 16": (95, 79.2), "Wed 17": (88, 73.3),
    },
    "Fort Kochi": {
        "Fri 11": (58, 89.2), "Sat 12": (63, 96.9), "Sun 13": (61, 93.8),
        "Mon 14": (50, 76.9), "Tue 15": (45, 69.2), "Tue 16": (40, 61.5), "Wed 17": (35, 53.8),
    },
    "Kumarakom Lake Resort": {
        "Fri 11": (84, 93.3), "Sat 12": (88, 97.8), "Sun 13": (85, 94.4),
        "Mon 14": (80, 88.9), "Tue 15": (74, 82.2), "Tue 16": (68, 75.6), "Wed 17": (60, 66.7),
    },
}

# Packages — Coorg Wilderness
PACKAGES = [
    {"Package": "Transfer Package",      "Arrivals": "—", "Inhouse": "—",
     "Inclusions": "MAP Meal Plan. Guided in-house activities. Round trip transportation from Bangalore, Mangalore and Kannur."},
    {"Package": "Adventure Package",     "Arrivals": "—", "Inhouse": "125 – Mr. Pilla Ravinder Malleswara Rao",
     "Inclusions": "AP Meal Plan. Guided in-house activities & adventure activities, Quad Biking, Jeep ride to the coffee plantation once during the stay."},
    {"Package": "Wellness Package",      "Arrivals": "—", "Inhouse": "—",
     "Inclusions": "AP Meal Plan. Guided in-house activities. 3 Days Nikaay spa Therapy."},
    {"Package": "Rejuvenation Package",  "Arrivals": "—", "Inhouse": "—",
     "Inclusions": "AP Meal Plan. Guided in-house activities & Rejuvenation Treatment."},
    {"Package": "Honeymoon Package",     "Arrivals": "—", "Inhouse": "—",
     "Inclusions": "Complimentary bottle of Indian wine, rich chocolate cake & exotic fruits basket. Candlelight 4-course dinner at Habba on Day 2. Floral bed decoration. 60-min Swedish therapy at Nikaay Spa."},
    {"Package": "Jain Food Guests",      "Arrivals": "—", "Inhouse": "—",
     "Inclusions": "Potatoes, Onions, Garlic, Carrots which all grow in the Roots."},
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def fmt_inr(val):
    if val >= 10000000:
        return f"₹{val/10000000:.2f} Cr"
    elif val >= 100000:
        return f"₹{val/100000:.2f} L"
    else:
        return f"₹{val:,.0f}"

def variance_color(v):
    return "green" if v >= 0 else "red"

def rev_bar_chart(categories, actual, budget, color):
    fig = go.Figure()
    fig.add_bar(name="Actual", x=categories, y=actual,
                marker_color=color, opacity=0.85)
    fig.add_bar(name="Budget", x=categories, y=budget,
                marker_color="#bdbdbd", opacity=0.7)
    fig.update_layout(
        barmode="group", height=280, margin=dict(l=10, r=10, t=10, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        yaxis=dict(tickformat=",.0f", title=""),
        plot_bgcolor="#fdf8f2", paper_bgcolor="#f5ede0",
        font=dict(size=11),
    )
    return fig

def hex_to_rgba(hex_color, alpha=0.12):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def occ_line_chart(data, color):
    df = pd.DataFrame(data, columns=["Date", "Day", "Occ", "Pct"])
    fig = go.Figure()
    fig.add_scatter(x=df["Date"], y=df["Pct"], mode="lines+markers",
                    line=dict(color=color, width=2),
                    marker=dict(size=5),
                    fill="tozeroy", fillcolor=hex_to_rgba(color),
                    name="Occupancy %")
    fig.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=30),
        yaxis=dict(range=[0, 110], title="%", ticksuffix="%"),
        xaxis=dict(title=""),
        plot_bgcolor="#fdf8f2", paper_bgcolor="#f5ede0",
        font=dict(size=11), showlegend=False,
    )
    return fig

def weekly_bar(weekly_data, color):
    labels = list(weekly_data.keys())
    closing = [v[0] for v in weekly_data.values()]
    occ_pct = [v[1] for v in weekly_data.values()]
    fig = go.Figure()
    fig.add_bar(x=labels, y=closing, name="Closing Rooms", marker_color=color, opacity=0.8)
    fig.add_scatter(x=labels, y=occ_pct, name="Occ %", yaxis="y2",
                    line=dict(color="#ff6f00", width=2), mode="lines+markers")
    fig.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=30),
        yaxis=dict(title="Rooms"),
        yaxis2=dict(title="Occ %", overlaying="y", side="right", range=[0, 110], ticksuffix="%"),
        plot_bgcolor="#fdf8f2", paper_bgcolor="#f5ede0",
        font=dict(size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    return fig

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="pj-header">
  <h1>🏨 Paul John Group of Hotels</h1>
  <p>Operations Dashboard &nbsp;|&nbsp; Date: 10 June 2026 &nbsp;|&nbsp; Welcome, Harry</p>
</div>
""", unsafe_allow_html=True)

# ── HOTEL TABS ────────────────────────────────────────────────────────────────

tabs = st.tabs(list(HOTELS.keys()))

for tab, (hotel_key, hotel_info) in zip(tabs, HOTELS.items()):
    with tab:
        color = hotel_info["color"]
        rooms_total = hotel_info["rooms"]
        hs = HOUSE_STATUS[hotel_key]
        kpi = KPIS[hotel_key]
        rev_day = REVENUE_DAY[hotel_key]
        rev_mtd = REVENUE_MTD[hotel_key]
        pace = PACE[hotel_key]
        occ_data = HOTEL_OCC_DATA[hotel_key]
        meal = MEAL_PLANS[hotel_key]
        rates = ROOM_RATES[hotel_key]
        weekly = WEEKLY[hotel_key]

        total_actual_day = sum(rev_day["actual"])
        total_budget_day = sum(rev_day["budget"])
        total_var_day    = total_actual_day - total_budget_day
        total_actual_mtd = sum(rev_mtd["actual"])
        total_budget_mtd = sum(rev_mtd["budget"])
        total_var_mtd    = total_actual_mtd - total_budget_mtd

        st.markdown(f"**{hotel_info['full_name']}** &nbsp;·&nbsp; {hotel_info['location']} &nbsp;·&nbsp; {rooms_total} Rooms")
        st.markdown("")

        # ── KPI ROW ───────────────────────────────────────────────────────────

        st.markdown('<div class="section-hdr">Today at a Glance — 10 June 2026</div>', unsafe_allow_html=True)
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Occupancy", f"{kpi['Occ%']}%")
        k2.metric("ARR", f"₹{kpi['ARR']:,}")
        k3.metric("RevPAR", f"₹{kpi['RevPAR']:,}")
        k4.metric("Closing Rooms", kpi["Closing"])
        k5.metric("Total Revenue", fmt_inr(total_actual_day),
                  delta=fmt_inr(total_var_day),
                  delta_color="normal" if total_var_day >= 0 else "inverse")
        k6.metric("MTD Revenue", fmt_inr(total_actual_mtd),
                  delta=fmt_inr(total_var_mtd),
                  delta_color="normal" if total_var_mtd >= 0 else "inverse")

        st.markdown("")

        # ── HOUSE STATUS + MEAL PLAN ──────────────────────────────────────────

        col_hs, col_mp, col_rates = st.columns([1.2, 1.5, 1.3])

        with col_hs:
            st.markdown('<div class="section-hdr">House Status</div>', unsafe_allow_html=True)
            for label, val in hs.items():
                icon = {"Arrivals": "🟢", "Departures": "🔴", "Stayovers": "🟡", "Closing": "🔵"}[label]
                st.markdown(f"{icon} **{label}** &nbsp; `{val}`")

        with col_mp:
            st.markdown('<div class="section-hdr">Meal Plan Breakdown</div>', unsafe_allow_html=True)
            mp_df = pd.DataFrame([
                {"Plan": plan, "Stayover RM": v["Stayover RM"], "Arrival RM": v["Arrival RM"],
                 "Total": v["Stayover RM"] + v["Arrival RM"]}
                for plan, v in meal.items()
            ])
            st.dataframe(mp_df, use_container_width=True, hide_index=True,
                         column_config={"Plan": st.column_config.TextColumn(width="small")})

        with col_rates:
            st.markdown('<div class="section-hdr">Room Rates (₹ / night)</div>', unsafe_allow_html=True)
            for cat, rate in rates.items():
                st.markdown(f"**{cat}** — ₹{rate:,}")

        st.markdown("")

        # ── REVENUE ───────────────────────────────────────────────────────────

        st.markdown('<div class="section-hdr">Revenue — For the Day vs Budget</div>', unsafe_allow_html=True)
        col_chart, col_table = st.columns([2, 1.2])

        with col_chart:
            st.plotly_chart(
                rev_bar_chart(REV_CATEGORIES, rev_day["actual"], rev_day["budget"], color),
                use_container_width=True,
            )

        with col_table:
            rev_rows = []
            for i, cat in enumerate(REV_CATEGORIES):
                a = rev_day["actual"][i]
                b = rev_day["budget"][i]
                v = a - b
                rev_rows.append({"Category": cat.replace(" Revenue", ""),
                                  "Actual": fmt_inr(a),
                                  "Budget": fmt_inr(b),
                                  "Var": ("+" if v >= 0 else "") + fmt_inr(v)})
            rev_rows.append({"Category": "TOTAL",
                              "Actual": fmt_inr(total_actual_day),
                              "Budget": fmt_inr(total_budget_day),
                              "Var": ("+" if total_var_day >= 0 else "") + fmt_inr(total_var_day)})
            st.dataframe(pd.DataFrame(rev_rows), use_container_width=True, hide_index=True)

        # MTD Revenue summary
        st.markdown('<div class="section-hdr">Revenue — Month to Date</div>', unsafe_allow_html=True)
        mtd_cols = st.columns(4)
        mtd_items = [
            ("Room Revenue", sum([rev_mtd["actual"][0]]), rev_mtd["budget"][0]),
            ("F&B Revenue",  rev_mtd["actual"][1],        rev_mtd["budget"][1]),
            ("Total Revenue", total_actual_mtd,            total_budget_mtd),
            ("Variance",      total_var_mtd,               None),
        ]
        for col, (label, actual, budget) in zip(mtd_cols, mtd_items):
            if budget is not None:
                var = actual - budget
                col.metric(label, fmt_inr(actual),
                           delta=fmt_inr(var),
                           delta_color="normal" if var >= 0 else "inverse")
            else:
                col.metric(label, ("+" if actual >= 0 else "") + fmt_inr(actual))

        st.markdown("")

        # ── OCCUPANCY CHART ───────────────────────────────────────────────────

        st.markdown('<div class="section-hdr">June 2026 Occupancy</div>', unsafe_allow_html=True)
        col_occ, col_weekly = st.columns([2, 1.5])

        with col_occ:
            st.plotly_chart(occ_line_chart(occ_data, color), use_container_width=True)
            # Occupancy table
            occ_df = pd.DataFrame(occ_data, columns=["Date", "Day", "Occ Rooms", "Occ %"])
            occ_df["Occ %"] = occ_df["Occ %"].astype(str) + "%"
            occ_df["Inventory"] = rooms_total
            with st.expander("Full Month Occupancy Table"):
                st.dataframe(occ_df, use_container_width=True, hide_index=True)

        with col_weekly:
            st.markdown('<div class="section-hdr">Weekly Wise (11–17 Jun)</div>', unsafe_allow_html=True)
            st.plotly_chart(weekly_bar(weekly, color), use_container_width=True)
            wk_df = pd.DataFrame([
                {"Day": k, "Closing": v[0], "Occ %": f"{v[1]}%"}
                for k, v in weekly.items()
            ])
            st.dataframe(wk_df, use_container_width=True, hide_index=True)

        st.markdown("")

        # ── RESERVATION PACE ──────────────────────────────────────────────────

        st.markdown('<div class="section-hdr">Reservation Pace — June 2026</div>', unsafe_allow_html=True)
        p1, p2, p3, p4, p5, p6 = st.columns(6)
        p1.metric("Budgeted RN",   f"{pace['Budgeted RN']:,}")
        p2.metric("Actual BOB RN", f"{pace['Actual BOB RN']:,}",
                  delta=str(pace["Actual BOB RN"] - pace["Budgeted RN"]),
                  delta_color="normal" if pace["Actual BOB RN"] >= pace["Budgeted RN"] else "inverse")
        p3.metric("Budgeted ARR",  f"₹{pace['Budgeted ARR']:,}")
        p4.metric("Actual ARR BOB",f"₹{pace['Actual ARR BOB']:,}",
                  delta=f"₹{pace['Actual ARR BOB'] - pace['Budgeted ARR']:,}",
                  delta_color="normal" if pace["Actual ARR BOB"] >= pace["Budgeted ARR"] else "inverse")
        p5.metric("Current Pace",  f"{pace['Current Pace']} rooms/day")
        p6.metric("Required Pace", f"{pace['Required Pace']} rooms/day")

        pp1, pp2 = st.columns(2)
        pp1.metric("Budgeted Revenue", fmt_inr(pace["Budgeted Revenue"]))
        pp2.metric("Actual Revenue BOB", fmt_inr(pace["Actual Revenue"]),
                   delta=fmt_inr(pace["Actual Revenue"] - pace["Budgeted Revenue"]),
                   delta_color="normal" if pace["Actual Revenue"] >= pace["Budgeted Revenue"] else "inverse")

        st.markdown("")

        # ── ARRIVALS (Coorg only shows real data; others show placeholder) ───

        st.markdown('<div class="section-hdr">Today\'s Arrivals</div>', unsafe_allow_html=True)

        if hotel_key == "Coorg Wilderness":
            arr_df = pd.DataFrame(COORG_ARRIVALS)
            st.dataframe(
                arr_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Room":      st.column_config.TextColumn("Room", width="small"),
                    "Guest":     st.column_config.TextColumn("Guest Name", width="medium"),
                    "ETA":       st.column_config.TextColumn("ETA", width="small"),
                    "Rooms/Pax": st.column_config.TextColumn("Rooms/Pax", width="small"),
                    "Meal":      st.column_config.TextColumn("Meal Plan", width="small"),
                    "Checkout":  st.column_config.TextColumn("Checkout", width="small"),
                    "Source":    st.column_config.TextColumn("Source", width="medium"),
                    "SPL":       st.column_config.TextColumn("Special Request", width="large"),
                },
            )
        else:
            st.info(f"Arrival grid for {hotel_info['full_name']} — connect live PMS data to populate.")

        st.markdown("")

        # ── SPECIAL PACKAGES (Coorg only) ─────────────────────────────────────

        if hotel_key == "Coorg Wilderness":
            st.markdown('<div class="section-hdr">Special Package Guests</div>', unsafe_allow_html=True)
            for pkg in PACKAGES:
                with st.expander(f"**{pkg['Package']}** — Arrivals: {pkg['Arrivals']} | Inhouse: {pkg['Inhouse']}"):
                    st.markdown(f"**Inclusions:** {pkg['Inclusions']}")

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.divider()
st.caption("Paul John Group of Hotels — Operations Dashboard · Built by Vinya AI · Data as of 10-Jun-2026")
