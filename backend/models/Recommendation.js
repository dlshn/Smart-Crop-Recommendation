const mongoose = require("mongoose");

const recommendationSchema = new mongoose.Schema({
  district: { type: String, required: true, index: true },
  zone: { type: String, required: true },
  month: { type: Number, required: true, index: true },
  crop: { type: String, required: true, index: true },
  predictedRainfallMm: Number,
  rainfallBand: String,
  predictedPriceLkr: Number,
  zoneMatch: String,
  suitabilityScore: Number,
  profitabilityScore: Number,
  riskScore: Number,
  finalScore: Number,
});

// Compound index for the main query pattern (district + month + crop lookup)
recommendationSchema.index({ district: 1, month: 1, crop: 1 });

module.exports = mongoose.model("Recommendation", recommendationSchema);
