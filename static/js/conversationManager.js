import {
    listConversations,
    getConversation,
    createConversation,
    renameConversation,
    deleteConversation
} from "./storage.js";

let currentConversationId = null;
let conversationsCache = [];

export function getCurrentConversationId() {
    return currentConversationId;
}

export function setCurrentConversation(id) {
    currentConversationId = id;
}

export function initConversationManager(renderConversation) {

    const conversationList = document.getElementById("conversation-list");
    const newChatBtn = document.getElementById("new-chat-btn");
    const searchInput = document.getElementById("search-chat");

    async function openConversation(id) {
        currentConversationId = id;
        const full = await getConversation(id);
        renderConversation(full || { id, title: "", messages: [] });
        renderSidebar();
    }

    function renderSidebar() {
        const query = searchInput?.value?.toLowerCase()?.trim();

        let conversations = conversationsCache;
        if (query) {
            conversations = conversations.filter(
                conversation => (conversation.title || "").toLowerCase().includes(query)
            );
        }

        conversationList.innerHTML = "";

        conversations.forEach(conversation => {

            const item = document.createElement("div");
            item.className = "conversation-item";

            if (conversation.id === currentConversationId) {
                item.classList.add("active");
            }

            const titleSpan = document.createElement("span");
            titleSpan.textContent = conversation.title || "Sans titre";

            const actions = document.createElement("div");
            actions.className = "conversation-actions";
            actions.innerHTML = `
                <button class="chat-menu-btn" type="button">⋯</button>
                <div class="chat-menu">
                    <button class="rename-chat" type="button">Renommer</button>
                    <button class="delete-chat" type="button">Supprimer</button>
                </div>
            `;

            item.appendChild(titleSpan);
            item.appendChild(actions);

            /* OPEN */
            item.addEventListener("click", (e) => {
                if (e.target.closest(".conversation-actions")) return;
                if (e.target.closest(".conv-title-input")) return;
                openConversation(conversation.id);
            });

            const menuBtn = item.querySelector(".chat-menu-btn");
            const menu = item.querySelector(".chat-menu");

            /* MENU TOGGLE */
            menuBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                const isOpen = menu.style.display === "flex";
                document.querySelectorAll(".chat-menu").forEach(m => {
                    m.style.display = "none";
                });
                if (!isOpen) menu.style.display = "flex";
            });

            /* RENAME — inline editing (double-click on title) */
            titleSpan.addEventListener("dblclick", (e) => {
                e.stopPropagation();

                const input = document.createElement("input");
                input.className = "conv-title-input";
                input.value = conversation.title || "";
                titleSpan.replaceWith(input);
                input.focus();
                input.select();

                let committed = false;

                async function commitSave() {
                    if (committed) return;
                    committed = true;
                    const newTitle = input.value.trim();
                    if (newTitle) {
                        await renameConversation(conversation.id, newTitle);
                    }
                    await refreshSidebar();
                }

                function commitCancel() {
                    if (committed) return;
                    committed = true;
                    refreshSidebar();
                }

                input.addEventListener("keydown", (e) => {
                    if (e.key === "Enter") { e.preventDefault(); commitSave(); }
                    if (e.key === "Escape") { e.stopPropagation(); commitCancel(); }
                });
                input.addEventListener("blur", commitSave);
                input.addEventListener("click", (e) => e.stopPropagation());
            });

            /* RENAME BUTTON (menu) — triggers same inline editing */
            item.querySelector(".rename-chat").addEventListener("click", (e) => {
                e.stopPropagation();
                menu.style.display = "none";
                titleSpan.dispatchEvent(new MouseEvent("dblclick", { bubbles: false }));
            });

            /* DELETE — inline confirmation */
            item.querySelector(".delete-chat").addEventListener("click", (e) => {
                e.stopPropagation();
                menu.style.display = "none";

                const confirmDiv = document.createElement("div");
                confirmDiv.style.cssText = "display:flex; gap:6px; align-items:center; flex-shrink:0;";
                confirmDiv.addEventListener("click", (e) => e.stopPropagation());

                const confirmBtn = document.createElement("button");
                confirmBtn.textContent = "Confirmer";
                confirmBtn.type = "button";
                confirmBtn.style.cssText = "font-size:11px; padding:2px 8px; border-radius:4px; border:none; background:rgba(239,68,68,0.15); color:#ef4444; cursor:pointer;";

                const cancelBtn = document.createElement("button");
                cancelBtn.textContent = "Annuler";
                cancelBtn.type = "button";
                cancelBtn.style.cssText = "font-size:11px; padding:2px 8px; border-radius:4px; border:none; background:rgba(100,116,139,0.15); color:#64748b; cursor:pointer;";

                confirmDiv.appendChild(confirmBtn);
                confirmDiv.appendChild(cancelBtn);
                actions.replaceWith(confirmDiv);

                function outsideHandler(e) {
                    if (!confirmDiv.contains(e.target)) {
                        document.removeEventListener("click", outsideHandler);
                        renderSidebar();
                    }
                }

                confirmBtn.addEventListener("click", async () => {
                    document.removeEventListener("click", outsideHandler);
                    await deleteConversation(conversation.id);
                    conversationsCache = await listConversations();
                    if (currentConversationId === conversation.id) {
                        if (conversationsCache.length) {
                            await openConversation(conversationsCache[0].id);
                        } else {
                            const created = await createConversation();
                            conversationsCache = await listConversations();
                            await openConversation(created.id);
                        }
                    } else {
                        renderSidebar();
                    }
                });

                cancelBtn.addEventListener("click", () => {
                    document.removeEventListener("click", outsideHandler);
                    renderSidebar();
                });

                setTimeout(() => {
                    document.addEventListener("click", outsideHandler);
                }, 0);
            });

            conversationList.appendChild(item);
        });
    }

    async function refreshSidebar() {
        conversationsCache = await listConversations();
        renderSidebar();
    }

    /* close menus on outside click */
    document.addEventListener("click", () => {
        document.querySelectorAll(".chat-menu").forEach(menu => {
            menu.style.display = "none";
        });
    });

    searchInput?.addEventListener("input", renderSidebar);

    /* NEW CHAT — FIX 1: skip if current conversation is already a fresh "Nouveau chat" */
    newChatBtn.addEventListener("click", async () => {
        const currentId = getCurrentConversationId();
        if (currentId) {
            const current = conversationsCache.find(c => c.id === currentId);
            if (current && current.title === "Nouveau chat") {
                return;
            }
        }
        const created = await createConversation();
        if (!created) return;
        conversationsCache = await listConversations();
        await openConversation(created.id);
    });

    /* INITIAL LOAD */
    (async () => {
        conversationsCache = await listConversations();
        if (!conversationsCache.length) {
            const created = await createConversation();
            conversationsCache = created ? [created] : [];
        }
        if (conversationsCache.length) {
            await openConversation(conversationsCache[0].id);
        }
    })();

    return {
        refreshSidebar,
        getCurrentConversationId,
        setCurrentConversation
    };
}
