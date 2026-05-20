export function addMessage(text, type, messages) {

    const wrapper = document.createElement("div");
    wrapper.classList.add("message", type);

    const content = document.createElement("div");
    content.classList.add("message-content");

    if (type === "bot") {
        content.innerHTML = marked.parse(text);
    } else {
        content.textContent = text;
    }

    wrapper.appendChild(content);

    /* COPY BUTTON ONLY FOR BOT */

    if (type === "bot") {

        const actions = document.createElement("div");
        actions.classList.add("message-actions");

        const btn = document.createElement("button");
        btn.classList.add("copy-btn");
        btn.type = "button";
        btn.textContent = "Copier";

        btn.addEventListener("click", async () => {

            try {

                await navigator.clipboard.writeText(
                    content.innerText.trim()
                );

                btn.textContent = "Copié ✔";
                btn.classList.add("copied");

                setTimeout(() => {
                    btn.textContent = "Copier";
                    btn.classList.remove("copied");
                }, 1200);

            } catch (err) {
                console.error(err);
            }
        });

        actions.appendChild(btn);
        wrapper.appendChild(actions);
    }

    messages.appendChild(wrapper);

    scrollToBottom(messages);

    return {
        wrapper,
        content
    };
}

export function setLoadingState(input, button, uploadBtn, state) {

    input.disabled = state;
    button.disabled = state;

    if (uploadBtn) uploadBtn.disabled = state;

    if (!state) input.focus();
}

export function scrollToBottom(messages) {
    messages.scrollTop = messages.scrollHeight;
}

export function createTypingIndicator(messages) {

    const el = document.createElement("div");
    el.classList.add("message", "bot");

    el.textContent = "IA écrit...";

    messages.appendChild(el);
    scrollToBottom(messages);

    return el;
}

export function typeEffect(
    contentElement,
    text,
    input,
    button,
    uploadBtn
) {

    let i = 0;
    let currentText = "";

    function type() {

        if (i < text.length) {

            currentText += text.slice(i, i + 2);

            contentElement.innerHTML =
                marked.parse(currentText);

            i += 2;

            scrollToBottom(
                contentElement.closest("#messages")
            );

            requestAnimationFrame(type);

        } else {

            input.disabled = false;
            button.disabled = false;

            if (uploadBtn) {
                uploadBtn.disabled = false;
            }

            input.focus();
        }
    }

    type();
}