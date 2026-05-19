import { sendMessageAPI, uploadFileAPI } from "./api.js";
import {
    addMessage,
    setLoadingState,
    typeEffect,
    createTypingIndicator
} from "./ui.js";

import { selectedFile } from "./upload.js";

document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("user-input");
    const button = document.getElementById("send-btn");
    const uploadBtn = document.getElementById("upload-btn");
    const messages = document.getElementById("messages");

    const MIN_HEIGHT = 46;
    const MAX_HEIGHT = 120;

    function autoResize() {

        input.style.height = "auto";

        const scrollHeight = input.scrollHeight;

        const newHeight = Math.min(Math.max(scrollHeight, MIN_HEIGHT), MAX_HEIGHT);

        input.style.height = newHeight + "px";
    }

    input.addEventListener("input", autoResize);

    async function sendMessage() {

        const text = input.value.trim();

        if (!text && !selectedFile) return;

        if (text) {
            addMessage(text, "user", messages);
        }

        input.value = "";
        input.style.height = MIN_HEIGHT + "px";

        const loadingMsg = createTypingIndicator(messages);

        setLoadingState(input, button, uploadBtn, true);

        let fileData = null;

        if (selectedFile) {
            fileData = await uploadFileAPI(selectedFile);
        }

        const response = await sendMessageAPI(text, fileData);

        const safeResponse =
            response?.answer ||
            response?.response ||
            response?.message ||
            response?.result ||
            response ||
            "Erreur : réponse vide";

        typeEffect(
            loadingMsg,
            String(safeResponse),
            input,
            button,
            uploadBtn
        );
    }

    button.addEventListener("click", sendMessage);

    input.addEventListener("keydown", (e) => {

        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});