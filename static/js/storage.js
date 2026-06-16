// Server-backed conversation store. The backend (per-user, in DB) is the single
// source of truth; localStorage is no longer used for durable history.
import { apiFetch } from "./api.js";

export async function listConversations() {
    const res = await apiFetch("/api/conversations");
    if (!res.ok) return [];
    return await res.json();
}

export async function getConversation(id) {
    const res = await apiFetch(`/api/conversations/${id}`);
    if (!res.ok) return null;
    return await res.json();
}

export async function createConversation() {
    const res = await apiFetch("/api/conversations", { method: "POST" });
    if (!res.ok) return null;
    return await res.json();
}

export async function renameConversation(id, title) {
    const res = await apiFetch(`/api/conversations/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ title })
    });
    return res.ok;
}

export async function deleteConversation(id) {
    const res = await apiFetch(`/api/conversations/${id}`, { method: "DELETE" });
    return res.ok;
}
