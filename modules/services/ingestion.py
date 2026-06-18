from config import CHUNK_OVERLAP, CHUNK_SIZE
from modules.services.document_parser import extract_pages
from modules.services.vectorstore import add_document_chunks
from modules.utils.chunking import chunk_pages


def ingest_file(filepath: str, user_id, document_id, source: str) -> dict:
    """Pipeline d'ingestion : extraction → chunking → indexation vectorielle.

    L'indexation est isolée par utilisateur : les chunks sont écrits dans la
    collection Chroma dédiée à ``user_id`` avec les métadonnées d'appartenance
    (dont le numéro de page pour les PDFs).
    """
    pages = extract_pages(filepath)
    chunks = chunk_pages(pages, CHUNK_SIZE, CHUNK_OVERLAP)

    if not chunks:
        raise ValueError("Le document ne contient pas de texte exploitable.")

    total_characters = sum(len(p["text"]) for p in pages)
    add_document_chunks(user_id, document_id, source, chunks)

    return {
        "filename": source,
        "chunks": len(chunks),
        "characters": total_characters,
    }
