/**
 * Seed script: loads data/recommendations.json (precomputed by the Python
 * ML pipeline) into MongoDB.
 *
 * Usage:
 *   node scripts/seed.js
 */
require("dotenv").config();
const mongoose = require("mongoose");
const fs = require("fs");
const path = require("path");
const Recommendation = require("../models/Recommendation");

const MONGO_URI = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/smart_crop_db";

async function seed() {
  console.log("Connecting to MongoDB:", MONGO_URI);
  await mongoose.connect(MONGO_URI);

  const dataPath = path.join(__dirname, "..", "data", "recommendations.json");
  const records = JSON.parse(fs.readFileSync(dataPath, "utf-8"));
  console.log(`Loaded ${records.length} records from JSON`);

  console.log("Clearing existing collection...");
  await Recommendation.deleteMany({});

  console.log("Inserting records (this may take a few seconds)...");
  await Recommendation.insertMany(records, { ordered: false });

  const count = await Recommendation.countDocuments();
  console.log(`Done. Collection now has ${count} documents.`);

  await mongoose.disconnect();
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
