require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const apiRoutes = require("./routes/api");

const app = express();
const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/smart_crop_db";

app.use(cors());
app.use(express.json());

app.use("/api", apiRoutes);

app.get("/", (req, res) => {
  res.json({ status: "Smart Crop Recommendation API is running" });
});

mongoose.connection.on("disconnected", () => {
  console.warn("MongoDB connection lost, mongoose will attempt to reconnect...");
});
mongoose.connection.on("reconnected", () => {
  console.log("MongoDB reconnected");
});
mongoose.connection.on("error", (err) => {
  console.error("MongoDB connection error:", err.message);
});

mongoose
  .connect(MONGO_URI, {
    // Atlas SRV lookups can resolve IPv6 hosts that some Windows networks
    // can't complete a TLS handshake with, causing intermittent
    // "socket disconnected before secure TLS connection was established"
    // errors. Forcing IPv4 avoids that path.
    family: 4,
    serverSelectionTimeoutMS: 15000,
  })
  .then(() => {
    console.log("Connected to MongoDB");
    app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
  })
  .catch((err) => {
    console.error("MongoDB connection failed:", err.message);
    console.error(
      "Check your MONGO_URI in .env (Atlas connection string, username/password, " +
      "and that your IP is whitelisted in Atlas Network Access). " +
      "Also make sure you ran 'npm run seed' at least once."
    );
    process.exit(1);
  });