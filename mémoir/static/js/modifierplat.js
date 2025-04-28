document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const imagePreview = document.getElementById("imagePreview");

    fileInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Soumission du formulaire via fetch (AJAX)
    const platForm = document.getElementById("platForm");

    platForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(platForm);

        // CSRF token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        fetch(platForm.action, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url; // 🔥 Utilise la vraie URL
            } else {
                alert("Erreur lors de la mise à jour du plat.");
            }
        })
        .catch(error => {
            console.error("Erreur:", error);
            alert("Une erreur est survenue.");
        });
    });
});