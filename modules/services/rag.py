import re
import unicodedata

from config import (
    RAG_DISTANCE_THRESHOLD,
    RAG_FOLLOWUP_DISTANCE,
    RAG_FOLLOWUP_TOP_K,
    RAG_SYNTHESIS_DISTANCE,
    RAG_SYNTHESIS_TOP_K,
    TOP_K,
)
from modules.services.vectorstore import get_chunk_by_index, get_document_chunks, get_stats, search


def _normalize(text: str) -> str:
    """Lowercase, drop accents and normalise apostrophes for intent matching."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().replace("’", "'").strip()


# ---------------------------------------------------------------------------
# Non-documentary queries — must NEVER trigger retrieval
# ---------------------------------------------------------------------------

_SMALLTALK_FULL_PATTERNS = [
    re.compile(r"^(bonjour|bonsoir|salut|coucou|hello|hi|hey|yo|hola|re|bonne (journee|soiree))[\s!.,?]*$"),
    re.compile(r"^(merci( beaucoup| bien| infiniment| d'avance)?|thanks?|thank you|je (te|vous) remercie)[\s!.,?]*$"),
    re.compile(r"^(ok|okay|d'accord|parfait|super|nickel|tres bien|au revoir|bye|a bientot)[\s!.,?]*$"),
    re.compile(r"^(ok|okay)\s+(parfait|super|nickel|tres bien|d'accord|c'est bon|impeccable)[\s!.,?]*$"),
]

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
    """True for greetings, thanks and meta-questions about the assistant."""
    normalized = _normalize(query)
    if not normalized:
        return True
    if any(p.match(normalized) for p in _SMALLTALK_FULL_PATTERNS):
        return True
    if any(p.search(normalized) for p in _ASSISTANT_META_PATTERNS):
        return True
    return False


# ---------------------------------------------------------------------------
# Synthesis queries — "list everything", "summarise the document"
# ---------------------------------------------------------------------------

_SYNTHESIS_PATTERNS = [
    re.compile(r"\b(resume[sz]?|recapitule[sz]?|synthetise[sz]?)\b"),
    re.compile(r"\b(liste[sz]?|enumere[sz]?|detaille[sz]?)\b"),
    re.compile(r"\btout(es?)?\s+(ce\s+qui|les?)\s+(est|sont|disponible|propose|liste)\b"),
    re.compile(r"\b(tous\s+les?|toutes\s+les?)\s+(produits?|articles?|prestations?|services?|offres?|options?|accessoires?|tarifs?|prix|references?)\b"),
    re.compile(r"\b(qu[ae]ll?[e]?s?\s+sont\s+(les?|vos?|des?|tous\s+les?|toutes\s+les?))\s+(produits?|articles?|prestations?|services?|offres?|prix|tarifs?)\b"),
    re.compile(r"\b(catalogue|gamme|offre\s+complete)\b"),
    re.compile(r"\bdonne[- ]?(moi)?\s+(tout|l'ensemble|la\s+liste|le\s+catalogue)\b"),
    re.compile(r"\bque\s+(contient|propose[sz]?|offre[sz]?|vend[sz]?|inclut)\b"),
    re.compile(r"\b(qu('est[- ]ce\s+que|est[- ]ce\s+qui)\s+(vous|tu)\s+propose[sz]?)\b"),
    re.compile(r"\b(dis[- ]?moi|montre[- ]?moi|explique[- ]?moi)\s+(tout|la\s+liste|le\s+catalogue|les?\s+(produits?|prestations?|services?|articles?|offres?))\b"),
    re.compile(r"\btout\s+ce\s+(que\s+(vous|tu)\s+(avez?|vendez?|proposez?)|qui\s+est\s+disponible)\b"),
    re.compile(r"\b(qu[ae]ll?[e]?s?\s+(produits?|articles?|prestations?|services?|options?|accessoires?)|qu'est[- ]ce\s+que\s+vous?\s+vendez?)\b"),
    re.compile(r"\b(qu'est[- ]?ce\s+qu'il\s+y\s+a|qu'avez[- ]?vous|qu'as[- ]?tu)\b"),
    re.compile(r"\bpresente[- ]?moi\s+(tout|vos?|tes?|le\s+catalogue|les\s+produit|les\s+prestation)\b"),
]


def _is_synthesis_query(query: str) -> bool:
    normalized = _normalize(query)
    return any(p.search(normalized) for p in _SYNTHESIS_PATTERNS)


# ---------------------------------------------------------------------------
# Follow-up queries — short contextual questions referencing a previous answer
# ---------------------------------------------------------------------------

_FOLLOWUP_PATTERNS = [
    re.compile(r"^(et\s+)?(les?|des?|leur[s]?)\s+(prix|tarif[s]?|cout[s]?|montant[s]?)\s*\??$"),
    re.compile(r"^(et\s+)?(les?|des?)\s+(prestation[s]?|service[s]?|option[s]?|accessoire[s]?)\s*\??$"),
    re.compile(r"^combien\s+([çc]a|cela|ca)\s+(co[uû]te?|vaut|fait)\s*\??$"),
    re.compile(r"^quel(le?s?)?\s+(est\s+l[ea]?|sont\s+les?)\s+(prix|tarif|cout)\s*\??$"),
    re.compile(r"^(et\s+)?(les?|des?)\s+\w+\s*\??$"),
    re.compile(r"^(c'est\s+)?(combien|quel\s+prix|quel\s+tarif)\s*\??$"),
    re.compile(r"^(et\s+)?(pour\s+)?(le\s+montage?|la\s+maintenance|l'audit|la\s+livraison)\s*\??$"),
]


def _is_followup_query(query: str) -> bool:
    normalized = _normalize(query)
    if len(normalized) > 60:
        return False
    return any(p.search(normalized) for p in _FOLLOWUP_PATTERNS)


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def build_rag_context(
    user_id,
    query: str,
    top_k: int = TOP_K,
    document_id: int | None = None,
) -> tuple[str | None, list[str]]:
    """Retrieve relevant chunks scoped strictly to ``user_id``'s documents.

    Behaviour differs by query type:
    - Non-documentary (greeting / meta) → no retrieval at all.
    - Synthesis ("liste tous les produits") → fetches up to RAG_SYNTHESIS_TOP_K
      chunks with a relaxed distance threshold. When ``document_id`` is given,
      retrieves ALL chunks in document order (best for full catalogues).
    - Follow-up ("et les prix ?") → relaxed threshold, moderate top_k.
    - Regular → standard threshold and top_k.
    """
    if _is_non_documentary_query(query):
        return None, []

    is_synthesis = _is_synthesis_query(query)
    is_followup = _is_followup_query(query)

    if is_synthesis:
        if document_id is not None:
            # Full document in reading order — best for catalogue-style synthesis.
            hits = get_document_chunks(user_id, document_id)
            # Safety cap: keep at most RAG_SYNTHESIS_TOP_K chunks to avoid
            # overwhelming the LLM context window.
            hits = hits[:RAG_SYNTHESIS_TOP_K]
        else:
            hits = search(
                user_id,
                query,
                top_k=RAG_SYNTHESIS_TOP_K,
                max_distance=RAG_SYNTHESIS_DISTANCE,
                document_id=None,
            )
            # Sort by document + chunk order for coherent reading.
            hits.sort(key=lambda h: (h.get("document_id") or 0, h.get("chunk_index", 0)))
    elif is_followup:
        hits = search(
            user_id,
            query,
            top_k=RAG_FOLLOWUP_TOP_K,
            max_distance=RAG_FOLLOWUP_DISTANCE,
            document_id=document_id,
        )
    else:
        hits = search(
            user_id,
            query,
            top_k=top_k,
            max_distance=RAG_DISTANCE_THRESHOLD,
            document_id=document_id,
        )
        # Neighbor expansion: for each hit, also include the immediately following
        # chunk (N+1) so that name-in-N / price-in-N+1 splits are covered.
        if hits and document_id is not None:
            present_indices = {h["chunk_index"] for h in hits}
            extra = []
            for h in list(hits):
                next_idx = h["chunk_index"] + 1
                if next_idx not in present_indices:
                    neighbor = get_chunk_by_index(user_id, document_id, next_idx)
                    if neighbor is not None:
                        extra.append(neighbor)
                        present_indices.add(next_idx)
            if extra:
                hits = hits + extra
                hits.sort(key=lambda h: h.get("chunk_index", 0))

    if not hits:
        return None, []

    context_parts = []
    sources = []

    for index, hit in enumerate(hits, start=1):
        source = hit["source"]
        sources.append(source)
        page = hit.get("page") or 0
        page_label = f", p.{page}" if page else ""
        context_parts.append(
            f"[Extrait {index} — source: {source}{page_label}]\n{hit['content']}"
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

RÈGLES ABSOLUES POUR CETTE RÉPONSE (prioritaires sur tout le reste) :
1. Synthétise et utilise DIRECTEMENT les informations du contexte ci-dessous.
2. Ne pose PAS de questions de clarification — le contexte fourni EST la source de vérité.
3. Si la demande est générale (« tout ce qui est disponible », « liste des produits », « résume le document »), liste et détaille TOUT ce qui figure dans les extraits.
4. Cite la source (nom du fichier) pour chaque information utilisée.
5. Si une information demandée est ABSENTE du contexte, dis-le explicitement — ne l'invente jamais.
6. La règle « poser des questions si informations insuffisantes » est SUSPENDUE quand ce contexte documentaire est présent.

{context}
"""


def rag_status(user_id) -> dict:
    stats = get_stats(user_id)
    return {
        "enabled": stats["total_chunks"] > 0,
        "total_chunks": stats["total_chunks"],
        "sources": stats["sources"],
    }
