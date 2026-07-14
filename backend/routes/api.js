const express = require("express");
const router = express.Router();
const fs = require("fs");
const path = require("path");
const Recommendation = require("../models/Recommendation");

const meta = JSON.parse(
  fs.readFileSync(path.join(__dirname, "..", "data", "meta.json"), "utf-8")
);

// GET /api/districts -> list of all districts
router.get("/districts", (req, res) => {
  res.json(meta.districts);
});

// GET /api/crops -> list of all crops
router.get("/crops", (req, res) => {
  res.json(meta.crops);
});

// POST /api/recommend
// body: { district: "Kandy", month: 6, crops: ["Banana","Mango",...] }
// If "crops" is omitted or empty, all crops are considered.
router.post("/recommend", async (req, res) => {
  try {
    const { district, month, crops, topN } = req.body;

    if (!district || !month) {
      return res.status(400).json({ error: "district and month are required" });
    }
    if (!meta.districts.includes(district)) {
      return res.status(400).json({ error: `Unknown district: ${district}` });
    }

    const query = { district, month: Number(month) };
    if (Array.isArray(crops) && crops.length > 0) {
      query.crop = { $in: crops };
    }

    const results = await Recommendation.find(query)
      .sort({ finalScore: -1 })
      .limit(topN ? Number(topN) : 3)
      .select("-_id -__v");

    res.json({ district, month: Number(month), results });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;
