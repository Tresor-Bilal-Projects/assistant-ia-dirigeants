export function addMessage(text, type, messages) {

    const wrapper = document.createElement("div");
    wrapper.classList.add("message", type);

    const content = document.createElement("div");
    content.classList.add("message-content");

    content.innerHTML = marked.parse(text);

    wrapper.appendChild(content);

    if (type === "bot") {

        const actions = document.createElement("div");
        actions.classList.add("message-actions");

        const btn = document.createElement("button");
        btn.classList.add("copy-btn");
        btn.type = "button";
        btn.textContent = "Copier";

        btn.addEventListener("click", async () => {

            await navigator.clipboard.writeText(content.innerText);

            btn.textContent = "Copié ✔";

            setTimeout(() => {
                btn.textContent = "Copier";
            }, 1200);
        });

        actions.appendChild(btn);
        wrapper.appendChild(actions);
    }

    messages.appendChild(wrapper);
    scrollToBottom(messages);

    return wrapper;
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

export function typeEffect(element, text, input, button, uploadBtn) {

    let i = 0;
    let currentText = "";

    element.innerHTML = "";

    function type() {

        if (i < text.length) {

            currentText += text.slice(i, i + 2); // plus fluide que 3

            element.innerHTML = marked.parse(currentText);

            i += 2;

            scrollToBottom(element.parentElement);

            setTimeout(type, 8);

        } else {

            input.disabled = false;
            button.disabled = false;
            if (uploadBtn) uploadBtn.disabled = false;

            input.focus();
        }
    }

    type();
}