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

    const cropsFilter = Array.isArray(crops) && crops.length > 0 ? crops : null;
    const allCrops = await Crop.find({
      ...(cropsFilter ? { crop: { $in: cropsFilter } } : {}),
      districts: district,
    }).lean();

    const shortCrops = allCrops.filter((item) => item.harvestType === "short");
    const longCrops = allCrops.filter((item) => item.harvestType === "long");

    const candidateResults = [];
    for (const crop of shortCrops) {
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
      candidateResults.push({ crop: crop.crop, metadata: crop, prediction });
    }

    const recommended = candidateResults
      .filter((item) => item.prediction.profitAboveMean)
      .sort((a, b) => b.prediction.predictedPriceLkr - a.prediction.predictedPriceLkr)
      .map((item) => ({
        ...item.prediction,
        crop: item.crop,
        suitableSoilTypes: item.metadata.soilTypes,
        harvestDays: item.metadata.harvestDays,
      }))
      .slice(0, 3);

    const fallbackRecommended = candidateResults
      .sort((a, b) => b.prediction.predictedPriceLkr - a.prediction.predictedPriceLkr)
      .map((item) => ({
        ...item.prediction,
        crop: item.crop,
        suitableSoilTypes: item.metadata.soilTypes,
        harvestDays: item.metadata.harvestDays,
      }))
      .slice(0, 3);

    const recommendedCrops = recommended.length > 0 ? recommended : fallbackRecommended;
    const meanPrice =
      recommendedCrops.reduce((sum, item) => sum + item.prediction.predictedPriceLkr, 0) /
      Math.max(recommendedCrops.length, 1);

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
      longTermCrops,
      meanPrice: Number(meanPrice.toFixed(2)),
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || "Internal server error" });
  }
});

module.exports = router;
