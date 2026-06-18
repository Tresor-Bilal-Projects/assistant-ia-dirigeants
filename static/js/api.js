// Shared API helpers (CSRF-aware).

export function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
}

/**
 * fetch wrapper that attaches the CSRF token on state-changing requests and
 * sets JSON content-type for JSON bodies. Cookies (session) are sent by default.
 */
export async function apiFetch(url, options = {}) {
    const opts = { ...options, headers: { ...(options.headers || {}) } };
    const method = (opts.method || "GET").toUpperCase();

    if (method !== "GET" && method !== "HEAD") {
        opts.headers["X-CSRFToken"] = csrfToken();
        if (opts.body && !(opts.body instanceof FormData) && !opts.headers["Content-Type"]) {
            opts.headers["Content-Type"] = "application/json";
        }
    }

    return fetch(url, opts);
}

// CHAT API — sends the message, the active conversation id, and optionally
// the active document id (to focus RAG retrieval on a specific document).
export async function sendMessageAPI(message, conversationId = null, activeDocumentId = null) {
    try {
        const body = { message, conversation_id: conversationId };
        if (activeDocumentId != null) {
            body.active_document_id = activeDocumentId;
        }

        const res = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken()
            },
            body: JSON.stringify(body)
        });

        return await res.json();

    } catch (err) {
        console.error("Chat API error:", err);
        return null;
    }
}

// UPLOAD API
export async function uploadFileAPI(file) {
    if (!file) return null;

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/upload", {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken() },
            body: formData
        });

        return await res.json();

    } catch (err) {
        console.error("Upload API error:", err);
        return null;
    }
}
