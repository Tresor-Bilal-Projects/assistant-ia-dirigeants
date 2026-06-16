import {
    getConversations,
    createConversation,
    updateConversation,
    deleteConversation
} from "./storage.js";

let currentConversationId = null;

export function getCurrentConversationId() {
    return currentConversationId;
}

export function setCurrentConversation(id) {
    currentConversationId = id;
}

export function addMessageToConversation(
    role,
    content
) {

    if (!currentConversationId) return;

    updateConversation(
        currentConversationId,
        (conversation) => {

            conversation.messages.push({
                role,
                content,
                createdAt: Date.now()
            });

            if (
                conversation.title ===
                    "Nouveau chat" &&
                role === "user"
            ) {

                conversation.title =
                    content.length > 40
                        ? content.substring(
                              0,
                              40
                          ) + "..."
                        : content;
            }
        }
    );
}

export function initConversationManager(
    renderConversation
) {

    const conversationList =
        document.getElementById(
            "conversation-list"
        );

    const newChatBtn =
        document.getElementById(
            "new-chat-btn"
        );

    const searchInput =
        document.getElementById(
            "search-chat"
        );

    function renderSidebar() {

        let conversations =
            getConversations();

        const query =
            searchInput?.value
                ?.toLowerCase()
                ?.trim();

        if (query) {

            conversations =
                conversations.filter(
                    conversation =>
                        conversation.title
                            .toLowerCase()
                            .includes(query)
                );
        }

        conversationList.innerHTML =
            "";

        conversations.forEach(
            conversation => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "conversation-item";

                if (
                    conversation.id ===
                    currentConversationId
                ) {
                    item.classList.add(
                        "active"
                    );
                }

                item.innerHTML = `
                    <span>
                        ${conversation.title}
                    </span>

                    <div class="conversation-actions">

                        <button
                            class="chat-menu-btn"
                            type="button"
                        >
                            ⋯
                        </button>

                        <div class="chat-menu">

                            <button
                                class="rename-chat"
                                type="button"
                            >
                                Renommer
                            </button>

                            <button
                                class="delete-chat"
                                type="button"
                            >
                                Supprimer
                            </button>

                        </div>

                    </div>
                `;

                /* OPEN CHAT */

                item.addEventListener(
                    "click",
                    (e) => {

                        if (
                            e.target.closest(
                                ".conversation-actions"
                            )
                        ) {
                            return;
                        }

                        currentConversationId =
                            conversation.id;

                        renderSidebar();

                        renderConversation(
                            conversation
                        );
                    }
                );

                /* MENU */
                const menuBtn =
                    item.querySelector(
                        ".chat-menu-btn"
                    );

                const menu =
                    item.querySelector(
                        ".chat-menu"
                    );

                menuBtn.addEventListener(
                    "click",
                    (e) => {

                        e.stopPropagation();

                        const isOpen =
                            menu.style.display ===
                            "flex";

                        document
                            .querySelectorAll(
                                ".chat-menu"
                            )
                            .forEach(
                                m => {
                                    m.style.display =
                                        "none";
                                }
                            );

                        if (!isOpen) {
                            menu.style.display =
                                "flex";
                        }
                    }
                );

                /* RENAME */
                item.querySelector(
                    ".rename-chat"
                ).addEventListener(
                    "click",
                    (e) => {

                        e.stopPropagation();

                        menu.style.display =
                            "none";

                        const newTitle =
                            prompt(
                                "Nom de la conversation",
                                conversation.title
                            );

                        if (
                            !newTitle ||
                            !newTitle.trim()
                        ) {
                            return;
                        }

                        updateConversation(
                            conversation.id,
                            current => {

                                current.title =
                                    newTitle.trim();
                            }
                        );

                        renderSidebar();
                    }
                );

                /* DELETE */
                item.querySelector(
                    ".delete-chat"
                ).addEventListener(
                    "click",
                    (e) => {

                        e.stopPropagation();

                        menu.style.display =
                            "none";

                        if (
                            !confirm(
                                "Supprimer cette conversation ?"
                            )
                        ) {
                            return;
                        }

                        deleteConversation(
                            conversation.id
                        );

                        const remaining =
                            getConversations();

                        if (
                            currentConversationId ===
                            conversation.id
                        ) {

                            if (
                                remaining.length
                            ) {

                                currentConversationId =
                                    remaining[0]
                                        .id;

                                renderConversation(
                                    remaining[0]
                                );

                            } else {

                                const newConv =
                                    createConversation();

                                currentConversationId =
                                    newConv.id;

                                renderConversation(
                                    newConv
                                );
                            }
                        }

                        renderSidebar();
                    }
                );

                conversationList.appendChild(
                    item
                );
            }
        );
    }

    document.addEventListener(
        "click",
        () => {

            document
                .querySelectorAll(
                    ".chat-menu"
                )
                .forEach(
                    menu => {

                        menu.style.display =
                            "none";
                    }
                );
        }
    );

    searchInput?.addEventListener(
        "input",
        renderSidebar
    );

    newChatBtn.addEventListener(
        "click",
        () => {

            const conversations =
                getConversations();

            const emptyConversation =
                conversations.find(
                    conversation =>
                        !conversation.messages ||
                        conversation.messages
                            .length === 0
                );

            if (emptyConversation) {

                currentConversationId =
                    emptyConversation.id;

                renderConversation(
                    emptyConversation
                );

                renderSidebar();

                return;
            }

            const conversation =
                createConversation();

            currentConversationId =
                conversation.id;

            renderConversation(
                conversation
            );

            renderSidebar();
        }
    );

    let conversations =
        getConversations();

    if (!conversations.length) {

        const first =
            createConversation();

        conversations = [first];
    }

    currentConversationId =
        conversations[0].id;

    renderConversation(
        conversations[0]
    );

    renderSidebar();

    return {
        refreshSidebar:
            renderSidebar
    };
}