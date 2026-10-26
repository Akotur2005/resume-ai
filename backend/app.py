import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

from routes.resumes import resumes_bp
from routes.reviews import reviews_bp

app = Flask(__name__)

# Max upload limit (e.g. 5MB)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Setup CORS to allow Vite frontend
client_origin = os.getenv("CLIENT_ORIGIN", "http://localhost:5173")
origins_list = [client_origin, "http://localhost:5173", "http://localhost:5174", r"^http:\/\/localhost:\d+$"]

CORS(
    app,
    resources={r"/api/*": {"origins": origins_list}},
    supports_credentials=True
)

# Register Blueprints
app.register_blueprint(resumes_bp)
app.register_blueprint(reviews_bp)

# Health check
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# Central error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Log traceback in console
    import traceback
    traceback.print_exc()
    status_code = getattr(e, "code", 500)
    return jsonify({"error": str(e) or "Server error"}), status_code

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Python Flask API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
