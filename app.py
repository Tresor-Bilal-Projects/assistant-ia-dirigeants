import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, TOP_K, UPLOAD_DIR
from modules.llm.hf_client import chat_completion
from modules.llm.system_prompt import SYSTEM_PROMPT
from modules.services.ingestion import ingest_file
from modules.services.rag import build_rag_context, build_system_prompt, rag_status

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/rag/status", methods=["GET"])
def rag_status_route():
    return jsonify(rag_status())


@app.route("/upload", methods=["POST"])
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
    app.run(debug=True)
