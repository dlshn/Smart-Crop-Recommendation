# Smart Crop Recommendation

Smart Crop Recommendation is a lightweight, explainable system that recommends crops based on soil, weather, and farmer constraints.

## Overview
- Purpose: Help farmers choose appropriate crops for a plot by combining historical data, simple ML models, and human-readable explanations.
- Platform: Web app with a React frontend and Node.js backend (see `frontend/` and `backend/`).

## Key Features
- Input form for soil parameters, location, season, budget and preferences.
- Ranked crop recommendations with confidence and expected yield range.
- Explainability: per-recommendation feature contributions (SHAP/LIME style) and plain-language reasoning.
- Save scenarios, export results, and collect feedback for model improvement.

## Repo Structure
- `backend/` — Node.js API, model-serving stubs, and seed scripts.
- `frontend/` — Vite + React UI components for inputs and results.
- `data/` — sample datasets and `dataset.csv` used for prototyping.

## Quick start (local)
Requirements: Node.js (16+ recommended), npm.

1. Install backend dependencies and seed sample data

```bash
cd backend
npm install
npm run seed
npm start
```

2. Install and run frontend

```bash
cd frontend
npm install
npm run dev
```

Open the app at the port shown by Vite (default `http://localhost:5173`).

## API (core)
- `POST /recommend` — Accepts JSON input (soil features, location, season, preferences). Returns ranked crops, confidence scores, and explanation payload (feature contributions and textual reasons).
- `GET /metadata` — Supported crops, feature ranges, and model version.
- `POST /feedback` — Collects user feedback to improve future models.

See `backend/routes/api.js` for implementation details.

## Model & Explainability
- Prototype uses a tree-based model (LightGBM/XGBoost) for tabular performance.
- Explainability: use SHAP for local feature contributions and partial dependence / global importance for broader insights.
- Safety rules: apply rule-based checks (e.g., exclude crops when pH/range constraints fail) and show clear warnings.

## Data & Preprocessing
- Use `data/dataset.csv` (or external agronomy datasets) with fields for soil, weather, and historical yield.
- Steps: validate → impute missing values → feature engineering (rolling weather stats, categorical encodings) → train/test splits by region/season.

## Testing & Evaluation
- Offline metrics: MAE/RMSE for yield prediction or classification metrics for suitability tasks.
- Monitor model drift and data distribution changes in production.

## Deployment & Ops
- Containerize with Docker; optionally orchestrate with Kubernetes for scale.
- CI/CD: lint, unit tests, model validation, and staged rollout (canary).

## Security & Privacy
- Encrypt data in transit and at rest for any PII.
- Log only necessary request fields; anonymize logs used for model training.

## Roadmap / Next Steps
1. Train a baseline model on `data/dataset.csv` and wire it into `POST /recommend`.
2. Add SHAP-based explanation payload and visualizations in the frontend.
3. Run a small pilot with real users and collect feedback.

## Contributing
Open issues and PRs are welcome. Please add tests for new endpoints and model changes.

---
If you want, I can flesh this out into a longer developer README with runbooks, Dockerfiles, and API examples. Which should I do next?
# Smart Crop Recommendation System — MERN Stack

This is the MERN (MongoDB, Express, React, Node) version of the system.
The machine learning (Random Forest models) still runs in Python — that
part doesn't change — but instead of calling Python at runtime, all
possible predictions were **precomputed** into a JSON file
(`backend/data/recommendations.json`, 11,100 rows covering every
District × Month × Crop combination) and loaded into MongoDB. The
Express API then just queries and sorts that data. This means the
Node.js backend has zero Python dependency at runtime.

```
mern/
  backend/    Express + MongoDB API
  frontend/   React (Vite) web app
```

## Prerequisites
- Node.js 18+
- MongoDB running locally (or a MongoDB Atlas connection string)

## 1. Backend setup

```
cd backend
npm install
cp .env.example .env      # edit MONGO_URI if needed
npm run seed               # loads recommendations.json into MongoDB
npm start                  # starts the API on http://localhost:5000
```

Test it:
```
curl http://localhost:5000/api/districts
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"district":"Kandy","month":6,"crops":["Banana","Mango","Carrot"]}'
```

## 2. Frontend setup

In a second terminal:
```
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). The dev
server proxies `/api` requests to the backend on port 5000
(see `vite.config.js`), so both must be running at the same time.

## If you want to regenerate the precomputed data
If you retrain the Python models (see the `python/` pipeline in the
main project folder), re-run:
```
python src/04_export_for_mern.py
```
This regenerates `backend/data/recommendations.json` and `meta.json`,
then re-run `npm run seed` in the backend.

## API Reference
| Method | Endpoint          | Body                                               | Returns                          |
|--------|-------------------|-----------------------------------------------------|-----------------------------------|
| GET    | /api/districts    | -                                                   | list of 25 district names         |
| GET    | /api/crops        | -                                                   | list of 37 crop names             |
| POST   | /api/recommend    | `{ district, month, crops?: [], topN?: 3 }`         | top-N ranked crop recommendations |

## Note on testing
This code was written and syntax-validated (via `node --check` for the
backend and `tsc --noEmit` for the JSX frontend) in a sandbox without
internet access, so `npm install` could not be run there. It has not
been executed end-to-end against a live MongoDB instance. Please run
`npm install` and test locally — if anything breaks, the error message
will point to the exact line and I can fix it.
