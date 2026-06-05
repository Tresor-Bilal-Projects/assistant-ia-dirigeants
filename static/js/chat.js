import { sendMessageAPI, uploadFileAPI } from "./api.js";

import {
    addMessage,
    setLoadingState,
    typeEffect
} from "./ui.js";

import { resetSelectedFile, selectedFile } from "./upload.js";

document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("user-input");
    const button = document.getElementById("send-btn");
    const uploadBtn = document.getElementById("upload-btn");
    const messages = document.getElementById("messages");

    const MIN_HEIGHT = 46;
    const MAX_HEIGHT = 120;

    /* TEXTAREA AUTO RESIZE */

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

    /* init height */

    autoResize();

    /* SEND MESSAGE */

    async function sendMessage() {

        const text = input.value.trim();

        if (!text && !selectedFile) return;

        /* USER MESSAGE */

        if (text) {
            addMessage(text, "user", messages);
        }

        /* RESET INPUT */

        input.value = "";

        input.style.height = MIN_HEIGHT + "px";

        autoResize();

        /* BOT PLACEHOLDER */

        const loading = addMessage("", "bot", messages);

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
                fileData = await uploadFileAPI(selectedFile);

                if (fileData?.error) {
                    throw new Error(fileData.error);
                }

                resetSelectedFile();
            }

            /* API CALL */

            const response = await sendMessageAPI(
                text,
                fileData
            );

            /* SAFE RESPONSE */

            let safeResponse =
                response?.answer ||
                response?.response ||
                response?.message ||
                response?.result ||
                "Erreur : réponse vide";

            if (response?.rag_used && response?.sources?.length) {
                safeResponse += `\n\n---\n**Sources RAG :** ${response.sources.join(", ")}`;
            }

            if (fileData?.message) {
                safeResponse = `📎 ${fileData.message}\n\n${safeResponse}`;
            }

            /* TYPE EFFECT */

            typeEffect(
                loading.content,
                String(safeResponse),
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

            setLoadingState(
                input,
                button,
                uploadBtn,
                false
            );
        }
    }

    /* BUTTON CLICK */

    button.addEventListener("click", sendMessage);

    /* ENTER / SHIFT+ENTER */

    input.addEventListener("keydown", (e) => {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            sendMessage();
        }
    });
});