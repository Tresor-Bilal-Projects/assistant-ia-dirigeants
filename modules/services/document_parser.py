import os


def extract_pages(filepath: str) -> list[dict]:
    """Extrait le texte par page/section. Retourne une liste de {text, page}.

    Pour les PDFs, chaque entrée correspond à une page (page=1-based).
    Pour TXT/DOCX, une seule entrée avec page=0 (non paginé).
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as handle:
            return [{"text": handle.read(), "page": 0}]

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(filepath)
        return [
            {"text": (page.extract_text() or ""), "page": i + 1}
            for i, page in enumerate(reader.pages)
        ]

    if ext == ".docx":
        from docx import Document

        document = Document(filepath)
        return [{"text": "\n".join(p.text for p in document.paragraphs), "page": 0}]

    raise ValueError(f"Format non supporté : {ext}")


def extract_text(filepath: str) -> str:
    """Rétrocompatibilité : retourne le texte brut concaténé."""
    return "\n\n".join(p["text"] for p in extract_pages(filepath))
