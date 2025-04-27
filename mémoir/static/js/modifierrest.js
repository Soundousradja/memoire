console.log("modifierrest.js est bien chargé !");

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("fileInput");
    const imagePreview = document.getElementById("imagePreview");
    const form = document.getElementById("restaurantForm");

    // ✅ Aperçu de l'image avant téléchargement
    fileInput.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = "block";
            };
            reader.readAsDataURL(file);
        }
    });

    // ✅ Soumission du formulaire
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Empêche le rechargement de la page

        const formData = new FormData(form);
        formData.append("csrfmiddlewaretoken", getCSRFToken()); // Ajoute le token CSRF

        fetch(window.location.pathname, {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Restaurant mis à jour !");
                window.location.href = "/super/restaurants/"; // Redirection après mise à jour
            } else {
                alert("Erreur lors de la mise à jour.");
            }
        })
        .catch(error => console.error("Erreur:", error));
    });

    // ✅ Fonction pour récupérer le token CSRF
    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }
});
