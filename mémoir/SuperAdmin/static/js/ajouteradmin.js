document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("addAdmin").addEventListener("click", function() {
        let name = document.getElementById("adminName").value.trim();
        let phone = document.getElementById("adminPhone").value.trim();
        let fileInput = document.getElementById("fileInput").files[0];
        let restaurant = document.getElementById("restaurantSelect").value; // ✅ récupérer le restaurant choisi

        if (!name || !phone || !fileInput || !restaurant) {
            alert("Tous les champs sont obligatoires !");
            return;
        }

        let formData = new FormData();
        formData.append("name", name);
        formData.append("phone", phone);
        formData.append("image", fileInput);
        formData.append("restaurant", restaurant); // ✅ ajouter au formData

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
                console.log(data.errors); // pour debugger si besoin
            }
        })
        .catch(error => console.error("Erreur:", error));
    });

    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }
});
