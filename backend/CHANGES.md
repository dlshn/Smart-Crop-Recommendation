# Changes in this backend folder (latest update)

## 1. Fixed: vegetables had no real historical mean price (`service/model_service.py`)
`dataset.csv` actually contains BOTH fruit and vegetable commodity/price
columns (`fruit_Commodity`/`fruit_Price...` AND
`vegitable_Commodity`/`vegitable_Price...`), but the code only ever read
the fruit columns. So for every vegetable crop, `get_crop_price_mean()`
returned `None`, `profitAboveMean` was always `False`, and the
mean-price filter silently never worked for 20 of your 37 crops.

Fixed by reshaping `dataset.csv` into one unified `crop`/`price` column
covering both fruits and vegetables (same technique used for
`recommendations.json` earlier). Verified with real data -- e.g. in
Nuwara Eliya for September: Carrot's own historical mean is 318.17,
Cabbage's is 274.52, Red Spinach's is 325.33 -- genuinely different,
individually-computed values per crop, not one shared number.

## 2. Simplified final short-term crop output (`routes/api.js`)
Per your spec, the `/api/recommend` response's `recommendations` array
now contains ONLY:
- `crop` (Name)
- `predictedPriceLkr` (Predicted price)
- `suitableSoilTypes` (Suitable soil type)
- `rainfallIdea` (a readable sentence, e.g. "Medium rainfall expected
  (~557mm total over the growing period)")

Removed from the short-term output: zone, zoneMatch, riskScore,
finalScore, suitabilityScore, harvestDate, harvestType,
historicalMeanPrice, rainfallBand as separate fields (rainfallBand is
now folded into the `rainfallIdea` sentence). The `Recommendation`
MongoDB collection (zone/risk scoring) is no longer queried by this
endpoint at all, since district suitability is already handled by
`Crop.districts` and the scoring fields are no longer part of the
output. `models/Recommendation.js` and the seeded data are left in
place in case you want them for something else later.

## 3. Filtering logic clarified (`routes/api.js`)
The pipeline is now explicitly:
1. Filter by district suitability (`Crop.districts` contains district)
2. Predict price + rainfall for every surviving SHORT crop
3. Keep only crops where `predictedPrice > thatCrop'sOwnHistoricalMean`
4. Return top 3 by predicted price, with the 4 simplified fields
5. LONG crops skip 2-4 entirely (district suitability only)

A `usingFallback: true/false` flag is now included in the response so
the frontend can tell if literally zero candidate crops cleared their
own mean price (rare, but the app still returns *something* ranked by
price in that edge case rather than an empty page).

## Frontend
`frontend/src/components/ResultCard.jsx` updated to match -- now shows
only Predicted Price / Suitable Soil Type / Rainfall Idea per card.

## From the previous update (still included)
- `models/Crop.js`, `models/Recommendation.js` -- were missing entirely
- `data/crops.json` -- real district suitability (agro-climatic zones)
  + differentiated soil types + DOA-sourced/general harvest timing
  (see `data/rebuild_crops.py` and `data/rebuild_harvest_timing.py`)

## Not included (recreate locally)
`node_modules/`, `.env` (your real MONGO_URI), `service/models/*.joblib`
(run `python -m service.pretrain` -- **you must re-run this** since
`model_service.py`'s data loading changed, old cached vegetable
fallback models are now stale).

## Next steps
```
cd backend
npm install
cp .env.example .env      # fill in your real MONGO_URI
npm run seed
pip install -r requirements.txt
python -m service.pretrain     # IMPORTANT: re-run even if you did before
python -m uvicorn service.app:app --reload --port 8000
# separate terminal:
npm start
```
