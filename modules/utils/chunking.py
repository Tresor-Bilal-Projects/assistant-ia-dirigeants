import re


def _is_section_header(line: str) -> bool:
    """Heuristic: short line that looks like a heading."""
    line = line.strip()
    if not line or len(line) > 80:
        return False
    if line.isupper() and len(line) > 3:
        return True
    if line.endswith(":") and len(line) < 60:
        return True
    words = line.split()
    if 1 <= len(words) <= 6 and all(
        w[0].isupper() for w in words if w and w[0].isalpha()
    ):
        return True
    return False


def _split_paragraphs(text: str) -> list[str]:
    """Split on blank lines; keep non-empty paragraphs."""
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Paragraph-aware chunking with overlap.

    Merges consecutive short paragraphs up to chunk_size, then splits
    oversized paragraphs by sentence or character boundaries. Preserves
    section headers by prepending them to the first chunk of their section.
    """
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""
    current_header = ""

    def flush(buf: str) -> None:
        stripped = buf.strip()
        if stripped:
            chunks.append(stripped)

    def split_large(para: str) -> list[str]:
        """Split a paragraph that exceeds chunk_size."""
        # Try sentence boundaries first.
        sentences = re.split(r"(?<=[.!?])\s+", para)
        parts: list[str] = []
        buf = ""
        for sent in sentences:
            if buf and len(buf) + 1 + len(sent) > chunk_size:
                parts.append(buf.strip())
                tail = buf[-overlap:] if overlap else ""
                buf = (tail + " " + sent).strip() if tail else sent
            else:
                buf = (buf + " " + sent).strip() if buf else sent
        if buf.strip():
            parts.append(buf.strip())
        # If sentences were still too long, fall back to character split.
        result: list[str] = []
        for part in parts:
            while len(part) > chunk_size:
                result.append(part[:chunk_size].strip())
                part = part[chunk_size - overlap:].strip()
            if part:
                result.append(part)
        return result

    for para in paragraphs:
        header_detected = _is_section_header(para)
        if header_detected:
            # Flush the current buffer, then start a new section.
            flush(current)
            current = ""
            current_header = para
            continue

        # Prepend section header to the first chunk of this section.
        effective_para = (current_header + "\n" + para) if current_header else para
        current_header = ""  # consumed

        if not current:
            current = effective_para
        elif len(current) + 1 + len(effective_para) <= chunk_size:
            current = current + "\n" + effective_para
        else:
            flush(current)
            # Overlap: carry the tail of the last chunk.
            tail = current[-overlap:] if overlap else ""
            current = (tail + "\n" + effective_para).strip() if tail else effective_para

        # If current already exceeds chunk_size, split it now.
        if len(current) > chunk_size:
            parts = split_large(current)
            for part in parts[:-1]:
                flush(part)
            current = parts[-1] if parts else ""

    flush(current)
    # Flush any remaining header that had no body paragraph.
    if current_header:
        flush(current_header)

    return chunks


def chunk_pages(
    pages: list[dict], chunk_size: int = 500, overlap: int = 50
) -> list[dict]:
    """Chunk page-by-page, preserving page numbers.

    Args:
        pages: list of {text: str, page: int} dicts from extract_pages().
    Returns:
        list of {text: str, page: int} dicts ready for vectorstore indexing.
    """
    result: list[dict] = []
    for page_data in pages:
        page_num = page_data.get("page", 0)
        for text_chunk in chunk_text(page_data["text"], chunk_size, overlap):
            result.append({"text": text_chunk, "page": page_num})
    return result
