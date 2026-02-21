document.addEventListener('DOMContentLoaded', () => {
    const bar = document.getElementById('bar');
    const menu = document.getElementById('menu');

    bar.addEventListener('click', () => {
        if (menu.classList.contains('-translate-x-full')) {
            menu.classList.remove('-translate-x-full');
        } else {
            menu.classList.add('-translate-x-full');
        }
    });
});

const imageInput = document.getElementById("imageInput");
const previewContainer = document.getElementById("previewContainer");

imageInput.addEventListener("change", function () {

    previewContainer.innerHTML = ""; // Clear old previews

    const files = this.files;

    if (files.length > 10) {
        alert("Maximum 10 images allowed.");
        imageInput.value = "";
        return;
    }

    Array.from(files).forEach(file => {

        if (!file.type.startsWith("image/")) return;

        const reader = new FileReader();

        reader.onload = function (e) {
            const wrapper = document.createElement("div");
            wrapper.classList.add("relative");

            const img = document.createElement("img");
            img.src = e.target.result;
            img.classList.add("w-full", "h-32", "object-cover", "rounded-xl", "shadow");

            wrapper.appendChild(img);
            previewContainer.appendChild(wrapper);
        };

        reader.readAsDataURL(file);
    });
});