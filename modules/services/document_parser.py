import os


def extract_text(filepath: str) -> str:
    """Extrait le texte brut d'un PDF, TXT ou DOCX."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as handle:
            return handle.read()

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(filepath)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    if ext == ".docx":
        from docx import Document

        document = Document(filepath)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError(f"Format non supporté : {ext}")
