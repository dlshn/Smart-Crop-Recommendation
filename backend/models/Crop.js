const mongoose = require("mongoose");

const cropSchema = new mongoose.Schema({
  crop: { type: String, required: true, unique: true },
  soilTypes: { type: [String], default: [] },
  districts: { type: [String], default: [] },
  harvestType: { type: String, enum: ["short", "long"], required: true },
  harvestDays: { type: Number, required: true },
  category: { type: String, enum: ["fruit", "vegetable", "other"], default: "other" },
  notes: String,
});

module.exports = mongoose.model("Crop", cropSchema);
