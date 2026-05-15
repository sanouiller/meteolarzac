#!/usr/bin/env python3
"""
fetch_weather.py — Récupère les données de la station Weatherlink v2
et les enregistre dans data.json à la racine du dépôt.

Appelé automatiquement par GitHub Actions toutes les 15 minutes.
Variables d'environnement requises (GitHub Secrets) :
  WEATHERLINK_API_KEY    → clé API v2
  WEATHERLINK_API_SECRET → secret API v2
  WEATHERLINK_STATION_ID → identifiant numérique de la station
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
STATION_ID = os.environ.get("WEATHERLINK_STATION_ID", "").strip()

if not all([API_KEY, API_SECRET, STATION_ID]):
    print("❌  Variables manquantes : WEATHERLINK_API_KEY / API_SECRET / STATION_ID")
    sys.exit(1)

# Signature HMAC-SHA256 obligatoire pour l'API Weatherlink v2
t         = int(time.time())
message   = f"api-key{API_KEY}t{t}"
signature = hmac.new(
    API_SECRET.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256,
).hexdigest()

params = f"api-key={API_KEY}&t={t}&api-signature={signature}"
url    = f"https://api.weatherlink.com/v2/current/{STATION_ID}?{params}"

try:
    req = urllib.request.Request(url, headers={"User-Agent": "meteo-college/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"❌  Erreur HTTP {e.code} : {e.reason}")
    sys.exit(1)
except Exception as e:
    print(f"❌  Erreur réseau : {e}")
    sys.exit(1)

# Métadonnées d'horodatage lisibles
data["_fetched_at"] = time.strftime("%d/%m/%Y à %H:%M", time.localtime(t))
data["_fetched_ts"] = t
data["_placeholder"] = False

# Écriture dans data.json à la racine du dépôt
out = os.path.join(os.path.dirname(__file__), "data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅  data.json mis à jour — {data['_fetched_at']}")
