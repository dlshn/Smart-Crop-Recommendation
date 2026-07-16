const mongoose = require("mongoose");

const predictionSchema = new mongoose.Schema({
  district: { type: String, required: true, index: true },
  crop: { type: String, required: true },
  month: { type: Number, required: true },
  plantingDate: { type: Date, required: true },
  harvestDate: { type: Date, required: true },
  harvestDays: { type: Number, required: true },
  predictedPriceLkr: { type: Number, required: true },
  predictedRainfallMm: { type: Number, required: true },
  rainfallRange: { type: String, default: "" },
  suitableSoilTypes: { type: [String], default: [] },
  profitAboveMean: { type: Boolean, default: false },
  harvestType: { type: String, enum: ["short", "long"], required: true },
  createdAt: { type: Date, default: Date.now },
});

predictionSchema.index({ district: 1, month: 1, crop: 1 });

module.exports = mongoose.model("Prediction", predictionSchema);
