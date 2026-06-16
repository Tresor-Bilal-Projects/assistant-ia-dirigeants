from config import CHUNK_OVERLAP, CHUNK_SIZE
from modules.services.document_parser import extract_text
from modules.services.vectorstore import add_document_chunks
from modules.utils.chunking import chunk_text


def ingest_file(filepath: str, filename: str) -> dict:
    """Pipeline d'ingestion : extraction → chunking → indexation vectorielle."""
    text = extract_text(filepath)
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

    if not chunks:
        raise ValueError("Le document ne contient pas de texte exploitable.")

    add_document_chunks(filename, chunks)

    return {
        "filename": filename,
        "chunks": len(chunks),
        "characters": len(text),
    }
