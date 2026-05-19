// CHAT API
export async function sendMessageAPI(message, file = null) {
    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message,
                file
            })
        });

        return await res.json();

    } catch (err) {
        console.error("Chat API error:", err);
        return null;
    }
}

// UPLOAD API
export async function uploadFileAPI(file) {
    if (!file) return null;

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        return await res.json();

    } catch (err) {
        console.error("Upload API error:", err);
        return null;
    }
}