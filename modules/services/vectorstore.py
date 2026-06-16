"""User-isolated ChromaDB vector store.

Isolation strategy: ONE collection per user (``user_<id>``). Every operation is
addressed by ``user_id`` and resolves to that user's own collection, so a query
can never physically reach another user's chunks — there is no shared pool to
forget to filter. Each chunk carries ``user_id``, ``document_id``, ``source``,
``chunk_index`` and ``page`` (0 = non-paginated) metadata.
"""
import chromadb

from config import VECTORSTORE_DIR

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
    return _client


def _collection_name(user_id) -> str:
    return f"user_{int(user_id)}"


def get_user_collection(user_id):
    return _get_client().get_or_create_collection(name=_collection_name(user_id))


def add_document_chunks(user_id, document_id, source: str, chunks: list) -> None:
    """Index chunks for one document inside the owner's collection.

    ``chunks`` may be plain strings (backward-compat) or dicts ``{text, page}``
    as produced by ``chunk_pages()``. Page 0 means non-paginated format.
    """
    collection = get_user_collection(user_id)

    try:
        collection.delete(where={"document_id": int(document_id)})
    except Exception:
        pass

    texts = []
    metadatas = []
    for index, chunk in enumerate(chunks):
        if isinstance(chunk, dict):
            text = chunk.get("text", "")
            page = int(chunk.get("page") or 0)
        else:
            text = chunk
            page = 0
        texts.append(text)
        metadatas.append({
            "user_id": int(user_id),
            "document_id": int(document_id),
            "source": source,
            "chunk_index": index,
            "page": page,
        })

    ids = [f"{int(user_id)}_{int(document_id)}_{i}" for i in range(len(texts))]
    collection.add(documents=texts, ids=ids, metadatas=metadatas)


def search(
    user_id,
    query: str,
    top_k: int = 4,
    max_distance: float | None = None,
    document_id: int | None = None,
) -> list[dict]:
    """Return the closest chunks for ``query`` within the user's collection.

    If ``document_id`` is provided the search is scoped to that document only.
    """
    collection = get_user_collection(user_id)
    total = collection.count()

    if total == 0:
        return []

    where = None
    if document_id is not None:
        where = {"document_id": int(document_id)}

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, total),
        where=where,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits = []
    for content, metadata, distance in zip(documents, metadatas, distances):
        if max_distance is not None and distance is not None and distance > max_distance:
            continue
        metadata = metadata or {}
        hits.append({
            "content": content,
            "source": metadata.get("source", "inconnu"),
            "document_id": metadata.get("document_id"),
            "chunk_index": metadata.get("chunk_index", 0),
            "page": metadata.get("page", 0),
            "distance": distance,
        })

    return hits


def get_document_chunks(user_id, document_id) -> list[dict]:
    """Return ALL chunks of one document ordered by chunk_index.

    Used for synthesis queries where we want the full document content in
    reading order rather than relevance order.
    """
    collection = get_user_collection(user_id)
    if collection.count() == 0:
        return []

    records = collection.get(
        where={"document_id": int(document_id)},
        include=["documents", "metadatas"],
    )

    texts = records.get("documents") or []
    metas = records.get("metadatas") or []

    items = []
    for text, meta in zip(texts, metas):
        meta = meta or {}
        if meta.get("user_id") != int(user_id):
            continue
        items.append({
            "content": text,
            "source": meta.get("source", "inconnu"),
            "document_id": meta.get("document_id"),
            "chunk_index": meta.get("chunk_index", 0),
            "page": meta.get("page", 0),
            "distance": None,
        })

    items.sort(key=lambda x: x["chunk_index"])
    return items


def list_sources(user_id) -> list[str]:
    collection = get_user_collection(user_id)
    if collection.count() == 0:
        return []

    records = collection.get(include=["metadatas"])
    sources = {
        metadata.get("source")
        for metadata in records.get("metadatas", [])
        if metadata and metadata.get("source")
    }
    return sorted(sources)


def get_stats(user_id) -> dict:
    collection = get_user_collection(user_id)
    return {
        "total_chunks": collection.count(),
        "sources": list_sources(user_id),
    }


def delete_document_chunks(user_id, document_id) -> None:
    collection = get_user_collection(user_id)
    try:
        collection.delete(where={"document_id": int(document_id)})
    except Exception:
        pass


def delete_user_collection(user_id) -> None:
    try:
        _get_client().delete_collection(name=_collection_name(user_id))
    except Exception:
        pass


def delete_legacy_collection(name: str) -> None:
    try:
        _get_client().delete_collection(name=name)
    except Exception:
        pass
