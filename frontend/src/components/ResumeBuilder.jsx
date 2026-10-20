import { useEffect, useState } from "react";
import { api } from "../api.js";
import { emptyResume } from "../emptyResume.js";
import ResumePreview from "./ResumePreview.jsx";
import ReviewResult from "./ReviewResult.jsx";

export default function ResumeBuilder({ initialResume }) {
  const [resume, setResume] = useState(initialResume?.data || emptyResume);
  const [resumeId, setResumeId] = useState(initialResume?.id || null);
  const [title, setTitle] = useState(initialResume?.title || "My Resume");
  const [saved, setSaved] = useState([]);
  const [targetRole, setTargetRole] = useState(initialResume?.targetRole || "");
  const [jobDescription, setJobDescription] = useState(initialResume?.jobDescription || "");
  const [review, setReview] = useState(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const refreshList = () => api.listResumes().then(setSaved).catch(() => {});
  useEffect(() => { refreshList(); }, []);

  useEffect(() => {
    if (initialResume?.data) {
      setResume({ ...emptyResume, ...initialResume.data });
      if (initialResume.title) setTitle(initialResume.title);
      if (initialResume.id !== undefined) setResumeId(initialResume.id);
      if (initialResume.targetRole) setTargetRole(initialResume.targetRole);
      if (initialResume.jobDescription) setJobDescription(initialResume.jobDescription);
    }
  }, [initialResume]);

  const set = (field, value) => setResume((r) => ({ ...r, [field]: value }));
  const setItem = (field, i, patch) =>
    setResume((r) => ({ ...r, [field]: r[field].map((x, idx) => (idx === i ? { ...x, ...patch } : x)) }));
  const addItem = (field, blank) => setResume((r) => ({ ...r, [field]: [...r[field], blank] }));
  const removeItem = (field, i) => setResume((r) => ({ ...r, [field]: r[field].filter((_, idx) => idx !== i) }));

  const run = async (label, fn) => {
    setBusy(label); setError("");
    try { await fn(); } catch (e) { setError(e.message); } finally { setBusy(""); }
  };

  const save = () => run("save", async () => {
    const row = resumeId ? await api.updateResume(resumeId, title, resume) : await api.createResume(title, resume);
    setResumeId(row.id);
    refreshList();
  });

  const load = (id) => run("load", async () => {
    const row = await api.getResume(id);
    setResume({ ...emptyResume, ...row.data }); setTitle(row.title); setResumeId(row.id); setReview(null);
  });

  const remove = (id) => run("delete", async () => {
    await api.deleteResume(id);
    if (id === resumeId) { setResumeId(null); setResume(emptyResume); }
    refreshList();
  });

  const importPdf = (file) => file && run("import", async () => {
    const data = await api.importPdf(file);
    setResume({ ...emptyResume, ...data }); setResumeId(null);
  });

  const improveBullet = (field, i, j) => run(`bullet-${field}-${i}-${j}`, async () => {
    const item = resume[field][i];
    const { improved } = await api.improveBullet({
      role: item.title || item.name || "", targetRole, bullet: item.bullets[j],
    });
    const bullets = item.bullets.map((b, k) => (k === j ? improved : b));
    setItem(field, i, { bullets });
  });

  const generateSummary = () => run("summary", async () => {
    const { summary } = await api.generateSummary({ targetRole, skills: resume.skills, experience: resume.experience });
    set("summary", summary);
  });

  const runReview = () => run("review", async () => {
    setReview(await api.reviewBuilt(resume, jobDescription, resumeId));
  });

  return (
    <div className="split">
      <section className="panel no-print">
        <div className="toolbar">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Resume title" />
          <button onClick={save} disabled={!!busy}>{busy === "save" ? "Saving..." : resumeId ? "Update" : "Save"}</button>
          <label className="btn">
            Import PDF
            <input type="file" accept="application/pdf" hidden onChange={(e) => importPdf(e.target.files[0])} />
          </label>
          <button onClick={() => window.print()}>Print / PDF</button>
        </div>

        {saved.length > 0 && (
          <div className="saved">
            {saved.map((s) => (
              <span key={s.id} className="chip">
                <a onClick={() => load(s.id)}>{s.title}</a>
                <b onClick={() => remove(s.id)} title="Delete">x</b>
              </span>
            ))}
          </div>
        )}

        {error && <p className="error">{error}</p>}
        {busy === "import" && <p>Reading PDF with AI...</p>}

        <h3>Target</h3>
        <input value={targetRole} onChange={(e) => setTargetRole(e.target.value)} placeholder="Target job title (e.g. Full Stack Developer)" />

        <h3>Basics</h3>
        <div className="grid2">
          <input value={resume.fullName} onChange={(e) => set("fullName", e.target.value)} placeholder="Full name" />
          <input value={resume.email} onChange={(e) => set("email", e.target.value)} placeholder="Email" />
          <input value={resume.phone} onChange={(e) => set("phone", e.target.value)} placeholder="Phone" />
          <input value={resume.location} onChange={(e) => set("location", e.target.value)} placeholder="City, State" />
        </div>
        <input value={resume.links.join(", ")} onChange={(e) => set("links", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} placeholder="Links (LinkedIn, GitHub) comma separated" />

        <h3>Summary <button className="ai" onClick={generateSummary} disabled={!!busy}>{busy === "summary" ? "..." : "AI write"}</button></h3>
        <textarea rows={3} value={resume.summary} onChange={(e) => set("summary", e.target.value)} />

        <h3>Skills</h3>
        <input value={resume.skills.join(", ")} onChange={(e) => set("skills", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} placeholder="React, Node.js, PostgreSQL, ..." />

        <h3>Experience</h3>
        {resume.experience.map((e, i) => (
          <div key={i} className="card">
            <div className="grid2">
              <input value={e.title} onChange={(ev) => setItem("experience", i, { title: ev.target.value })} placeholder="Job title" />
              <input value={e.company} onChange={(ev) => setItem("experience", i, { company: ev.target.value })} placeholder="Company" />
              <input value={e.start} onChange={(ev) => setItem("experience", i, { start: ev.target.value })} placeholder="Start (Jan 2023)" />
              <input value={e.end} onChange={(ev) => setItem("experience", i, { end: ev.target.value })} placeholder="End (Present)" />
            </div>
            <input value={e.location} onChange={(ev) => setItem("experience", i, { location: ev.target.value })} placeholder="Location" />
            {e.bullets.map((b, j) => (
              <div key={j} className="bullet">
                <textarea rows={2} value={b} onChange={(ev) => setItem("experience", i, { bullets: e.bullets.map((x, k) => (k === j ? ev.target.value : x)) })} placeholder="What did you do? AI will polish it." />
                <button className="ai" disabled={!!busy || !b} onClick={() => improveBullet("experience", i, j)}>
                  {busy === `bullet-experience-${i}-${j}` ? "..." : "AI improve"}
                </button>
              </div>
            ))}
            <button onClick={() => setItem("experience", i, { bullets: [...e.bullets, ""] })}>+ bullet</button>
            <button className="danger" onClick={() => removeItem("experience", i)}>Remove job</button>
          </div>
        ))}
        <button onClick={() => addItem("experience", { company: "", title: "", location: "", start: "", end: "", bullets: [""] })}>+ Add experience</button>

        <h3>Projects</h3>
        {resume.projects.map((p, i) => (
          <div key={i} className="card">
            <div className="grid2">
              <input value={p.name} onChange={(ev) => setItem("projects", i, { name: ev.target.value })} placeholder="Project name" />
              <input value={p.tech} onChange={(ev) => setItem("projects", i, { tech: ev.target.value })} placeholder="Tech used" />
            </div>
            {p.bullets.map((b, j) => (
              <div key={j} className="bullet">
                <textarea rows={2} value={b} onChange={(ev) => setItem("projects", i, { bullets: p.bullets.map((x, k) => (k === j ? ev.target.value : x)) })} />
                <button className="ai" disabled={!!busy || !b} onClick={() => improveBullet("projects", i, j)}>
                  {busy === `bullet-projects-${i}-${j}` ? "..." : "AI improve"}
                </button>
              </div>
            ))}
            <button onClick={() => setItem("projects", i, { bullets: [...p.bullets, ""] })}>+ bullet</button>
            <button className="danger" onClick={() => removeItem("projects", i)}>Remove</button>
          </div>
        ))}
        <button onClick={() => addItem("projects", { name: "", tech: "", bullets: [""] })}>+ Add project</button>

        <h3>Education</h3>
        {resume.education.map((e, i) => (
          <div key={i} className="card">
            <div className="grid2">
              <input value={e.degree} onChange={(ev) => setItem("education", i, { degree: ev.target.value })} placeholder="Degree" />
              <input value={e.school} onChange={(ev) => setItem("education", i, { school: ev.target.value })} placeholder="School / College" />
              <input value={e.start} onChange={(ev) => setItem("education", i, { start: ev.target.value })} placeholder="Start" />
              <input value={e.end} onChange={(ev) => setItem("education", i, { end: ev.target.value })} placeholder="End" />
            </div>
            <input value={e.grade} onChange={(ev) => setItem("education", i, { grade: ev.target.value })} placeholder="CGPA / Percentage" />
            <button className="danger" onClick={() => removeItem("education", i)}>Remove</button>
          </div>
        ))}
        <button onClick={() => addItem("education", { school: "", degree: "", start: "", end: "", grade: "" })}>+ Add education</button>

        <h3>Certifications</h3>
        <input value={resume.certifications.join(", ")} onChange={(e) => set("certifications", e.target.value.split(",").map((s) => s.trim()).filter(Boolean))} placeholder="Comma separated" />

        <h3>Check ATS score</h3>
        <textarea rows={4} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} placeholder="Paste job description (optional but gives better keyword matching)" />
        <button className="primary" onClick={runReview} disabled={!!busy}>{busy === "review" ? "Analyzing..." : "Review my resume"}</button>
        {review && <ReviewResult result={review} />}
      </section>

      <section className="preview">
        <ResumePreview r={resume} />
      </section>
    </div>
  );
}
