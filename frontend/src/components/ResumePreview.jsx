// ATS-safe layout: ONE column, real text (no images/tables/icons), standard headings,
// system fonts. "Print / Save as PDF" produces a text-selectable PDF that ATS can parse.
export default function ResumePreview({ r }) {
  const contact = [r.email, r.phone, r.location, ...(r.links || [])].filter(Boolean).join(" | ");

  return (
    <article className="paper" id="resume-paper">
      <h1>{r.fullName || "Your Name"}</h1>
      <p className="contact">{contact}</p>

      {r.summary && (
        <section>
          <h2>SUMMARY</h2>
          <p>{r.summary}</p>
        </section>
      )}

      {r.skills?.length > 0 && (
        <section>
          <h2>SKILLS</h2>
          <ul className="vertical-list skills-list">
            {r.skills.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </section>
      )}

      {r.experience?.some((e) => e.company || e.title) && (
        <section>
          <h2>EXPERIENCE</h2>
          {r.experience.map((e, i) => (
            <div key={i} className="entry">
              <p className="row">
                <strong>{e.title}{e.company && `, ${e.company}`}</strong>
                <span>{[e.start, e.end].filter(Boolean).join(" - ")}</span>
              </p>
              {e.location && <p className="muted">{e.location}</p>}
              <ul>{(e.bullets || []).filter(Boolean).map((b, j) => <li key={j}>{b}</li>)}</ul>
            </div>
          ))}
        </section>
      )}

      {r.projects?.length > 0 && (
        <section>
          <h2>PROJECTS</h2>
          {r.projects.map((p, i) => (
            <div key={i} className="entry">
              <p><strong>{p.name}</strong>{p.tech && ` | ${p.tech}`}</p>
              <ul>{(p.bullets || []).filter(Boolean).map((b, j) => <li key={j}>{b}</li>)}</ul>
            </div>
          ))}
        </section>
      )}

      {r.education?.some((e) => e.school) && (
        <section>
          <h2>EDUCATION</h2>
          {r.education.map((e, i) => (
            <p key={i} className="row">
              <span><strong>{e.degree}</strong>{e.school && `, ${e.school}`}{e.grade && ` | ${e.grade}`}</span>
              <span>{[e.start, e.end].filter(Boolean).join(" - ")}</span>
            </p>
          ))}
        </section>
      )}

      {r.certifications?.length > 0 && (
        <section>
          <h2>CERTIFICATIONS</h2>
          <ul className="vertical-list certs-list">
            {r.certifications.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}
