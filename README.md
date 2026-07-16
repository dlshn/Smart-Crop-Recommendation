# Smart Crop Recommendation

A web app that recommends profitable, suitable crops for Sri Lankan farmers based on
district, planting month, and soil/zone suitability — combining a rule-based
suitability dataset with live ML price and rainfall predictions.

## Tech Stack

**Frontend**
- React 18 + Vite
- Tailwind CSS (utility-first styling, light agricultural theme)

**Backend API**
- Node.js + Express
- MongoDB + Mongoose (crop metadata and precomputed district/month/crop suitability scores)
- Calls the Python ML service over HTTP for live price/rainfall predictions

**ML Service**
- Python + FastAPI (served with `uvicorn`)
- scikit-learn `RandomForestRegressor` — one model per crop, trained on historical
  fruit price/weather data, cached to disk with `joblib`
- pandas for data loading/feature engineering

**Data**
- `data/dataset.csv` — historical fruit price + weather records (source dataset;
  vegetables aren't covered, so they fall back to a shared all-crops model). **Not
  committed to git** (gitignored, ~9MB/130k rows) — must be present on disk before
  starting the ML service, or `load_data()` will fail with `FileNotFoundError`. Get
  it from whoever holds the current copy if you don't have one.
- `backend/data/recommendations.json` — precomputed suitability/zone/risk scores per
  District × Month × Crop, seeded into MongoDB
- `backend/data/crops.json` — crop metadata (soil types, districts, harvest type/days)

## Architecture

```
React (Vite, :5173)
   │  /api/* proxied to backend
   ▼
Express + MongoDB (:5000)
   │  crop metadata + seeded suitability scores
   │  calls model service per candidate crop
   ▼
FastAPI + scikit-learn (:8000)
   │  predicts price (LKR) and rainfall (mm) per crop/district/month
   ▼
Cached RandomForest models (backend/models/*.joblib)
```

The Express layer merges the live ML prediction (price, rainfall, profitability)
with the precomputed suitability/zone/risk data from MongoDB before returning
ranked recommendations to the frontend.

## Repo Structure
- `backend/` — Express API, Mongoose models, seed script, and the Python ML service
  (`backend/service/`)
- `frontend/` — Vite + React UI
- `data/` — source dataset used to train the ML models

## Quick Start (local)

Requirements: Node.js 18+, Python 3.10+, MongoDB (local or Atlas).

Each of the three services below runs in its own terminal window and needs to stay
running. Commands are shown for Windows PowerShell; on macOS/Linux swap
`.venv\Scripts\Activate.ps1` for `source .venv/bin/activate` and `copy` for `cp`.

**1. ML service** (terminal 1)
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m service.pretrain
# one-time: trains and caches a RandomForest model per crop to backend/models/*.joblib
python -m uvicorn service.app:app --reload --host 127.0.0.1 --port 8000
```

**2. Backend API** (terminal 2 — no venv needed here)
```powershell
cd backend
npm install
copy .env.example .env
# then edit .env and set MONGO_URI
npm run seed
# loads crop metadata + suitability scores into MongoDB
npm start
# http://localhost:5000
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173, proxies /api to :5000
```

## API Reference

| Method | Endpoint         | Body                                              | Returns                                    |
|--------|------------------|----------------------------------------------------|---------------------------------------------|
| GET    | `/api/districts` | -                                                    | list of district names                       |
| GET    | `/api/crops`     | -                                                    | list of crop names                            |
| POST   | `/api/recommend` | `{ district, month, crops?: string[], lang?: "en"\|"si" }` | ranked crop recommendations + long-term crops + mean price |

See `backend/routes/api.js` and `backend/service/app.py` for implementation details.

## Notes
- The Python service trains and caches a `RandomForestRegressor` per crop on first
  run (`python -m service.pretrain`); live requests only do inference against the
  cached models, so make sure to run it once before starting the ML service normally.
- Crops not present in `dataset.csv` (vegetables) fall back to a single shared
  all-crops model — treat those price predictions as rough estimates only.
