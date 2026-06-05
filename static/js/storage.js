const STORAGE_KEY = "assistant_conversations";

export function getConversations() {

    try {

        return JSON.parse(
            localStorage.getItem(
                STORAGE_KEY
            )
        ) || [];

    } catch {

        return [];
    }
}

export function saveConversations(
    conversations
) {

    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(
            conversations
        )
    );
}

export function getConversation(
    id
) {

    return getConversations().find(
        conversation =>
            conversation.id === id
    );
}

export function createConversation() {

    const conversations =
        getConversations();

    const existingEmpty =
        conversations.find(
            conversation =>
                !conversation.messages ||
                conversation.messages
                    .length === 0
        );

    if (existingEmpty) {
        return existingEmpty;
    }

    const conversation = {

        id: crypto.randomUUID(),

        title: "Nouveau chat",

        createdAt: Date.now(),

        messages: []
    };

    conversations.unshift(
        conversation
    );

    saveConversations(
        conversations
    );

    return conversation;
}

export function updateConversation(
    id,
    updater
) {

    const conversations =
        getConversations();

    const index =
        conversations.findIndex(
            conversation =>
                conversation.id === id
        );

    if (index === -1) {
        return;
    }

    updater(
        conversations[index]
    );

    saveConversations(
        conversations
    );
}

export function deleteConversation(
    id
) {

    const conversations =
        getConversations().filter(
            conversation =>
                conversation.id !== id
        );

    saveConversations(
        conversations
    );
}