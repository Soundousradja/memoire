document.addEventListener("DOMContentLoaded", function() {
    const addPlatButton = document.getElementById("addPlat");
    const ingredientContainer = document.getElementById("ingredient-container");
    let ingredientCount = 1;

    if (addPlatButton) {
        addPlatButton.addEventListener("click", async function() {
            // ... (rest of your JavaScript data collection code) ...

            try {
                const response = await fetch("/super/menu/ajouter/", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    }
                });

                const contentType = response.headers.get("content-type");

                if (contentType && contentType.includes("application/json")) {
                    const data = await response.json();
                    if (data.success) {
                        alert("Plat ajouté avec succès !");
                        window.location.href = data.redirect_url;
                    } else {
                        if (data.errors) {
                            // Display form validation errors
                            let errorMessages = "Veuillez corriger les erreurs suivantes :\n";
                            for (const field in data.errors) {
                                errorMessages += `${getFieldLabel(field)}: ${data.errors[field].join(", ")}\n`;
                            }
                            alert(errorMessages);
                        } else {
                            alert("Erreur : " + (data.error || "Erreur inconnue"));
                        }
                    }
                } else {
                    const text = await response.text();
                    console.error("Réponse non JSON :", text);
                    alert("Erreur inattendue.");
                }
            } catch (error) {
                console.error("Erreur:", error);
                alert("Erreur de connexion au serveur");
            }
        });
    }

    function getCSRFToken() {
        return document.querySelector("input[name='csrfmiddlewaretoken']").value;
    }

    // Helper function to get a user-friendly label for form fields
    function getFieldLabel(fieldName) {
        switch (fieldName) {
            case "name":
                return "Nom du plat";
            case "price":
                return "Prix du plat";
            case "image":
                return "Image du plat";
            case "description":
                return "Description";
            case "is_available":
                return "Disponibilité";
            case "ingredients":
                return "Ingrédients";
            default:
                return fieldName;
        }
    }
});