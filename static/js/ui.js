export function addMessage(text, type, messages) {

    const wrapper = document.createElement("div");
    wrapper.classList.add("message", type);

    const content = document.createElement("div");
    content.classList.add("message-content");

    if (type === "bot") {

        const html = marked.parse(text || "");
        content.innerHTML = html;

        // Fix UI code blocks + copy per block
        enhanceCodeBlocks(content);

    } else {
        content.textContent = text;
    }

    wrapper.appendChild(content);

    /* COPY BUTTON GLOBAL (BOT ONLY) */

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
                    extractCleanText(content)
                );

                btn.textContent = "Copié ✔";
                btn.classList.add("copied");

                setTimeout(() => {
                    btn.textContent = "Copier";
                    btn.classList.remove("copied");
                }, 1200);

            } catch (err) {
                console.error("Copy error:", err);
            }
        });

        actions.appendChild(btn);
        wrapper.appendChild(actions);
    }

    messages.appendChild(wrapper);

    scrollToBottom(messages);

    return { wrapper, content };
}

/* LOADING STATE */

export function setLoadingState(input, button, uploadBtn, state) {

    input.disabled = state;
    button.disabled = state;

    if (uploadBtn) uploadBtn.disabled = state;

    if (!state) input.focus();
}

/* SCROLL */

export function scrollToBottom(messages) {
    messages.scrollTop = messages.scrollHeight;
}

/* TYPING INDICATOR */

export function createTypingIndicator(messages) {

    const el = document.createElement("div");
    el.classList.add("message", "bot");

    el.textContent = "IA écrit...";

    messages.appendChild(el);
    scrollToBottom(messages);

    return el;
}

/* TYPE EFFECT (FIXED + SAFE)*/

export function typeEffect(contentElement, text, input, button, uploadBtn) {

    let i = 0;
    let currentText = "";

    function type() {

        if (i < text.length) {

            currentText += text.slice(i, i + 2);

            contentElement.innerHTML = marked.parse(currentText || "");

            // re-apply code block enhancements
            enhanceCodeBlocks(contentElement);

            i += 2;

            scrollToBottom(contentElement.closest("#messages"));

            requestAnimationFrame(type);

        } else {

            input.disabled = false;
            button.disabled = false;

            if (uploadBtn) uploadBtn.disabled = false;

            input.focus();
        }
    }

    type();
}

/* CODE BLOCK ENHANCER (CHATGPT STYLE) */

function enhanceCodeBlocks(container) {

    const blocks = container.querySelectorAll("pre");

    blocks.forEach((pre) => {

        // avoid double wrapping
        if (pre.parentElement?.classList.contains("code-wrapper")) return;

        const wrapper = document.createElement("div");
        wrapper.classList.add("code-wrapper");

        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        const btn = document.createElement("button");
        btn.classList.add("code-copy-btn");
        btn.textContent = "Copy";

        btn.addEventListener("click", async () => {

            try {
                await navigator.clipboard.writeText(pre.innerText);

                btn.textContent = "Copied";

                setTimeout(() => {
                    btn.textContent = "Copy";
                }, 1200);

            } catch (err) {
                console.error("Code copy error:", err);
            }
        });

        wrapper.appendChild(btn);
    });
}

/* CLEAN TEXT FOR GLOBAL COPY */

function extractCleanText(content) {

    const clone = content.cloneNode(true);

    clone.querySelectorAll("button").forEach(btn => btn.remove());

    return clone.innerText.trim();
}