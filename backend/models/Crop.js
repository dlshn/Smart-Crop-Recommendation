const mongoose = require("mongoose");

const cropSchema = new mongoose.Schema({
  crop: { type: String, required: true, unique: true, index: true },
  soilTypes: { type: [String], default: [] },
  districts: { type: [String], default: [], index: true },
  harvestType: { type: String, enum: ["short", "long"], required: true },
  // Only meaningful for "short" (annual/seasonal) crops, where it drives
  // the harvest-date math for price/rainfall prediction. "long" (perennial
  // tree/vine) crops are listed by district/soil suitability only -- no
  // date math uses this field for them -- so it is null for those, rather
  // than holding a number that looks precise but isn't actually used.
  harvestDays: { type: Number, default: null },
  category: { type: String, enum: ["fruit", "vegetable"], required: true },
  notes: { type: String, default: "" },
});

module.exports = mongoose.model("Crop", cropSchema);
