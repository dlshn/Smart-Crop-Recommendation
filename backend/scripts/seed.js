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
const Crop = require("../models/Crop");

const MONGO_URI = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/smart_crop_db";

async function seed() {
  console.log("Connecting to MongoDB:", MONGO_URI);
  await mongoose.connect(MONGO_URI);

  const recPath = path.join(__dirname, "..", "data", "recommendations.json");
  const records = JSON.parse(fs.readFileSync(recPath, "utf-8"));
  console.log(`Loaded ${records.length} recommendation records from JSON`);

  const cropPath = path.join(__dirname, "..", "data", "crops.json");
  const cropRecords = JSON.parse(fs.readFileSync(cropPath, "utf-8"));
  console.log(`Loaded ${cropRecords.length} crop metadata records from JSON`);

  console.log("Clearing existing collections...");
  await Recommendation.deleteMany({});
  await Crop.deleteMany({});

  console.log("Inserting recommendations...");
  await Recommendation.insertMany(records, { ordered: false });
  console.log("Inserting crop metadata...");
  await Crop.insertMany(cropRecords, { ordered: false });

  const recCount = await Recommendation.countDocuments();
  const cropCount = await Crop.countDocuments();
  console.log(`Done. Recommendation documents: ${recCount}, Crop metadata documents: ${cropCount}`);

  await mongoose.disconnect();
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
