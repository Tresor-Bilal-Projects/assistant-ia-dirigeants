from modules.services.vectorstore import get_stats, search


def build_rag_context(query: str, top_k: int = 4) -> tuple[str | None, list[str]]:
    """Récupère les passages les plus pertinents pour enrichir le prompt."""
    hits = search(query, top_k=top_k)

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
