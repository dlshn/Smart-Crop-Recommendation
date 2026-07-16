const express = require("express");
const router = express.Router();
const fs = require("fs");
const path = require("path");
const Crop = require("../models/Crop");

const meta = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "data", "meta.json"), "utf-8")
);

const MODEL_SERVICE_URL = process.env.MODEL_SERVICE_URL || "http://127.0.0.1:8000/predict";

async function callPriceService(payload) {
  const response = await fetch(MODEL_SERVICE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Model service error: ${response.status} ${errorBody}`);
  }
  return response.json();
}

// Turns a rainfall band + mm figure into a short human-readable sentence
// for the "Rainfall idea within growing period" output field.
function describeRainfall(rainfallRangeLabel, predictedRainfallMm) {
  const label = rainfallRangeLabel || "Unknown";
  return `${label} rainfall expected (~${Math.round(predictedRainfallMm)}mm total over the growing period)`;
}

// GET /api/districts -> list of all districts
router.get("/districts", (req, res) => {
  res.json(meta.districts);
});

// GET /api/crops -> list of all crops
router.get("/crops", (req, res) => {
  res.json(meta.crops);
});

// POST /api/recommend
// body: { district: "Kandy", month: 6, crops: ["Banana","Mango",...], lang: "en" }
//
// Pipeline:
//   1. Filter candidate crops by district suitability (Crop.districts)
//   2. For each surviving SHORT crop, predict price at harvest + rainfall
//      over the growing period (calls the Python ML service)
//   3. Keep only crops whose predicted price is above THAT crop's own
//      individually-computed historical mean price (not a shared value)
//   4. Return the top 3 by predicted price, each with only:
//      Name, Predicted price, Suitable soil type, Rainfall idea
//   5. LONG crops skip steps 2-4 entirely and are just listed by
//      district suitability (see longTermCrops below)
router.post("/recommend", async (req, res) => {
  try {
    const { district, month, crops, lang = "en" } = req.body;
    const plantingYear = new Date().getFullYear();

    if (!district || !month) {
      return res.status(400).json({ error: "district and month are required" });
    }
    if (!meta.districts.includes(district)) {
      return res.status(400).json({ error: `Unknown district: ${district}` });
    }

    const plantingDate = new Date(plantingYear, Number(month) - 1, 1);
    if (Number.isNaN(plantingDate.getTime())) {
      return res.status(400).json({ error: "Invalid planting month" });
    }

    // ---- Step 1: district-suitability filter ----
    const cropsFilter = Array.isArray(crops) && crops.length > 0 ? crops : null;
    const allCrops = await Crop.find({
      ...(cropsFilter ? { crop: { $in: cropsFilter } } : {}),
      districts: district,
    }).lean();

    const shortCrops = allCrops.filter((item) => item.harvestType === "short");
    const longCrops = allCrops.filter((item) => item.harvestType === "long");

    // ---- Step 2: predict price (at harvest) + rainfall for every
    //      district-suitable short crop ----
    const candidateResults = await Promise.all(
      shortCrops.map(async (crop) => {
        const payload = {
          district,
          crop: crop.crop,
          plantingDate: plantingDate.toISOString().slice(0, 10),
          language: lang,
          harvestDays: crop.harvestDays,
          harvestType: crop.harvestType,
          soilTypes: crop.soilTypes,
        };
        const prediction = await callPriceService(payload);
        return { crop: crop.crop, metadata: crop, prediction };
      })
    );

    // ---- Step 3: keep only crops priced above THEIR OWN historical
    //      mean (prediction.historicalMeanPrice / profitAboveMean are
    //      computed per-crop by the ML service's get_crop_price_mean) ----
    const profitable = candidateResults.filter((item) => item.prediction.profitAboveMean === true);

    // Fallback only if literally none clear their own mean (e.g. very
    // sparse data for every candidate) -- still ranked by price, but
    // flagged so the frontend can tell the user this is a fallback.
    const usingFallback = profitable.length === 0;
    const pool = usingFallback ? candidateResults : profitable;

    // ---- Step 4: rank by predicted price, take top 3, output ONLY the
    //      4 required fields ----
    const recommendedCrops = pool
      .sort((a, b) => b.prediction.predictedPriceLkr - a.prediction.predictedPriceLkr)
      .slice(0, 3)
      .map((item) => ({
        crop: item.crop,
        predictedPriceLkr: item.prediction.predictedPriceLkr,
        suitableSoilTypes: item.metadata.soilTypes,
        rainfallIdea: describeRainfall(item.prediction.rainfallRange, item.prediction.predictedRainfallMm),
      }));

    const meanPrice =
      recommendedCrops.reduce((sum, item) => sum + item.predictedPriceLkr, 0) /
      Math.max(recommendedCrops.length, 1);

    // ---- Step 5: long-term crops -- district suitability only, no
    //      price/rainfall prediction ----
    const longTermCrops = longCrops.map((crop) => ({
      crop: crop.crop,
      suitableSoilTypes: crop.soilTypes,
      harvestType: crop.harvestType,
      harvestDays: crop.harvestDays,
      notes: crop.notes,
    }));

    res.json({
      district,
      month: Number(month),
      plantingDate: plantingDate.toISOString().slice(0, 10),
      recommendations: recommendedCrops,
      usingFallback,
      longTermCrops,
      meanPrice: Number(meanPrice.toFixed(2)),
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || "Internal server error" });
  }
});

module.exports = router;
