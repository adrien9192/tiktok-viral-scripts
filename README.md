# TikTok Viral Script Generator

Génère des scripts de vidéos virales TikTok avec l'IA, basé sur les codes et tendances de janvier 2026.

## Features

- **Analyse des tendances** - Intègre les formats viraux actuels (26 Goals, Micro-Series, etc.)
- **Hooks optimisés** - 7 styles de hooks avec scores d'efficacité
- **Structure complète** - Hook → Setup → Content → Payoff → CTA
- **Niches spécialisées** - Finance, Fitness, Lifestyle, Business, Comedy, Education
- **Hashtags intelligents** - Suggère des hashtags ciblés (pas de #fyp inutile)
- **Conseils algorithme** - Tips basés sur les priorités algo TikTok 2026

## Quick Start

```bash
# Clone et lancer
cd tiktok_viral_scripts
./start.sh

# Ouvrir http://localhost:8080
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Interface web |
| `/api/generate` | POST | Générer un script |
| `/api/trends` | GET | Tendances actuelles |
| `/api/hooks` | GET | Styles de hooks disponibles |
| `/api/niches` | GET | Niches et configurations |
| `/api/health` | GET | Health check |

## Exemple de requête

```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Comment j ai gagné 5000€ en side hustle",
    "niche": "business",
    "hook_style": "confession",
    "length": "medium",
    "include_cta": true
  }'
```

## Codes Viraux TikTok 2026

### Algorithme - Ce qui compte

1. **Completion Rate > 80%** - Priorité absolue
2. **Long-form (60s+)** - Shift vers contenu plus long
3. **Original Audio** - Sons originaux > trending
4. **Micro-séries** - Format "Episode X of Y"
5. **Engagement Velocity** - Réponses rapides

### Hooks par efficacité

| Style | Efficacité |
|-------|------------|
| Controversy | 95% |
| Curiosity Gap | 92% |
| Confession | 90% |
| Transformation | 89% |
| Fear of Missing | 88% |
| Education | 87% |
| Story Loop | 85% |

## Déploiement

### Railway
```bash
railway up
```

### Render
Le fichier `render.yaml` est prêt pour déploiement automatique.

### Docker
```bash
docker build -t tiktok-scripts .
docker run -p 8080:8080 tiktok-scripts
```

## Structure

```
tiktok_viral_scripts/
├── src/
│   ├── api/          # FastAPI application
│   ├── services/     # Business logic
│   ├── templates/    # HTML templates
│   └── static/       # CSS/JS
├── config/           # Viral codes YAML
├── tests/            # Tests
└── MISSION_CONTROL.md
```

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Vanilla JS + CSS (TikTok-inspired dark theme)
- **AI**: Claude CLI integration
- **Deploy**: Docker, Railway, Render ready

---

*Créé par Adrien Lainé - Powered by Claude AI*
