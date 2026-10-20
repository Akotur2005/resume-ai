import express from "express";
import cors from "cors";
import "dotenv/config";
import resumes from "./routes/resumes.js";
import reviews from "./routes/reviews.js";

const app = express();
const allowedOrigins = [process.env.CLIENT_ORIGIN, "http://localhost:5173", "http://localhost:5174"].filter(Boolean);
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin) || /^http:\/\/localhost:\d+$/.test(origin)) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
  }
}));
app.use(express.json({ limit: "2mb" }));

app.get("/api/health", (_req, res) => res.json({ ok: true }));
app.use("/api/resumes", resumes);
app.use("/api/reviews", reviews);

// Central error handler
app.use((err, _req, res, _next) => {
  console.error(err);
  res.status(500).json({ error: err.message || "Server error" });
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`API running on http://localhost:${port}`));
