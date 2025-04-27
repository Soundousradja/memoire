document.addEventListener("DOMContentLoaded", function() {
    console.log("Gestion des restaurants chargée !");
});

function deleteRestaurant(restaurantId) {
    if (confirm("Voulez-vous vraiment supprimer ce restaurant ?")) {
        fetch(`/super/supprimer_restaurant/${restaurantId}/`, {
            method: "POST",  
            headers: {
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Restaurant supprimé !");
                window.location.href = "/super/restaurants/"; // Redirection
            } else {
                alert("Erreur lors de la suppression.");
            }
        })
        .catch(error => console.error("Erreur:", error));
    }
}

// Fonction pour récupérer le token CSRF


function getCSRFToken() {
    return document.querySelector("input[name='csrfmiddlewaretoken']").value;
}

function editRestaurant(id) {
    window.location.href = `/super/modifier_restaurant/${id}/`;
}

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            let trimmedCookie = cookie.trim();
            if (trimmedCookie.startsWith('csrftoken=')) {
                cookieValue = trimmedCookie.substring(10);
            }
        });
    }
    return cookieValue;
}
