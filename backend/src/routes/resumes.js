import { Router } from "express";
import { query } from "../db.js";
import { bulletChain, summaryChain, generateFromJdChain } from "../langchain/builderChain.js";

const router = Router();

// List saved resumes
router.get("/", async (_req, res, next) => {
  try {
    const { rows } = await query(
      "SELECT id, title, updated_at FROM resumes ORDER BY updated_at DESC"
    );
    res.json(rows);
  } catch (e) { next(e); }
});

// Get one
router.get("/:id", async (req, res, next) => {
  try {
    const { rows } = await query("SELECT * FROM resumes WHERE id = $1", [req.params.id]);
    if (!rows[0]) return res.status(404).json({ error: "Not found" });
    res.json(rows[0]);
  } catch (e) { next(e); }
});

// Create
router.post("/", async (req, res, next) => {
  try {
    const { title = "My Resume", data } = req.body;
    if (!data) return res.status(400).json({ error: "data is required" });
    const { rows } = await query(
      "INSERT INTO resumes (title, data) VALUES ($1, $2) RETURNING *",
      [title, data]
    );
    res.status(201).json(rows[0]);
  } catch (e) { next(e); }
});

// Update
router.put("/:id", async (req, res, next) => {
  try {
    const { title, data } = req.body;
    const { rows } = await query(
      `UPDATE resumes SET title = COALESCE($1, title), data = COALESCE($2, data), updated_at = NOW()
       WHERE id = $3 RETURNING *`,
      [title, data, req.params.id]
    );
    if (!rows[0]) return res.status(404).json({ error: "Not found" });
    res.json(rows[0]);
  } catch (e) { next(e); }
});

// Delete
router.delete("/:id", async (req, res, next) => {
  try {
    await query("DELETE FROM resumes WHERE id = $1", [req.params.id]);
    res.status(204).end();
  } catch (e) { next(e); }
});

// ---- AI helpers used by the builder form ----
router.post("/ai/bullet", async (req, res, next) => {
  try {
    const { role = "", targetRole = "", bullet } = req.body;
    if (!bullet) return res.status(400).json({ error: "bullet is required" });
    const improved = await bulletChain.invoke({ role, targetRole, bullet });
    res.json({ improved: improved.trim() });
  } catch (e) { next(e); }
});

router.post("/ai/summary", async (req, res, next) => {
  try {
    const { targetRole = "", skills = [], experience = [] } = req.body;
    const exp = experience
      .map((e) => `${e.title} at ${e.company} (${e.start}-${e.end}): ${(e.bullets || []).join("; ")}`)
      .join("\n");
    const summary = await summaryChain.invoke({ targetRole, skills: skills.join(", "), experience: exp });
    res.json({ summary: summary.trim() });
  } catch (e) { next(e); }
});

router.post("/ai/from-jd", async (req, res, next) => {
  try {
    const { jobDescription, userNotes = "", fullName = "", targetTitle = "" } = req.body;
    if (!jobDescription || !jobDescription.trim()) {
      return res.status(400).json({ error: "Job description is required" });
    }
    const resumeData = await generateFromJdChain.invoke({
      jobDescription,
      userNotes,
      fullName: fullName || "Your Name",
      targetTitle,
    });
    res.json(resumeData);
  } catch (e) { next(e); }
});

export default router;
