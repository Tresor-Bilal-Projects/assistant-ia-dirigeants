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

            /* RENAME */
            item.querySelector(".rename-chat").addEventListener("click", async (e) => {
                e.stopPropagation();
                menu.style.display = "none";
                const newTitle = prompt("Nom de la conversation", conversation.title);
                if (!newTitle || !newTitle.trim()) return;
                await renameConversation(conversation.id, newTitle.trim());
                await refreshSidebar();
            });

            /* DELETE */
            item.querySelector(".delete-chat").addEventListener("click", async (e) => {
                e.stopPropagation();
                menu.style.display = "none";
                if (!confirm("Supprimer cette conversation ?")) return;

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

    /* NEW CHAT */
    newChatBtn.addEventListener("click", async () => {
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
