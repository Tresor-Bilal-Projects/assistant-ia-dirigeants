import re
import unicodedata

from config import RAG_DISTANCE_THRESHOLD
from modules.services.vectorstore import get_stats, search


def _normalize(text: str) -> str:
    """Lowercase, drop accents and normalise apostrophes for intent matching."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().replace("’", "'").strip()


# Whole-message greetings / acknowledgements: no documentary intent at all.
_SMALLTALK_FULL_PATTERNS = [
    re.compile(r"^(bonjour|bonsoir|salut|coucou|hello|hi|hey|yo|hola|re|bonne (journee|soiree))[\s!.,?]*$"),
    re.compile(r"^(merci( beaucoup| bien| infiniment| d'avance)?|thanks?|thank you|je (te|vous) remercie)[\s!.,?]*$"),
    re.compile(r"^(ok|okay|d'accord|parfait|super|nickel|tres bien|au revoir|bye|a bientot)[\s!.,?]*$"),
]

# Meta-questions about the assistant itself (matched anywhere in the message).
_ASSISTANT_META_PATTERNS = [
    re.compile(r"\bqui (es[- ]?tu|etes[- ]?vous)\b"),
    re.compile(r"\b(ton|ta|votre|vos) (role|but|objectif|utilite|fonction|mission|capacites|competences)\b"),
    re.compile(r"\bque (peux[- ]?tu|pouvez[- ]?vous|sais[- ]?tu) faire\b"),
    re.compile(r"\b(a quoi|pourquoi) sers[- ]?tu\b"),
    re.compile(r"\bpresente[- ]?toi\b"),
    re.compile(r"\bcomment (vas[- ]?tu|tu vas|ca va|fonctionnes[- ]?tu|tu fonctionnes)\b"),
    re.compile(r"\bca va\b"),
    re.compile(r"\bresume ton role\b"),
]


def _is_non_documentary_query(query: str) -> bool:
    """True for greetings, thanks and meta-questions about the assistant.

    These must never trigger document retrieval: in a small corpus their
    embedding can land close to unrelated chunks, so distance alone is not
    enough to reject them.
    """
    normalized = _normalize(query)
    if not normalized:
        return True
    if any(pattern.match(normalized) for pattern in _SMALLTALK_FULL_PATTERNS):
        return True
    if any(pattern.search(normalized) for pattern in _ASSISTANT_META_PATTERNS):
        return True
    return False


def build_rag_context(query: str, top_k: int = 4) -> tuple[str | None, list[str]]:
    """Récupère les passages les plus pertinents pour enrichir le prompt.

    Retourne ``(None, [])`` — RAG désactivé — lorsque la requête est non
    documentaire (salutation / remerciement / question méta sur l'assistant)
    ou lorsqu'aucun extrait n'est assez proche pour être pertinent
    (distance <= ``RAG_DISTANCE_THRESHOLD``).
    """
    if _is_non_documentary_query(query):
        return None, []

    hits = search(query, top_k=top_k, max_distance=RAG_DISTANCE_THRESHOLD)

    if not hits:
        return None, []

    context_parts = []
    sources = []

    for index, hit in enumerate(hits, start=1):
        source = hit["source"]
        sources.append(source)
        context_parts.append(
            f"[Extrait {index} — source: {source}]\n{hit['content']}"
        )

    unique_sources = list(dict.fromkeys(sources))
    return "\n\n".join(context_parts), unique_sources


def build_system_prompt(base_prompt: str, context: str | None) -> str:
    if not context:
        return base_prompt

    return f"""{base_prompt}

=========================
CONTEXTE DOCUMENTAIRE (RAG)
=========================

Tu disposes d'extraits issus de documents internes de l'entreprise.
Utilise-les pour répondre de façon précise et orientée décision.
Cite la source (nom du fichier) quand tu t'appuies sur un extrait.
Si l'information demandée n'est pas dans le contexte, dis-le clairement au lieu d'inventer.

{context}
"""


def rag_status() -> dict:
    stats = get_stats()
    return {
        "enabled": stats["total_chunks"] > 0,
        "total_chunks": stats["total_chunks"],
        "sources": stats["sources"],
    }
