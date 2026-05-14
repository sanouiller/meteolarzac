# 🌤️ Station Météo — Collège

Affichage en temps réel des données de la station météo Weatherlink,  
hébergé sur GitHub Pages et actualisé automatiquement toutes les 15 minutes.

---

## Structure du dépôt

```
/
├── index.html                      ← Page d'affichage (GitHub Pages)
├── fetch_weather.py                ← Script de récupération Weatherlink
├── data.json                       ← Données météo (généré automatiquement)
└── .github/
    └── workflows/
        └── meteo.yml               ← Planificateur automatique
```

---

## Installation

### 1. Créer le dépôt GitHub
- Nouveau dépôt public nommé `meteo-college`
- Uploader tous les fichiers tels quels (respecter l'arborescence)

### 2. Ajouter les secrets Weatherlink
**Settings → Secrets and variables → Actions → New repository secret**

| Nom | Valeur |
|---|---|
| `WEATHERLINK_API_KEY` | Votre clé API v2 |
| `WEATHERLINK_API_SECRET` | Votre secret API v2 |
| `WEATHERLINK_STATION_ID` | L'ID de votre station |

> Clés disponibles sur weatherlink.com → compte → API Keys → Générer la clé v2

### 3. Activer GitHub Pages
**Settings → Pages → Source : Deploy from a branch → main → / (root) → Save**

### 4. Premier lancement manuel
**Actions → "Mise à jour météo" → Run workflow**  
→ La page se remplit immédiatement avec les vraies données.

### 5. URL à intégrer dans Kosmos
```
https://VOTRE-PSEUDO.github.io/meteo-college/
```

---

## Planning automatique
Le workflow tourne toutes les **15 minutes** via GitHub Actions (gratuit).  
La page se rafraîchit elle-même côté navigateur toutes les 15 minutes.

---

## Raspberry Pi — Affichage en kiosque
Voir les scripts `setup.sh` (dépôt séparé) pour la configuration  
du mode kiosque et du planning d'allumage TV (lun–ven, hors vacances Zone C).
