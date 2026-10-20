const color = (n) => (n >= 80 ? "#16a34a" : n >= 60 ? "#d97706" : "#dc2626");

function Bar({ label, value }) {
  return (
    <div className="barrow">
      <span>{label}</span>
      <div className="bar"><div style={{ width: `${value}%`, background: color(value) }} /></div>
      <b>{value}</b>
    </div>
  );
}

export default function ReviewResult({ result }) {
  const { atsScore, breakdown, summary, strengths, issues, matchedKeywords, missingKeywords, rewrittenBullets } = result;

  return (
    <div className="result">
      <div className="score" style={{ borderColor: color(atsScore), color: color(atsScore) }}>
        {atsScore}<small>/100</small>
      </div>
      <p>{summary}</p>

      <h3>Breakdown</h3>
      {Object.entries(breakdown).map(([k, v]) => <Bar key={k} label={k} value={v} />)}

      <h3>Strengths</h3>
      <ul>{strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>

      <h3>Fix these</h3>
      {issues.map((it, i) => (
        <div key={i} className={`issue ${it.severity}`}>
          <b>[{it.severity}] {it.section}</b>
          <p>{it.problem}</p>
          <p><em>Fix:</em> {it.fix}</p>
        </div>
      ))}

      <h3>Keywords</h3>
      <div className="tags">{matchedKeywords.map((k) => <span key={k} className="tag ok">{k}</span>)}</div>
      <div className="tags">{missingKeywords.map((k) => <span key={k} className="tag miss">{k}</span>)}</div>

      {rewrittenBullets?.length > 0 && (
        <>
          <h3>Better bullet points</h3>
          {rewrittenBullets.map((b, i) => (
            <div key={i} className="rewrite">
              <p className="old">{b.original}</p>
              <p className="new">{b.improved}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
