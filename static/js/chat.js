import { sendMessageAPI, uploadFileAPI } from "./api.js";

import {
addMessage,
setLoadingState,
typeEffect
} from "./ui.js";

import {
resetSelectedFile,
selectedFile
} from "./upload.js";

import {
initConversationManager,
addMessageToConversation
} from "./conversationManager.js";

document.addEventListener("DOMContentLoaded", () => {

const input = document.getElementById("user-input");
const button = document.getElementById("send-btn");
const uploadBtn = document.getElementById("upload-btn");
const messages = document.getElementById("messages");

const MIN_HEIGHT = 46;
const MAX_HEIGHT = 120;

let manager = null;

function renderConversation(conversation) {
    messages.innerHTML = "";

    if (!conversation) return;

    conversation.messages.forEach((msg) => {
        addMessage(
            msg.content,
            msg.role === "user" ? "user" : "bot",
            messages
        );
    });

    messages.scrollTop = messages.scrollHeight;
}

manager = initConversationManager(renderConversation);

function autoResize() {
    input.style.height = MIN_HEIGHT + "px";

    const newHeight = Math.min(
        input.scrollHeight,
        MAX_HEIGHT
    );

    input.style.height = newHeight + "px";

    input.style.overflowY =
        input.scrollHeight > MAX_HEIGHT
            ? "auto"
            : "hidden";
}

input.addEventListener("input", autoResize);
autoResize();

async function sendMessage() {
    const text = input.value.trim();

    if (!text && !selectedFile) {
        return;
    }

    if (text) {
        addMessage(text, "user", messages);

        addMessageToConversation(
            "user",
            text
        );

        manager.refreshSidebar();
    }

    input.value = "";
    input.style.height = MIN_HEIGHT + "px";
    autoResize();

    const loading = addMessage(
        "",
        "bot",
        messages
    );

    setLoadingState(
        input,
        button,
        uploadBtn,
        true
    );

    try {
        let fileData = null;

        if (selectedFile) {
            fileData = await uploadFileAPI(selectedFile);

            if (fileData?.error) {
                throw new Error(fileData.error);
            }

            resetSelectedFile();
        }

        let botText = "";

        if (!text && fileData?.message) {
            botText = `📎 ${fileData.message}`;
        } else {
            const response = await sendMessageAPI(
                text,
                fileData
            );

            const safeResponse =
                response?.answer ||
                response?.response ||
                response?.message ||
                response?.result ||
                "Erreur : réponse vide";

            botText = String(safeResponse);

            if (
                response?.rag_used &&
                response?.sources?.length
            ) {
                botText +=
                    `\n\n---\n**Sources RAG :** ` +
                    response.sources.join(", ");
            }

            if (fileData?.message) {
                botText =
                    `📎 ${fileData.message}\n\n${botText}`;
            }
        }

        addMessageToConversation(
            "assistant",
            botText
        );

        manager.refreshSidebar();

        typeEffect(
            loading.content,
            botText,
            input,
            button,
            uploadBtn
        );

    } catch (err) {
        console.error(err);

        const errorMessage =
            err?.message ||
            "Une erreur est survenue.";

        loading.content.innerHTML = `
            <p style="color:red;">
                ${errorMessage}
            </p>
        `;

        addMessageToConversation(
            "assistant",
            errorMessage
        );

        manager.refreshSidebar();

        setLoadingState(
            input,
            button,
            uploadBtn,
            false
        );
    }
}

button.addEventListener(
    "click",
    sendMessage
);

input.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }
    }
);

});
