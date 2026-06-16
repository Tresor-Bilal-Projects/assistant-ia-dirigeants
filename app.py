import os
import secrets

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, TOP_K, UPLOAD_DIR
from extensions import csrf, db, login_manager
from models import User
from auth import auth_bp
from modules.llm.hf_client import chat_completion
from modules.llm.system_prompt import SYSTEM_PROMPT
from modules.services.ingestion import ingest_file
from modules.services.rag import build_rag_context, build_system_prompt, rag_status

app = Flask(__name__)

# --- Security / session configuration ---------------------------------------
# SECRET_KEY must come from the environment (.env). Never hard-code it.
_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    _secret_key = secrets.token_hex(32)
    app.logger.warning(
        "SECRET_KEY is not set; using an ephemeral key (sessions reset on every "
        "restart). Set SECRET_KEY in your .env for stable sessions."
    )
app.config["SECRET_KEY"] = _secret_key

os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(app.instance_path, "users.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# --- Extensions --------------------------------------------------------------
db.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Veuillez vous connecter pour accéder au chat."
login_manager.login_message_category = "error"

app.register_blueprint(auth_bp)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def _handle_unauthorized():
    # JSON endpoints must answer with a clean 401 rather than an HTML redirect.
    if request.path.startswith(("/chat", "/upload", "/api/")):
        return jsonify({"error": "Authentification requise."}), 401
    return redirect(url_for("auth.login", next=request.path))


@app.cli.command("init-db")
def init_db_command():
    """Create the database tables (idempotent)."""
    db.create_all()
    print("Database initialised at", app.config["SQLALCHEMY_DATABASE_URI"])


@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/api/rag/status", methods=["GET"])
@login_required
def rag_status_route():
    return jsonify(rag_status())


@app.route("/upload", methods=["POST"])
@csrf.exempt
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier fourni."}), 400

    file = request.files["file"]

    if not file or not file.filename:
        return jsonify({"error": "Fichier invalide."}), 400

    filename = secure_filename(file.filename)
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": "Format non supporté. Utilisez PDF, TXT ou DOCX."
        }), 400

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)

    if size_mb > MAX_UPLOAD_MB:
        return jsonify({
            "error": f"Fichier trop volumineux (max {MAX_UPLOAD_MB} Mo)."
        }), 400

    filepath = UPLOAD_DIR / filename
    file.save(filepath)

    try:
        result = ingest_file(str(filepath), filename)

        return jsonify({
            "success": True,
            "filename": filename,
            "chunks_indexed": result["chunks"],
            "characters": result["characters"],
            "message": (
                f"Document '{filename}' indexé avec succès "
                f"({result['chunks']} fragments vectorisés)."
            ),
        })

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@app.route("/chat", methods=["POST"])
@csrf.exempt
@login_required
def chat():
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"response": "Veuillez saisir une question."}), 400

    context, sources = build_rag_context(message, top_k=TOP_K)
    system_prompt = build_system_prompt(SYSTEM_PROMPT, context)
    rag_used = bool(context)

    try:
        reply = chat_completion(system_prompt, message)

        response_payload = {
            "response": reply,
            "rag_used": rag_used,
            "sources": sources,
        }

        if rag_used:
            response_payload["context_chunks"] = len(sources)

        return jsonify(response_payload)

    except Exception as error:
        return jsonify({
            "response": f"Erreur serveur: {str(error)}",
            "rag_used": rag_used,
            "sources": sources,
        }), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
