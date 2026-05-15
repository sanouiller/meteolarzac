#!/usr/bin/env python3
"""
fetch_weather.py — Récupère les données Weatherlink v2
Secrets GitHub requis : WEATHERLINK_API_KEY, WEATHERLINK_API_SECRET
"""
import hashlib, hmac, json, os, sys, time, urllib.error, urllib.request

API_KEY    = os.environ.get("WEATHERLINK_API_KEY",    "").strip()
API_SECRET = os.environ.get("WEATHERLINK_API_SECRET", "").strip()

if not API_KEY or not API_SECRET:
    print("❌  Secrets manquants : WEATHERLINK_API_KEY et/ou WEATHERLINK_API_SECRET")
    sys.exit(1)

def sig(params: dict) -> str:
    """Signature HMAC-SHA256 : concaténation triée clé+valeur (sans & ni =)"""
    chaine = "".join(f"{k}{v}" for k, v in sorted(params.items()))
    return hmac.new(API_SECRET.encode(), chaine.encode(), hashlib.sha256).hexdigest()

def appel_api(path: str, params_sig: dict = None) -> dict:
    """
    Appelle https://api.weatherlink.com/v2/{path}
    params_sig : paramètres inclus dans le calcul de signature
                 (api-key et t sont ajoutés automatiquement)
    """
    t = int(time.time())
    p = {"api-key": API_KEY, "t": str(t)}
    if params_sig:
        p.update(params_sig)

    p["api-signature"] = sig(p)
    query = "&".join(f"{k}={v}" for k, v in p.items())
    url   = f"https://api.weatherlink.com/v2/{path}?{query}"

    req = urllib.request.Request(url, headers={"User-Agent": "meteo-college/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌  Erreur HTTP {e.code} ({e.reason}) sur /v2/{path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌  Erreur réseau : {e}")
        sys.exit(1)

# ── 1. Découverte de la station ───────────────────────────────────────────────
print("🔍 Recherche de la station...")
data_stations = appel_api("stations")
stations = data_stations.get("stations", [])
if not stations:
    print("❌  Aucune station trouvée sur ce compte Weatherlink"); sys.exit(1)

station    = stations[0]
station_id = str(station.get("station_id", ""))
nom        = station.get("station_name", "Station inconnue")
print(f"✅  Station : {nom} (ID: {station_id})")

# ── 2. Données actuelles (station-id doit être dans la signature) ─────────────
print("🌡️  Récupération des données météo...")
data = appel_api(f"current/{station_id}", params_sig={"station-id": station_id})

# ── 3. Sauvegarde ─────────────────────────────────────────────────────────────
t_now = int(time.time())
data["_fetched_at"]   = time.strftime("%d/%m/%Y à %H:%M", time.localtime(t_now))
data["_fetched_ts"]   = t_now
data["_station_name"] = nom
data["_placeholder"]  = False

out = os.path.join(os.path.dirname(__file__), "data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅  data.json mis à jour — {data['_fetched_at']}")
