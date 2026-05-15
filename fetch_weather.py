#!/usr/bin/env python3
"""
fetch_weather.py — Récupère les données Weatherlink v2
Auth : api-key en query string + X-Api-Secret en header HTTP

Secrets GitHub requis :
  WEATHERLINK_API_KEY    → clé API v2
  WEATHERLINK_API_SECRET → secret API v2
"""
import json, os, sys, time, urllib.error, urllib.request

API_KEY    = os.environ.get("WEATHERLINK_API_KEY",    "").strip()
API_SECRET = os.environ.get("WEATHERLINK_API_SECRET", "").strip()

if not API_KEY or not API_SECRET:
    print("❌  Secrets manquants : WEATHERLINK_API_KEY et/ou WEATHERLINK_API_SECRET")
    sys.exit(1)

HEADERS = {
    "User-Agent":   "meteo-college/1.0",
    "X-Api-Secret": API_SECRET,          # ← authentification par header
}

def appel_api(path):
    url = f"https://api.weatherlink.com/v2/{path}?api-key={API_KEY}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌  Erreur HTTP {e.code} ({e.reason}) sur /v2/{path}")
        print("    → Vérifiez WEATHERLINK_API_KEY et WEATHERLINK_API_SECRET")
        sys.exit(1)
    except Exception as e:
        print(f"❌  Erreur réseau : {e}")
        sys.exit(1)

# ── 1. Découverte de la station ───────────────────────────────
print("🔍 Recherche de la station...")
stations = appel_api("stations").get("stations", [])
if not stations:
    print("❌  Aucune station trouvée sur ce compte Weatherlink")
    sys.exit(1)

station    = stations[0]
station_id = str(station.get("station_id", ""))
nom        = station.get("station_name", "Station inconnue")
print(f"✅  Station : {nom} (ID: {station_id})")

# ── 2. Données actuelles ──────────────────────────────────────
print("🌡️  Récupération des données météo...")
data = appel_api(f"current/{station_id}")

# ── 3. Sauvegarde ─────────────────────────────────────────────
t_now = int(time.time())
data["_fetched_at"]   = time.strftime("%d/%m/%Y à %H:%M", time.localtime(t_now))
data["_fetched_ts"]   = t_now
data["_station_name"] = nom
data["_placeholder"]  = False

out = os.path.join(os.path.dirname(__file__), "data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅  data.json mis à jour — {data['_fetched_at']}")
