"""Authenticated JSON API for user-private data: conversations, documents, account.

Every endpoint is login-protected and enforces ownership server-side. Resources
that do not belong to ``current_user`` answer 404 (never reveal existence).
Mutating endpoints are CSRF-protected via the ``X-CSRFToken`` header sent by the
frontend (the token is exposed in a <meta> tag).
"""
from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required, logout_user

from extensions import db
from models import Conversation, Document, Message
from modules.services.user_files import delete_user_dir, delete_user_file
from modules.services.vectorstore import delete_document_chunks, delete_user_collection

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _owned_conversation_or_404(conversation_id) -> Conversation:
    conversation = db.session.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        abort(404)
    return conversation


def _owned_document_or_404(document_id) -> Document:
    document = db.session.get(Document, document_id)
    if document is None or document.user_id != current_user.id:
        abort(404)
    return document


# ── Conversations ───────────────────────────────────────────────────────────
@api_bp.route("/conversations", methods=["GET"])
@login_required
def list_conversations():
    conversations = (
        Conversation.query
        .filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in conversations])


@api_bp.route("/conversations", methods=["POST"])
@login_required
def create_conversation():
    conversation = Conversation(user_id=current_user.id, title="Nouveau chat")
    db.session.add(conversation)
    db.session.commit()
    return jsonify(conversation.to_dict()), 201


@api_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@login_required
def get_conversation(conversation_id):
    conversation = _owned_conversation_or_404(conversation_id)
    return jsonify(conversation.to_dict(with_messages=True))


@api_bp.route("/conversations/<int:conversation_id>", methods=["PATCH"])
@login_required
def rename_conversation(conversation_id):
    conversation = _owned_conversation_or_404(conversation_id)
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Le titre est requis."}), 400
    conversation.title = title[:200]
    db.session.commit()
    return jsonify(conversation.to_dict())


@api_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
@login_required
def delete_conversation(conversation_id):
    conversation = _owned_conversation_or_404(conversation_id)
    db.session.delete(conversation)  # cascade removes its messages
    db.session.commit()
    return jsonify({"success": True})


# ── Documents ───────────────────────────────────────────────────────────────
@api_bp.route("/documents", methods=["GET"])
@login_required
def list_documents():
    documents = (
        Document.query
        .filter_by(user_id=current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return jsonify([d.to_dict() for d in documents])


@api_bp.route("/documents/<int:document_id>", methods=["GET"])
@login_required
def get_document(document_id):
    document = _owned_document_or_404(document_id)
    return jsonify(document.to_dict())


@api_bp.route("/documents/<int:document_id>", methods=["DELETE"])
@login_required
def delete_document(document_id):
    document = _owned_document_or_404(document_id)

    # 1. Chroma chunks, 2. physical file, 3. SQL row — all owner-scoped.
    delete_document_chunks(current_user.id, document.id)
    delete_user_file(current_user.id, document.stored_filename)
    db.session.delete(document)
    db.session.commit()
    return jsonify({"success": True})


# ── Account ─────────────────────────────────────────────────────────────────
def purge_user_data(user) -> None:
    """Full, owner-scoped cleanup: files, Chroma collection, SQL rows."""
    delete_user_collection(user.id)
    delete_user_dir(user.id)
    db.session.delete(user)  # cascade removes documents, conversations, messages
    db.session.commit()


@api_bp.route("/account", methods=["DELETE"])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    purge_user_data(user)
    return jsonify({"success": True})
