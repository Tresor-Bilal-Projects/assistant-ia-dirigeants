export let selectedFile = null;

document.addEventListener("DOMContentLoaded", () => {

    const uploadBtn = document.getElementById("upload-btn");
    const filePreview = document.getElementById("file-preview");
    const fileName = document.getElementById("file-name");
    const removeFileBtn = document.getElementById("remove-file");

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf,.txt,.docx";
    fileInput.style.display = "none";

    document.body.appendChild(fileInput);

    // ouvrir explorer
    uploadBtn.addEventListener("click", () => {
        fileInput.click();
    });

    // sélection fichier
    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) return;

        selectedFile = file;

        fileName.textContent = file.name;
        filePreview.style.display = "flex";
    });

    // supprimer fichier
    removeFileBtn.addEventListener("click", () => {
        selectedFile = null;
        fileInput.value = "";
        filePreview.style.display = "none";
    });
});