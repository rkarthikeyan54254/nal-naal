# நல்நாள் · NalNaal

A Tamil daily-calendar Progressive Web App (PWA) rooted in the **Pambu Panchangam (Vakyam tradition)**, built for a Tamil Hindu family. Every day shows its presiding deity, nakshatram, tithi, occasions and festivals — with a nearby-temple finder for observance days.

## Features

- **Full-year panchangam** (Aadi 2026 → Aadi 2027), Drik-computed with Swiss Ephemeris (Lahiri ayanamsa)
- **Pambu Panchangam override layer** — the physical book always wins over computation
- **A real deity image every day** — all 27 nakshatrams mapped to their presiding deity (Anusham → Kanchi Maha Periyava, per family tradition)
- **21 major fixed festivals** — Deepavali, Pongal, Karthigai Deepam, Thaipusam, Krishna Jayanthi, and more
- **Dual-occasion handling** — when a festival and a meaningful star coincide, both are honoured (festival on the card, star deity as a chip)
- **Temple finder** — one tap opens Google Maps to the nearest relevant temple (privacy-first, no API key, no location stored)
- **Installable PWA** — works offline, installs to the home screen

## Tech

- Vanilla HTML / CSS / JS PWA (no build step)
- `generate_panchangam.py` — the panchangam engine (requires `pyswisseph`)
- Service worker for offline caching

## Running locally

```bash
cd tamil-nal-app
python3 -m http.server 8765
# open http://localhost:8765
```

## Regenerating panchangam data

```bash
pip install pyswisseph
python3 generate_panchangam.py   # writes data.json
```

To correct any date against the physical Pambu Panchangam, edit the `OVERRIDES` dict in `generate_panchangam.py` (or `overrides.json`) and re-run. Overrides always take precedence.

## Structure

- `index.html`, `styles.css`, `app.js` — the app
- `generate_panchangam.py` — panchangam + festival engine
- `data.json` — generated full-year data
- `images/` — deity & festival images
- `icons/` — app icons
- `manifest.json`, `sw.js` — PWA manifest & service worker

---

*Built with care for family devotion. நல்நாள் வாழ்த்துக்கள்.*
