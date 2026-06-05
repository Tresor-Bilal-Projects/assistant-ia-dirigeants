export let selectedFile = null;

let fileInput = null;
let filePreview = null;

export function resetSelectedFile() {
    selectedFile = null;

    if (fileInput) {
        fileInput.value = "";
    }

    if (filePreview) {
        filePreview.style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const uploadBtn = document.getElementById("upload-btn");
    filePreview = document.getElementById("file-preview");
    const fileName = document.getElementById("file-name");
    const removeFileBtn = document.getElementById("remove-file");

    fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf,.txt,.docx";
    fileInput.style.display = "none";

    document.body.appendChild(fileInput);

    uploadBtn.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) return;

        selectedFile = file;
        fileName.textContent = file.name;
        filePreview.style.display = "flex";
    });

    removeFileBtn.addEventListener("click", () => {
        resetSelectedFile();
    });
});
