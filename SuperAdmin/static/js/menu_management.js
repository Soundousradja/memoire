function deletePlat(platId) {
    if (confirm("Voulez-vous vraiment supprimer ce plat ?")) {
        fetch(`/restaurants/menu/supprimer/${platId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json"
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Option 1: Remove from UI
                document.getElementById(`plat-${platId}`)?.remove();
                // Option 2: Redirect
                window.location.href = "/restaurants/menu/pizza/";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert(error.error || "Erreur lors de la suppression");
        });
    }
}

// CSRF Token function
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]').value;
}