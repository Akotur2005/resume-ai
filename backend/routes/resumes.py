import json
from flask import Blueprint, request, jsonify
from psycopg2.extras import Json
from db import query
from chains.builder_chain import bullet_chain, summary_chain, generate_from_jd_chain

resumes_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")

def format_row(row):
    """Format row for JSON response, converting datetime to ISO string."""
    if not row:
        return None
    d = dict(row)
    if "created_at" in d and d["created_at"]:
        d["created_at"] = d["created_at"].isoformat()
    if "updated_at" in d and d["updated_at"]:
        d["updated_at"] = d["updated_at"].isoformat()
    return d

# List saved resumes
@resumes_bp.route("", methods=["GET"])
@resumes_bp.route("/", methods=["GET"])
def list_resumes():
    rows = query(
        "SELECT id, title, updated_at FROM resumes ORDER BY updated_at DESC",
        fetch_all=True
    )
    return jsonify([format_row(r) for r in (rows or [])])

# Get one resume
@resumes_bp.route("/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    row = query(
        "SELECT * FROM resumes WHERE id = %s",
        [resume_id],
        fetch_one=True
    )
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(format_row(row))

# Create resume
@resumes_bp.route("", methods=["POST"])
@resumes_bp.route("/", methods=["POST"])
def create_resume():
    body = request.get_json(silent=True) or {}
    title = body.get("title", "My Resume")
    data = body.get("data")
    if not data:
        return jsonify({"error": "data is required"}), 400

    row = query(
        "INSERT INTO resumes (title, data) VALUES (%s, %s) RETURNING *",
        [title, Json(data)],
        fetch_one=True,
        commit=True
    )
    return jsonify(format_row(row)), 201

# Update resume
@resumes_bp.route("/<int:resume_id>", methods=["PUT"])
def update_resume(resume_id):
    body = request.get_json(silent=True) or {}
    title = body.get("title")
    data = body.get("data")
    
    row = query(
        """UPDATE resumes SET 
             title = COALESCE(%s, title), 
             data = COALESCE(%s, data), 
             updated_at = NOW()
           WHERE id = %s RETURNING *""",
        [title, Json(data) if data is not None else None, resume_id],
        fetch_one=True,
        commit=True
    )
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(format_row(row))

# Delete resume
@resumes_bp.route("/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    query("DELETE FROM resumes WHERE id = %s", [resume_id], commit=True)
    return "", 204

# ---- AI helpers used by the builder form ----
@resumes_bp.route("/ai/bullet", methods=["POST"])
def ai_bullet():
    body = request.get_json(silent=True) or {}
    bullet = body.get("bullet")
    if not bullet:
        return jsonify({"error": "bullet is required"}), 400
        
    role = body.get("role", "")
    target_role = body.get("targetRole", "")
    improved = bullet_chain.invoke({
        "role": role,
        "targetRole": target_role,
        "bullet": bullet
    })
    return jsonify({"improved": improved.strip()})

@resumes_bp.route("/ai/summary", methods=["POST"])
def ai_summary():
    body = request.get_json(silent=True) or {}
    target_role = body.get("targetRole", "")
    skills = body.get("skills") or []
    experience = body.get("experience") or []
    
    exp_lines = []
    for e in experience:
        title = e.get("title", "")
        company = e.get("company", "")
        start = e.get("start", "")
        end = e.get("end", "")
        bullets = "; ".join(e.get("bullets") or [])
        exp_lines.append(f"{title} at {company} ({start}-{end}): {bullets}")
    exp_text = "\n".join(exp_lines)
    
    summary = summary_chain.invoke({
        "targetRole": target_role,
        "skills": ", ".join(skills),
        "experience": exp_text
    })
    return jsonify({"summary": summary.strip()})

@resumes_bp.route("/ai/from-jd", methods=["POST"])
def ai_from_jd():
    body = request.get_json(silent=True) or {}
    job_description = body.get("jobDescription", "").strip()
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400
        
    user_notes = body.get("userNotes", "")
    full_name = body.get("fullName", "") or "Your Name"
    target_title = body.get("targetTitle", "")
    
    resume_data = generate_from_jd_chain.invoke({
        "jobDescription": job_description,
        "userNotes": user_notes,
        "fullName": full_name,
        "targetTitle": target_title,
    })
    
    result = resume_data.model_dump() if hasattr(resume_data, "model_dump") else dict(resume_data)
    return jsonify(result)
