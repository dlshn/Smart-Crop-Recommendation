const mongoose = require("mongoose");

const cropSchema = new mongoose.Schema({
  crop: { type: String, required: true, unique: true, index: true },
  soilTypes: { type: [String], default: [] },
  districts: { type: [String], default: [], index: true },
  harvestType: { type: String, enum: ["short", "long"], required: true },
  harvestDays: { type: Number, required: true },
  category: { type: String, enum: ["fruit", "vegetable"], required: true },
  notes: { type: String, default: "" },
});

module.exports = mongoose.model("Crop", cropSchema);
