import json
from flask import Blueprint, request, jsonify
from psycopg2.extras import Json
from db import query
from utils.pdf_utils import extract_text_from_pdf, resume_to_text
from chains.review_chain import review_resume
from chains.builder_chain import parse_chain

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")

def format_review_summary(row):
    if not row:
        return None
    d = dict(row)
    if "created_at" in d and d["created_at"]:
        d["created_at"] = d["created_at"].isoformat()
    return d

# Review an UPLOADED PDF resume (+ optional job description)
@reviews_bp.route("/upload", methods=["POST"])
def upload_review():
    if "resume" not in request.files:
        return jsonify({"error": "Attach a PDF as 'resume'"}), 400
        
    file = request.files["resume"]
    if not file or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
        
    try:
        text = extract_text_from_pdf(file.stream)
    except Exception as e:
        return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 400
        
    if len(text) < 100:
        return jsonify({
            "error": "Could not read text from this PDF. It may be a scanned image, which ATS systems also cannot read."
        }), 422
        
    job_description = request.form.get("jobDescription", "").strip()
    result = review_resume(text, job_description)
    
    row = query(
        """INSERT INTO reviews (source, file_name, resume_text, job_description, ats_score, result)
           VALUES ('upload', %s, %s, %s, %s, %s) RETURNING id, created_at""",
        [file.filename, text, job_description, result.get("atsScore", 0), Json(result)],
        fetch_one=True,
        commit=True
    )
    
    created_at_iso = row["created_at"].isoformat() if row and row["created_at"] else None
    response_data = {
        "id": row["id"],
        "createdAt": created_at_iso,
        **result
    }
    return jsonify(response_data)

# Review a resume built in the builder (saved in Postgres or sent inline)
@reviews_bp.route("/builder", methods=["POST"])
def builder_review():
    body = request.get_json(silent=True) or {}
    resume_id = body.get("resumeId")
    resume_data = body.get("data")
    job_description = body.get("jobDescription", "").strip()
    
    if resume_id and not resume_data:
        row = query("SELECT data FROM resumes WHERE id = %s", [resume_id], fetch_one=True)
        if not row:
            return jsonify({"error": "Resume not found"}), 404
        resume_data = row["data"]
        
    if not resume_data:
        return jsonify({"error": "Provide resumeId or data"}), 400
        
    text = resume_to_text(resume_data)
    result = review_resume(text, job_description)
    
    row = query(
        """INSERT INTO reviews (resume_id, source, resume_text, job_description, ats_score, result)
           VALUES (%s, 'builder', %s, %s, %s, %s) RETURNING id, created_at""",
        [resume_id or None, text, job_description, result.get("atsScore", 0), Json(result)],
        fetch_one=True,
        commit=True
    )
    
    created_at_iso = row["created_at"].isoformat() if row and row["created_at"] else None
    response_data = {
        "id": row["id"],
        "createdAt": created_at_iso,
        **result
    }
    return jsonify(response_data)

# Import an uploaded PDF INTO the builder (PDF -> structured JSON via LangChain)
@reviews_bp.route("/import", methods=["POST"])
def import_pdf():
    if "resume" not in request.files:
        return jsonify({"error": "Attach a PDF as 'resume'"}), 400
        
    file = request.files["resume"]
    try:
        text = extract_text_from_pdf(file.stream)
    except Exception as e:
        return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 400
        
    parsed = parse_chain.invoke({"text": text})
    result = parsed.model_dump() if hasattr(parsed, "model_dump") else dict(parsed)
    return jsonify(result)

# History list
@reviews_bp.route("", methods=["GET"])
@reviews_bp.route("/", methods=["GET"])
def list_reviews():
    rows = query(
        """SELECT id, resume_id, source, file_name, ats_score, created_at 
           FROM reviews ORDER BY created_at DESC LIMIT 50""",
        fetch_all=True
    )
    return jsonify([format_review_summary(r) for r in (rows or [])])

# Get one review by ID
@reviews_bp.route("/<int:review_id>", methods=["GET"])
def get_review(review_id):
    row = query("SELECT * FROM reviews WHERE id = %s", [review_id], fetch_one=True)
    if not row:
        return jsonify({"error": "Not found"}), 404
        
    created_at_iso = row["created_at"].isoformat() if row["created_at"] else None
    result_data = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
    response_data = {
        "id": row["id"],
        "createdAt": created_at_iso,
        **result_data
    }
    return jsonify(response_data)
