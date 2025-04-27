document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("addAdmin").addEventListener("click", function() {
        let name = document.getElementById("adminName").value.trim();
        let phone = document.getElementById("adminPhone").value.trim();
        let fileInput = document.getElementById("fileInput").files[0];

        if (!name || !phone || !fileInput) {
            alert("Tous les champs sont obligatoires !");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("phone", phone);
        formData.append("image", fileInput);

        fetch("/super/ajouter_admin/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Admin ajouté avec succès !");
                window.location.href = "/super/gestion_admin/";
            } else {
                alert("Erreur lors de l'ajout !");
            }
        })
        .catch(error => console.error("Erreur:", error));
    });

    // Fonction pour récupérer le token CSRF
    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }
});
