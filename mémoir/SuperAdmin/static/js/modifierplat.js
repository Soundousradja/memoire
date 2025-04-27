document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const imagePreview = document.getElementById("imagePreview");
    const platForm = document.getElementById("platForm");

    // Preview image change when file is selected
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

    // Handle form submission
    platForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(platForm);
        const csrftoken = getCookie('csrftoken'); // Get CSRF token

        fetch(platForm.action, {
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData,
        })
        .then(response => {
            if (response.ok) {
                // Redirect using category ID from hidden input
                const categorieId = document.getElementById("categorieId").value;
                window.location.href = `/super/categorie_plats/${categorieId}/`;  // Correct redirection
            } else {
                alert("Erreur lors de la mise à jour du plat.");
            }
        })
        .catch(error => {
            console.error("Erreur:", error);
            alert("Une erreur est survenue.");
        });
    });

    // Utility function to get the CSRF token from cookies
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
});
