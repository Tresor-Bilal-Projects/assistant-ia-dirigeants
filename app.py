import os
import secrets
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, COLLECTION_NAME, MAX_UPLOAD_MB, TOP_K
from extensions import csrf, db, login_manager
from models import Conversation, Document, Message, User
from auth import auth_bp
from api_routes import api_bp
from modules.llm.hf_client import chat_completion
from modules.llm.system_prompt import SYSTEM_PROMPT
from modules.services.ingestion import ingest_file
from modules.services.rag import build_rag_context, build_system_prompt, rag_status
from modules.services.user_files import (
    delete_user_file,
    make_stored_filename,
    user_file_path,
)
from modules.services.vectorstore import delete_document_chunks, delete_legacy_collection


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    """Enforce ON DELETE CASCADE for SQLite (off by default)."""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass


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
app.register_blueprint(api_bp)


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


@app.cli.command("reset-rag")
def reset_rag_command():
    """Purge the legacy pre-isolation global vector store.

    Old development chunks (collection 'company_docs') are NOT migrated to any
    user. This drops that legacy collection so global and private data never mix.
    Per-user collections (user_<id>) and uploaded files are left untouched.
    """
    delete_legacy_collection(COLLECTION_NAME)
    print(f"Legacy collection '{COLLECTION_NAME}' removed (if it existed).")
    print("Per-user collections and files were left untouched.")


@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/api/rag/status", methods=["GET"])
@login_required
def rag_status_route():
    return jsonify(rag_status(current_user.id))


@app.route("/upload", methods=["POST"])
@csrf.exempt
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier fourni."}), 400

    file = request.files["file"]

    if not file or not file.filename:
        return jsonify({"error": "Fichier invalide."}), 400

    original_filename = secure_filename(file.filename)
    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": "Format non supporté. Utilisez PDF, TXT ou DOCX."
        }), 400

    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    file.seek(0)

    if size_bytes / (1024 * 1024) > MAX_UPLOAD_MB:
        return jsonify({
            "error": f"Fichier trop volumineux (max {MAX_UPLOAD_MB} Mo)."
        }), 400

    # Server-generated internal name under the user's own folder (no collisions,
    # no user-controlled path).
    stored_filename = make_stored_filename(extension)
    filepath = user_file_path(current_user.id, stored_filename)
    file.save(filepath)

    # Create the owned Document row first so we have its id for chunk metadata.
    document = Document(
        user_id=current_user.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=extension.lstrip("."),
        file_size=size_bytes,
        chunk_count=0,
    )
    db.session.add(document)
    db.session.flush()  # assign document.id without committing yet
    document_id = document.id

    try:
        result = ingest_file(str(filepath), current_user.id, document_id, original_filename)
        document.chunk_count = result["chunks"]
        db.session.commit()

        return jsonify({
            "success": True,
            "document_id": document_id,
            "filename": original_filename,
            "chunks_indexed": result["chunks"],
            "characters": result["characters"],
            "message": (
                f"Document '{original_filename}' indexé avec succès "
                f"({result['chunks']} fragments vectorisés)."
            ),
        })

    except Exception as error:
        db.session.rollback()
        # Roll back side effects: physical file + any chunks already written.
        delete_user_file(current_user.id, stored_filename)
        delete_document_chunks(current_user.id, document_id)
        return jsonify({"error": str(error)}), 500


def _resolve_chat_conversation(conversation_id):
    """Return an owned Conversation, creating one if none was provided.

    Returns ``None`` when a conversation_id is supplied but is not owned by the
    current user (caller answers 404). Never trusts the id blindly.
    """
    if conversation_id in (None, "", 0):
        conversation = Conversation(user_id=current_user.id, title="Nouveau chat")
        db.session.add(conversation)
        db.session.flush()
        return conversation

    try:
        conversation_id = int(conversation_id)
    except (TypeError, ValueError):
        return None

    conversation = db.session.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        return None
    return conversation


@app.route("/chat", methods=["POST"])
@csrf.exempt
@login_required
def chat():
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"response": "Veuillez saisir une question."}), 400

    conversation = _resolve_chat_conversation(data.get("conversation_id"))
    if conversation is None:
        return jsonify({"error": "Conversation introuvable."}), 404

    # 1. Persist the user message and (lazily) title the conversation.
    db.session.add(Message(conversation_id=conversation.id, role="user", content=message))
    if not conversation.title or conversation.title == "Nouveau chat":
        conversation.title = message[:40] + "..." if len(message) > 40 else message
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    # 2. Retrieval is scoped to THIS user's documents only.
    # active_document_id narrows the search to a specific document (e.g. just
    # uploaded) so synthesis queries stay focused on that document.
    active_document_id = data.get("active_document_id") or None
    if active_document_id is not None:
        try:
            active_document_id = int(active_document_id)
        except (TypeError, ValueError):
            active_document_id = None
    context, sources = build_rag_context(current_user.id, message, top_k=TOP_K, document_id=active_document_id)
    system_prompt = build_system_prompt(SYSTEM_PROMPT, context)
    rag_used = bool(context)

    try:
        reply = chat_completion(system_prompt, message)
        status = 200
    except Exception as error:
        reply = f"Erreur serveur: {str(error)}"
        status = 500

    # 3. Persist the assistant reply (even on LLM error, for history fidelity).
    db.session.add(Message(conversation_id=conversation.id, role="assistant", content=reply))
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    payload = {
        "response": reply,
        "rag_used": rag_used,
        "sources": sources,
        "conversation_id": conversation.id,
        "title": conversation.title,
    }
    if rag_used:
        payload["context_chunks"] = len(sources)
    return jsonify(payload), status


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
