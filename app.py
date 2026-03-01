import json
import time
import threading
import math
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

CHECK_INTERVAL = 5
API_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"

GEO_CACHE_FILE = "geo_cache.json"
HISTORY_FILE = "history.json"
CITIES_FILE = "cities_coords.json"

USER_AGENT = "Mozilla/5.0"

ALERT_TYPE_MAP = {
    1: "ירי רקטות",
    2: "חדירת מחבלים",
    3: "רעידת אדמה",
    4: "חדירת כלי טיס",
    5: "חדירת כלי שיט",
    6: "חדירת כלי טיס עוין",
    7: "ירי בליסטי",
    8: "נפילת כטב״מ",
    9: "חדירת רחפן",
    10: "ירי רקטות",
}

ALERT_TIME_BY_REGION = {
    "דרום": 15,
    "מרכז": 60,
    "צפון": 60,
    "צפון רחוק": 90,
}

LAUNCH_POINTS = {
    "עזה": (31.5, 34.5),
    "לבנון": (33.2, 35.3),
    "איראן": (32.0, 53.0),
    "תימן": (15.5, 48.5),
}

def load_json_safe(path, default):
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except:
        return default

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

geo_cache = load_json_safe(GEO_CACHE_FILE, {})
history = load_json_safe(HISTORY_FILE, [])
CITY_COORDS = load_json_safe(CITIES_FILE, {})

latest = {"ts": None, "cities": [], "type": None, "coords": []}
state_lock = threading.Lock()

def now_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def classify_region(lat):
    if lat < 31.3:
        return "דרום"
    elif lat < 32.3:
        return "מרכז"
    elif lat < 33.0:
        return "צפון"
    return "צפון רחוק"

def alert_time_for_lat(lat):
    region = classify_region(lat)
    return ALERT_TIME_BY_REGION.get(region, 60), region

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def choose_visual_source(lat, lon):
    best = None
    best_d = 1e18
    for name, (slat, slon) in LAUNCH_POINTS.items():
        d = haversine(slat, slon, lat, lon)
        if d < best_d:
            best_d = d
            best = name
    return best or "עזה"

def fetch_alerts():
    try:
        r = requests.get(
            API_URL,
            headers={
                "User-Agent": USER_AGENT,
                "Referer": "https://www.oref.org.il/",
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=5
        )

        print("====== OREF DEBUG ======")
        print("STATUS:", r.status_code)
        print("HEADERS:", r.headers)
        print("BODY (first 300 chars):", r.text[:300])
        print("========================")

        if r.status_code != 200:
            return [], None

        data = json.loads(r.content.decode("utf-8-sig"))
        cities = data.get("data") or []

        cat = data.get("cat")
        try:
            cat = int(cat)
        except:
            cat = None

        category = ALERT_TYPE_MAP.get(cat, "אירוע ביטחוני")

        if isinstance(cities, str):
            cities = [c.strip() for c in cities.split(",") if c.strip()]

        return cities, category

    except Exception as e:
        print("FETCH ERROR:", e)
        return [], None
    
def geocode_city(city):
    if city in geo_cache:
        v = geo_cache[city]
        return float(v["lat"]), float(v["lon"])

    if city in CITY_COORDS:
        v = CITY_COORDS[city]
        lat = float(v["lat"])
        lon = float(v["lon"])
        geo_cache[city] = {"lat": lat, "lon": lon}
        save_json(GEO_CACHE_FILE, geo_cache)
        return lat, lon

    return None

def cleanup_history():
    now = datetime.now()
    with state_lock:
        history[:] = [
            ev for ev in history
            if (now - datetime.strptime(ev["ts"], "%Y-%m-%d %H:%M:%S")).total_seconds() < 900
        ]
        save_json(HISTORY_FILE, history)

def build_event(cities, event_type):
    coords = []

    for city in cities:
        res = geocode_city(city)
        if not res:
            continue

        lat, lon = res
        shelter, region = alert_time_for_lat(lat)
        source = choose_visual_source(lat, lon)

        coords.append({
            "name": city,
            "lat": lat,
            "lon": lon,
            "region": region,
            "shelter_seconds": shelter,
            "type": event_type,
            "source": source
        })

    return {
        "ts": now_ts(),
        "cities": cities,
        "coords": coords,
        "type": event_type
    }

def push_event(event):
    with state_lock:
        history.append(event)

        latest.update({
            "ts": event["ts"],
            "cities": event["cities"],
            "type": event["type"],
            "coords": event["coords"]
        })

        save_json(HISTORY_FILE, history)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/state")
def api_state():
    return jsonify({
        "latest": latest,
        "history": history
    })

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.json or {}
    cities = data.get("cities", [])

    if not cities:
        return {"status": "no data"}

    event = build_event(cities, "ירי רקטות")
    push_event(event)
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
