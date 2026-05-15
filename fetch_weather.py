#!/usr/bin/env python3
"""
fetch_weather.py — Récupère les données de la station Weatherlink v2
Trouve automatiquement l'ID de station — plus besoin de le configurer.

Secrets GitHub requis (2 seulement) :
  WEATHERLINK_API_KEY    → clé API v2
  WEATHERLINK_API_SECRET → secret API v2
"""
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_KEY    = os.environ.get("WEATHERLINK_API_KEY", "").strip()
API_SECRET = os.environ.get("WEATHERLINK_API_SECRET", "").strip()

if not API_KEY or not API_SECRET:
    print("❌  Secrets manquants : WEATHERLINK_API_KEY et/ou WEATHERLINK_API_SECRET")
    sys.exit(1)

def signature(params_str):
    return hmac.new(
        API_SECRET.encode("utf-8"),
        params_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def appel_api(endpoint):
    t      = int(time.time())
    params = {"api-key": API_KEY, "t": str(t)}
    chaine = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    params["api-signature"] = signature(chaine)
    query  = "&".join(f"{k}={v}" for k, v in params.items())
    url    = f"https://api.weatherlink.com/v2/{endpoint}?{query}"
    req    = urllib.request.Request(url, headers={"User-Agent": "meteo-college/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

# Étape 1 : découverte automatique de la station
print("🔍 Recherche des stations disponibles...")
try:
    stations_data = appel_api("stations")
except urllib.error.HTTPError as e:
    print(f"❌  Erreur HTTP {e.code} : {e.reason}")
    print("    → Vérifiez WEATHERLINK_API_KEY et WEATHERLINK_API_SECRET dans vos secrets GitHub")
    sys.exit(1)
except Exception as e:
    print(f"❌  Erreur réseau : {e}")
    sys.exit(1)

stations = stations_data.get("stations", [])
if not stations:
    print("❌  Aucune station trouvée sur ce compte Weatherlink")
    sys.exit(1)

station    = stations[0]
station_id = station.get("station_id") or station.get("station_id_uuid")
nom        = station.get("station_name", "Station inconnue")
print(f"✅  Station trouvée : {nom} (ID: {station_id})")

# Étape 2 : données actuelles
print("🌡️  Récupération des données météo...")
try:
    data = appel_api(f"current/{station_id}")
except urllib.error.HTTPError as e:
    print(f"❌  Erreur HTTP {e.code} lors de la récupération des données")
    sys.exit(1)
except Exception as e:
    print(f"❌  Erreur réseau : {e}")
    sys.exit(1)

t_now = int(time.time())
data["_fetched_at"]   = time.strftime("%d/%m/%Y à %H:%M", time.localtime(t_now))
data["_fetched_ts"]   = t_now
data["_station_name"] = nom
data["_placeholder"]  = False

out = os.path.join(os.path.dirname(__file__), "data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅  data.json mis à jour — {data['_fetched_at']}")
