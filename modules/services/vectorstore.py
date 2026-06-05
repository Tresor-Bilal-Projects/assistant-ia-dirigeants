import chromadb

from config import COLLECTION_NAME, VECTORSTORE_DIR

_client = None
_collection = None


def get_collection():
    global _client, _collection

    if _collection is None:
        _client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)

    return _collection


def add_document_chunks(filename: str, chunks: list[str]) -> None:
    collection = get_collection()

    try:
        collection.delete(where={"source": filename})
    except Exception:
        pass

    ids = [f"{filename}__{index}" for index in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": index} for index in range(len(chunks))]

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas,
    )


def search(query: str, top_k: int = 4) -> list[dict]:
    collection = get_collection()
    total = collection.count()

    if total == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, total),
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits = []
    for content, metadata, distance in zip(documents, metadatas, distances):
        hits.append({
            "content": content,
            "source": metadata.get("source", "inconnu"),
            "chunk_index": metadata.get("chunk_index", 0),
            "distance": distance,
        })

    return hits


def list_sources() -> list[str]:
    collection = get_collection()
    total = collection.count()

    if total == 0:
        return []

    records = collection.get(include=["metadatas"])
    sources = {
        metadata.get("source")
        for metadata in records.get("metadatas", [])
        if metadata and metadata.get("source")
    }
    return sorted(sources)


def get_stats() -> dict:
    collection = get_collection()
    return {
        "total_chunks": collection.count(),
        "sources": list_sources(),
    }
