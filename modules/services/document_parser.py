import os
import re


# ---------------------------------------------------------------------------
# Kerning / spaced-letter cleanup
# ---------------------------------------------------------------------------

_SPACED_LETTER_RE = re.compile(r"([A-Za-zÀ-ÿ]) (?=[A-Za-zÀ-ÿ])")


def _single_char_ratio(text: str) -> float:
    """Fraction of whitespace-separated tokens that are single alphabetic chars."""
    tokens = text.split()
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if len(t) == 1 and t.isalpha()) / len(tokens)


def _clean_spaced_letters(text: str, threshold: float = 0.30) -> str:
    """Remove inter-letter spaces produced by PDF kerning on some design tools.

    Only applied when more than *threshold* of the tokens are single alphabetic
    characters — a reliable signal that every letter was extracted separately.
    Safe on normal text (French/English prose never exceeds ~5%).
    """
    if _single_char_ratio(text) > threshold:
        return _SPACED_LETTER_RE.sub(r"\1", text)
    return text


# ---------------------------------------------------------------------------


def extract_pages(filepath: str) -> list[dict]:
    """Extrait le texte par page/section. Retourne une liste de {text, page}.

    Pour les PDFs, chaque entrée correspond à une page (page=1-based).
    Pour TXT/DOCX, une seule entrée avec page=0 (non paginé).
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as handle:
            return [{"text": _clean_spaced_letters(handle.read()), "page": 0}]

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(filepath)
        return [
            {"text": _clean_spaced_letters(page.extract_text() or ""), "page": i + 1}
            for i, page in enumerate(reader.pages)
        ]

    if ext == ".docx":
        from docx import Document

        document = Document(filepath)
        return [
            {
                "text": _clean_spaced_letters(
                    "\n".join(p.text for p in document.paragraphs)
                ),
                "page": 0,
            }
        ]

    raise ValueError(f"Format non supporté : {ext}")


def extract_text(filepath: str) -> str:
    """Rétrocompatibilité : retourne le texte brut concaténé."""
    return "\n\n".join(p["text"] for p in extract_pages(filepath))
