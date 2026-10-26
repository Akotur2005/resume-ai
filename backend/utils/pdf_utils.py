import io
import re
from pypdf import PdfReader

def extract_text_from_pdf(file_bytes_or_stream):
    """Extract clean text from PDF bytes or file-like object."""
    if isinstance(file_bytes_or_stream, (bytes, bytearray)):
        stream = io.BytesIO(file_bytes_or_stream)
    else:
        stream = file_bytes_or_stream
        
    reader = PdfReader(stream)
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)
            
    full_text = "\n".join(text_parts)
    # Normalize line breaks
    full_text = full_text.replace("\r", "")
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)
    return full_text.strip()

def resume_to_text(r):
    """Turn the structured resume dictionary into plain text for ATS review."""
    if not isinstance(r, dict):
        return ""
        
    lines = []
    full_name = r.get("fullName", "")
    contact_parts = [
        r.get("email"),
        r.get("phone"),
        r.get("location"),
        *(r.get("links") or [])
    ]
    contact_str = " | ".join([p for p in contact_parts if p])
    
    if full_name:
        lines.append(full_name)
    if contact_str:
        lines.append(contact_str)
        
    if r.get("summary"):
        lines.extend(["\nSUMMARY", r.get("summary")])
        
    skills = r.get("skills")
    if skills:
        lines.extend(["\nSKILLS", ", ".join(skills)])
        
    experience = r.get("experience")
    if experience:
        lines.append("\nEXPERIENCE")
        for e in experience:
            title = e.get("title", "")
            company = e.get("company", "")
            location = e.get("location", "")
            start = e.get("start", "")
            end = e.get("end", "")
            lines.append(f"{title} - {company}, {location} ({start} - {end})")
            for b in (e.get("bullets") or []):
                lines.append(f"- {b}")
                
    projects = r.get("projects")
    if projects:
        lines.append("\nPROJECTS")
        for p in projects:
            name = p.get("name", "")
            tech = p.get("tech", "")
            lines.append(f"{name} ({tech})")
            for b in (p.get("bullets") or []):
                lines.append(f"- {b}")
                
    education = r.get("education")
    if education:
        lines.append("\nEDUCATION")
        for ed in education:
            degree = ed.get("degree", "")
            school = ed.get("school", "")
            start = ed.get("start", "")
            end = ed.get("end", "")
            grade = ed.get("grade", "")
            lines.append(f"{degree} - {school} ({start} - {end}) {grade}".strip())
            
    certifications = r.get("certifications")
    if certifications:
        lines.extend(["\nCERTIFICATIONS", ", ".join(certifications)])
        
    return "\n".join(lines)
