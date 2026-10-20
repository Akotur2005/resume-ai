import { useState } from "react";
import { api } from "../api.js";
import ResumePreview from "./ResumePreview.jsx";
import ReviewResult from "./ReviewResult.jsx";

const SAMPLE_JD = `Role: Senior Full Stack Engineer (React + Node.js)
Company: CloudScale Technologies

Requirements:
- 3+ years experience building modern web applications with React, TypeScript, and Node.js / Express.
- Deep expertise in relational databases, PostgreSQL, and schema design.
- Hands-on experience developing RESTful APIs and microservices.
- Experience with cloud platforms (AWS/GCP), Docker, and CI/CD pipelines.
- Knowledge of LLMs, AI integrations, or LangChain is a strong plus.
- Proven track record of improving system latency, test coverage, and scalability.`;

export default function JdResumeGenerator({ onEditInBuilder }) {
  const [jobDescription, setJobDescription] = useState("");
  const [targetTitle, setTargetTitle] = useState("");
  const [fullName, setFullName] = useState("");
  const [userNotes, setUserNotes] = useState("");
  const [generatedResume, setGeneratedResume] = useState(null);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [savedId, setSavedId] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleQuickFill = () => {
    setJobDescription(SAMPLE_JD);
    setTargetTitle("Senior Full Stack Engineer");
    setFullName("Aryan Kotur");
    setUserNotes("Final year B.E. student with projects in React, Node.js, LangChain, PostgreSQL and AI integrations.");
  };

  const handleGenerate = async (e) => {
    e?.preventDefault();
    if (!jobDescription.trim()) {
      setError("Please paste a job description first.");
      return;
    }
    setError("");
    setLoading(true);
    setReview(null);
    setSaveSuccess(false);

    try {
      const data = await api.generateFromJd({
        jobDescription,
        targetTitle,
        fullName,
        userNotes,
      });
      setGeneratedResume(data);
      setSavedId(null);
    } catch (err) {
      setError(err.message || "Failed to generate tailored resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!generatedResume) return;
    try {
      setError("");
      const title = `${targetTitle || generatedResume.fullName || "ATS"} Resume`;
      const res = await api.createResume(title, generatedResume);
      setSavedId(res.id);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRunReview = async () => {
    if (!generatedResume) return;
    setReviewLoading(true);
    setError("");
    try {
      const res = await api.reviewBuilt(generatedResume, jobDescription, savedId);
      setReview(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setReviewLoading(false);
    }
  };

  const handleCustomize = () => {
    if (!generatedResume) return;
    if (onEditInBuilder) {
      onEditInBuilder({
        data: generatedResume,
        title: `${targetTitle || generatedResume.fullName || "Tailored"} Resume`,
        id: savedId,
        targetRole: targetTitle,
        jobDescription,
      });
    }
  };

  return (
    <div className="split">
      <section className="panel no-print">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
          <div>
            <h2>Create Resume from Job Description</h2>
            <p className="muted" style={{ fontSize: "13px", margin: "4px 0 0" }}>
              Paste any target job description. AI extracts required skills, keywords, and qualifications to construct a 100% ATS-optimized resume.
            </p>
          </div>
          <button 
            type="button" 
            onClick={handleQuickFill} 
            style={{ fontSize: "12px", padding: "6px 12px", background: "rgba(139, 92, 246, 0.15)", color: "#c084fc", border: "1px solid rgba(139, 92, 246, 0.3)" }}
          >
            ⚡ Sample JD
          </button>
        </div>

        <form onSubmit={handleGenerate}>
          <div className="grid2">
            <div>
              <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500 }}>Target Job Title</label>
              <input
                value={targetTitle}
                onChange={(e) => setTargetTitle(e.target.value)}
                placeholder="e.g. Senior Full Stack Engineer"
              />
            </div>
            <div>
              <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500 }}>Candidate Name</label>
              <input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Aryan Kotur"
              />
            </div>
          </div>

          <div style={{ marginTop: "10px" }}>
            <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500 }}>
              Job Description (Required)
            </label>
            <textarea
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job posting or job requirements here..."
              required
            />
          </div>

          <div style={{ marginTop: "10px" }}>
            <label style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: 500 }}>
              Your Background / Notes (Optional)
            </label>
            <textarea
              rows={3}
              value={userNotes}
              onChange={(e) => setUserNotes(e.target.value)}
              placeholder="Paste your past experience, skills, projects or rough points for AI to incorporate..."
            />
          </div>

          <button
            type="submit"
            className="primary"
            disabled={loading || !jobDescription.trim()}
            style={{
              width: "100%",
              marginTop: "16px",
              padding: "12px",
              fontSize: "14.5px",
              fontWeight: 600,
              background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
            }}
          >
            {loading ? "⏳ Generating ATS Tailored Resume with AI..." : "✨ Generate ATS Tailored Resume"}
          </button>
        </form>

        {loading && (
          <div style={{ marginTop: "14px", padding: "14px", borderRadius: "8px", background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.25)", color: "#c084fc", fontSize: "13.5px" }}>
            <strong>Analyzing Job Description...</strong>
            <ul style={{ margin: "6px 0 0", paddingLeft: "20px", fontSize: "12.5px" }}>
              <li>Extracting required hard skills, tools, and methodologies</li>
              <li>Composing ATS-targeted professional summary</li>
              <li>Writing metric-driven experience bullets with action verbs</li>
              <li>Formatting strictly for applicant tracking systems</li>
            </ul>
          </div>
        )}

        {error && (
          <div className="error" style={{ marginTop: "14px", padding: "12px", borderRadius: "8px" }}>
            <strong>Error: </strong> {error}
          </div>
        )}

        {generatedResume && (
          <div style={{ marginTop: "24px", paddingTop: "18px", borderTop: "1px solid var(--border-subtle)" }}>
            <h3>Resume Actions</h3>
            <div className="toolbar" style={{ marginTop: "8px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
              <button 
                type="button"
                onClick={handleSave}
                style={{ background: saveSuccess ? "#16a34a" : undefined }}
              >
                {saveSuccess ? "✓ Saved to Database" : "💾 Save to Database"}
              </button>
              <button type="button" onClick={handleCustomize}>
                ✏️ Edit in Builder
              </button>
              <button type="button" onClick={() => window.print()}>
                🖨️ Print / PDF
              </button>
              <button 
                type="button" 
                className="ai" 
                onClick={handleRunReview} 
                disabled={reviewLoading}
              >
                {reviewLoading ? "Analyzing..." : "🎯 Check ATS Score"}
              </button>
            </div>

            {review && (
              <div style={{ marginTop: "20px" }}>
                <h3>ATS Match Analysis</h3>
                <ReviewResult result={review} />
              </div>
            )}
          </div>
        )}
      </section>

      <section className="preview">
        {generatedResume ? (
          <ResumePreview r={generatedResume} />
        ) : (
          <div style={{
            background: "var(--bg-panel)",
            border: "2px dashed var(--border-subtle)",
            borderRadius: "14px",
            padding: "48px 24px",
            textAlign: "center",
            color: "var(--text-secondary)"
          }}>
            <div style={{ fontSize: "42px", marginBottom: "16px" }}>📄</div>
            <h3 style={{ margin: "0 0 8px", color: "var(--text-main)", fontSize: "16px", textTransform: "none" }}>
              ATS Resume Preview
            </h3>
            <p style={{ margin: "0 auto", maxWidth: "420px", fontSize: "13.5px", lineHeight: "1.6" }}>
              Paste a Job Description on the left and click <strong>"Generate ATS Tailored Resume"</strong>.
              Your tailored resume will appear here formatted with ATS-safe headings and layout.
            </p>
            <div style={{ marginTop: "24px", display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
              <span className="chip" style={{ fontSize: "12px" }}>✓ Single Column Standard Layout</span>
              <span className="chip" style={{ fontSize: "12px" }}>✓ Exact Keyword Matching</span>
              <span className="chip" style={{ fontSize: "12px" }}>✓ Metric-driven Action Bullets</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
