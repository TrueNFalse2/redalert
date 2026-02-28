# 🛡️ Red Alert Pro – Live Threat Visualization System

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-Production-green)
![Status](https://img.shields.io/badge/Status-Live-success)
![Deployment](https://img.shields.io/badge/Deployed-Railway-purple)

Real-time Israeli Home Front Command alert monitoring system built with **Flask + Leaflet.js**, featuring live missile trajectory animation, threat classification, and dynamic alert visualization.

---

## 🚀 Live Demo

🌐 **Live Website:**  
👉 https://redalert-production-0c4a.up.railway.app/

---

## 🎯 Features

- ✅ Real-time OREF alert monitoring  
- ✅ Missile trajectory animation  
- ✅ Threat type detection (Rockets, UAV, Earthquake, Infiltration)  
- ✅ Launch source estimation (Gaza, Lebanon, Iran, Yemen)  
- ✅ Regional shelter time calculation  
- ✅ Dynamic red alert radius visualization  
- ✅ Live browser siren  
- ✅ Simulation mode  
- ✅ Automatic cleanup of expired alerts  
- ✅ Cloud deployed (Railway)

---

## 🧠 Alert Types Supported

| Code | Event Type |
|------|------------|
| 1 | Rocket Fire |
| 2 | Terror Infiltration |
| 3 | Earthquake |
| 4 | Aircraft Infiltration |
| 5 | Naval Infiltration |
| 6 | Hostile Aircraft |
| 7 | Ballistic Missile |
| 8 | UAV Impact |
| 9 | Drone Infiltration |
| 10 | Rocket Fire |

---

## 🗺️ Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML + CSS + Vanilla JS
- **Maps:** Leaflet.js
- **Server:** Gunicorn
- **Deployment:** Railway (Cloud)
- **API Source:** OREF Home Front Command

---

## 📂 Project Structure


redalert/
│
├── app.py
├── requirements.txt
├── history.json
├── geo_cache.json
├── cities_coords.json
├── siren.mp3
│
└── templates/
└── index.html


---

## ⚙️ How It Works

1. Backend polls OREF API every 5 seconds
2. New alerts are classified
3. City coordinates are resolved
4. Event stored in memory
5. Frontend fetches `/api/state`
6. Missile animation rendered
7. Siren plays in browser
8. Map auto-adjusts to active threat zone

---

## 🧪 Simulation Mode

Trigger simulation via:


POST /simulate


Simulates alert for:
- Ashkelon
- Sderot
- Tel Aviv

---

## 🔥 Deployment Configuration

Start command:


gunicorn app:app --bind 0.0.0.0:$PORT


Production requirements:


Flask
requests
gunicorn


---

## 📌 Notes

- Server-side audio disabled (browser handles siren)
- Optimized for cloud deployment
- Designed for educational & visualization purposes
- Fully GitHub-integrated CI deployment

---

## 👨‍💻 Author

**Lior Rimon**  
B.A. Information Systems Management  
Cybersecurity & Cloud Enthusiast  
