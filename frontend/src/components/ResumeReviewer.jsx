import { useEffect, useState } from "react";
import { api } from "../api.js";
import ReviewResult from "./ReviewResult.jsx";

export default function ResumeReviewer() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadHistory = () => api.listReviews().then(setHistory).catch(() => {});
  useEffect(() => { loadHistory(); }, []);

  const handleFileSelect = async (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await api.reviewUpload(selectedFile, jobDescription);
      setResult(res);
      loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!file) return setError("Please choose a PDF resume first.");
    handleFileSelect(file);
  };

  const open = async (id) => {
    try { setResult(await api.getReview(id)); } catch (e) { setError(e.message); }
  };

  return (
    <div className="reviewer">
      <section className="panel">
        <h2>Upload your resume (PDF)</h2>
        <p className="muted" style={{ fontSize: "13px", marginTop: "-6px", marginBottom: "14px" }}>
          Select any PDF resume — ATS will automatically analyze and score it immediately!
        </p>
        <input 
          type="file" 
          accept="application/pdf" 
          onChange={(e) => handleFileSelect(e.target.files[0])} 
        />
        
        {loading && (
          <div style={{ padding: "12px", background: "rgba(139, 92, 246, 0.1)", border: "1px solid rgba(139, 92, 246, 0.3)", borderRadius: "8px", margin: "10px 0", color: "#c084fc", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>⏳</span>
            <span><strong>Analyzing PDF with AI...</strong> Reading text and calculating ATS compatibility.</span>
          </div>
        )}

        <h3>Job description (optional)</h3>
        <textarea rows={8} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} placeholder="Paste the job description to get keyword match + missing keywords" />
        
        <button className="primary" onClick={submit} disabled={loading || !file}>
          {loading ? "Analyzing..." : "Re-run ATS Score"}
        </button>

        {error && (
          <div className="error" style={{ marginTop: "12px", padding: "12px", borderRadius: "8px" }}>
            <strong>Error: </strong>{error}
          </div>
        )}

        {history.length > 0 && (
          <>
            <h3>Past reviews</h3>
            <ul className="history">
              {history.map((h) => (
                <li key={h.id} onClick={() => open(h.id)}>
                  <b>{h.ats_score}</b> {h.file_name || "Builder resume"}
                  <small>{new Date(h.created_at).toLocaleString()}</small>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="panel">{result ? <ReviewResult result={result} /> : <p className="muted">Your report will appear here.</p>}</section>
    </div>
  );
}
