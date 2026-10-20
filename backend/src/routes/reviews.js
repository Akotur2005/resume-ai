import { Router } from "express";
import multer from "multer";
import { query } from "../db.js";
import { reviewResume } from "../langchain/reviewChain.js";
import { parseChain } from "../langchain/builderChain.js";
import { extractTextFromPdf, resumeToText } from "../utils/pdf.js";

const router = Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024 } });

// Review an UPLOADED PDF resume (+ optional job description)
router.post("/upload", upload.single("resume"), async (req, res, next) => {
  try {
    if (!req.file) return res.status(400).json({ error: "Attach a PDF as 'resume'" });
    if (req.file.mimetype !== "application/pdf")
      return res.status(400).json({ error: "Only PDF files are supported" });

    const text = await extractTextFromPdf(req.file.buffer);
    if (text.length < 100)
      return res.status(422).json({
        error: "Could not read text from this PDF. It may be a scanned image, which ATS systems also cannot read.",
      });

    const jobDescription = req.body.jobDescription || "";
    const result = await reviewResume(text, jobDescription);

    const { rows } = await query(
      `INSERT INTO reviews (source, file_name, resume_text, job_description, ats_score, result)
       VALUES ('upload', $1, $2, $3, $4, $5) RETURNING id, created_at`,
      [req.file.originalname, text, jobDescription, result.atsScore, result]
    );
    res.json({ id: rows[0].id, createdAt: rows[0].created_at, ...result });
  } catch (e) { next(e); }
});

// Review a resume built in the builder (saved in Postgres or sent inline)
router.post("/builder", async (req, res, next) => {
  try {
    const { resumeId, data, jobDescription = "" } = req.body;
    let resume = data;
    if (resumeId && !resume) {
      const { rows } = await query("SELECT data FROM resumes WHERE id = $1", [resumeId]);
      if (!rows[0]) return res.status(404).json({ error: "Resume not found" });
      resume = rows[0].data;
    }
    if (!resume) return res.status(400).json({ error: "Provide resumeId or data" });

    const text = resumeToText(resume);
    const result = await reviewResume(text, jobDescription);

    const { rows } = await query(
      `INSERT INTO reviews (resume_id, source, resume_text, job_description, ats_score, result)
       VALUES ($1, 'builder', $2, $3, $4, $5) RETURNING id, created_at`,
      [resumeId || null, text, jobDescription, result.atsScore, result]
    );
    res.json({ id: rows[0].id, createdAt: rows[0].created_at, ...result });
  } catch (e) { next(e); }
});

// Import an uploaded PDF INTO the builder (PDF -> structured JSON via LangChain)
router.post("/import", upload.single("resume"), async (req, res, next) => {
  try {
    if (!req.file) return res.status(400).json({ error: "Attach a PDF as 'resume'" });
    const text = await extractTextFromPdf(req.file.buffer);
    const data = await parseChain.invoke({ text });
    res.json(data);
  } catch (e) { next(e); }
});

// History
router.get("/", async (_req, res, next) => {
  try {
    const { rows } = await query(
      "SELECT id, resume_id, source, file_name, ats_score, created_at FROM reviews ORDER BY created_at DESC LIMIT 50"
    );
    res.json(rows);
  } catch (e) { next(e); }
});

router.get("/:id", async (req, res, next) => {
  try {
    const { rows } = await query("SELECT * FROM reviews WHERE id = $1", [req.params.id]);
    if (!rows[0]) return res.status(404).json({ error: "Not found" });
    res.json({ id: rows[0].id, createdAt: rows[0].created_at, ...rows[0].result });
  } catch (e) { next(e); }
});

export default router;
