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
