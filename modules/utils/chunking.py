def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Découpe un texte en fragments avec chevauchement pour le RAG."""
    normalized = " ".join(text.split())

    if not normalized.strip():
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    chunks = []
    start = 0

    while start < len(normalized):
        end = start + chunk_size
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks
