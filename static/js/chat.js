import { sendMessageAPI, uploadFileAPI } from "./api.js";

import {
    addMessage,
    setLoadingState,
    typeEffect
} from "./ui.js";

import { selectedFile } from "./upload.js";

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

    /* RENDER CONVERSATION */
    function renderConversation(conversation) {

        messages.innerHTML = "";

        if (!conversation) return;

        conversation.messages.forEach(msg => {

            addMessage(
                msg.content,
                msg.role === "user"
                    ? "user"
                    : "bot",
                messages
            );
        });

        messages.scrollTop =
            messages.scrollHeight;
    }

    /* INIT CONVERSATION MANAGER */
    manager = initConversationManager(
        renderConversation
    );

    /* TEXTAREA AUTO RESIZE */
    function autoResize() {

        input.style.height =
            MIN_HEIGHT + "px";

        const newHeight = Math.min(
            input.scrollHeight,
            MAX_HEIGHT
        );

        input.style.height =
            newHeight + "px";

        input.style.overflowY =
            input.scrollHeight > MAX_HEIGHT
                ? "auto"
                : "hidden";
    }

    input.addEventListener(
        "input",
        autoResize
    );

    autoResize();

    /* SEND MESSAGE */

    async function sendMessage() {

        const text =
            input.value.trim();

        if (!text && !selectedFile) {
            return;
        }

        /* USER MESSAGE */
        if (text) {

            addMessage(
                text,
                "user",
                messages
            );

            addMessageToConversation(
                "user",
                text
            );

            manager.refreshSidebar();
        }

        /* RESET INPUT */
        input.value = "";

        input.style.height =
            MIN_HEIGHT + "px";

        autoResize();

        /* BOT PLACEHOLDER */
        const loading =
            addMessage(
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

            /* FILE UPLOAD */
            if (selectedFile) {

                fileData =
                    await uploadFileAPI(
                        selectedFile
                    );
            }

            /* API CALL */
            const response =
                await sendMessageAPI(
                    text,
                    fileData
                );

            /* SAFE RESPONSE */
            const safeResponse =
                response?.answer ||
                response?.response ||
                response?.message ||
                response?.result ||
                response ||
                "Erreur : réponse vide";

            const botText =
                String(safeResponse);

            /* SAVE BOT MESSAGE */
            addMessageToConversation(
                "assistant",
                botText
            );

            manager.refreshSidebar();

            /* TYPE EFFECT */
            typeEffect(
                loading.content,
                botText,
                input,
                button,
                uploadBtn
            );

        } catch (err) {

            console.error(err);

            loading.content.innerHTML = `
                <p style="color:red;">
                    Une erreur est survenue.
                </p>
            `;

            addMessageToConversation(
                "assistant",
                "Une erreur est survenue."
            );

            setLoadingState(
                input,
                button,
                uploadBtn,
                false
            );
        }
    }

    /* BUTTON CLICK */
    button.addEventListener(
        "click",
        sendMessage
    );

    /* ENTER / SHIFT+ENTER */

    input.addEventListener(
        "keydown",
        (e) => {

            if (
                e.key === "Enter" &&
                !e.shiftKey
            ) {

                e.preventDefault();

                sendMessage();
            }
        }
    );
});