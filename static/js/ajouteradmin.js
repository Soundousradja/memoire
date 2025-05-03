document.addEventListener("DOMContentLoaded", function() {
    // Sélectionner le formulaire
    const adminForm = document.getElementById("adminForm");
    
    // Ajouter un écouteur d'événement sur la soumission du formulaire
    adminForm.addEventListener("submit", function(event) {
        // Empêcher la soumission normale du formulaire
        event.preventDefault();
        
        // Récupérer les valeurs du formulaire
        let name = document.getElementById("adminName").value.trim();
        let phone = document.getElementById("adminPhone").value.trim();
        let fileInput = document.getElementById("fileInput").files[0];
        let restaurant = document.getElementById("restaurantSelect").value;

        // Vérifier que tous les champs sont remplis
        if (!name || !phone || !fileInput || !restaurant) {
            alert("Tous les champs sont obligatoires !");
            return;
        }

        // Créer un objet FormData pour envoyer les données
        let formData = new FormData();
        formData.append("name", name);
        formData.append("phone", phone);
        formData.append("image", fileInput);
        formData.append("restaurant", restaurant);
        
        // Récupérer le token CSRF depuis le formulaire
        const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

        // Envoyer les données via fetch API
        fetch("/super/ajouter_admin/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Admin ajouté avec succès !");
                // Rediriger vers la page de gestion des admins
                window.location.href = "/super/gestion_admin/";
            } else {
                alert("Erreur lors de l'ajout !");
                console.log(data.errors);
            }
        })
        .catch(error => {
            console.error("Erreur:", error);
            alert("Une erreur s'est produite lors de l'ajout de l'admin.");
        });
    });
});