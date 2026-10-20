import pdfParse from "pdf-parse/lib/pdf-parse.js"; // direct path avoids pdf-parse's debug-mode bug

export async function extractTextFromPdf(buffer) {
  const { text } = await pdfParse(buffer);
  return text.replace(/\r/g, "").replace(/\n{3,}/g, "\n\n").trim();
}

// Turn the structured resume JSON into plain text the reviewer chain can read.
export function resumeToText(r) {
  const lines = [];
  lines.push(r.fullName, [r.email, r.phone, r.location, ...(r.links || [])].filter(Boolean).join(" | "));
  if (r.summary) lines.push("\nSUMMARY", r.summary);
  if (r.skills?.length) lines.push("\nSKILLS", r.skills.join(", "));
  if (r.experience?.length) {
    lines.push("\nEXPERIENCE");
    r.experience.forEach((e) => {
      lines.push(`${e.title} - ${e.company}, ${e.location} (${e.start} - ${e.end})`);
      (e.bullets || []).forEach((b) => lines.push(`- ${b}`));
    });
  }
  if (r.projects?.length) {
    lines.push("\nPROJECTS");
    r.projects.forEach((p) => {
      lines.push(`${p.name} (${p.tech})`);
      (p.bullets || []).forEach((b) => lines.push(`- ${b}`));
    });
  }
  if (r.education?.length) {
    lines.push("\nEDUCATION");
    r.education.forEach((e) => lines.push(`${e.degree} - ${e.school} (${e.start} - ${e.end}) ${e.grade}`));
  }
  if (r.certifications?.length) lines.push("\nCERTIFICATIONS", r.certifications.join(", "));
  return lines.join("\n");
}
