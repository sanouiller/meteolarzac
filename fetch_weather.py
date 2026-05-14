import hmac
import hashlib
import time
import requests
import json
import os
import sys

# Récupération des variables d'environnement (configurées dans GitHub Secrets)
api_key    = os.environ.get('WEATHERLINK_API_KEY', '')
api_secret = os.environ.get('WEATHERLINK_API_SECRET', '')
station_id = os.environ.get('WEATHERLINK_STATION_ID', '')

if not api_key or not api_secret or not station_id:
    print("❌ Variables manquantes : WEATHERLINK_API_KEY, WEATHERLINK_API_SECRET, WEATHERLINK_STATION_ID")
    sys.exit(1)

# Calcul de la signature HMAC-SHA256 (obligatoire pour l'API Weatherlink v2)
t = int(time.time())
message = f"api-key{api_key}t{t}"
signature = hmac.new(
    api_secret.encode('utf-8'),
    message.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# Appel à l'API Weatherlink v2
url = f"https://api.weatherlink.com/v2/current/{station_id}"
params = {
    'api-key': api_key,
    't': str(t),
    'api-signature': signature
}

try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    # Ajout d'un timestamp lisible pour affichage
    data['_fetched_at'] = time.strftime('%d/%m/%Y à %H:%M', time.localtime(t))
    data['_fetched_ts'] = t

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Données météo enregistrées ({data['_fetched_at']})")

except requests.exceptions.RequestException as e:
    print(f"❌ Erreur lors de l'appel API : {e}")
    sys.exit(1)
