// This event listener runs when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function() {
    console.log("Gestion des Admins chargée !");
});

// Function to delete an admin given its ID
function deleteAdmin(adminId) {
    // Ask for confirmation before deletion
    if (confirm("Voulez-vous vraiment supprimer cet Admin ?")) {
        // Send a POST request to the URL responsible for deletion,
        // using the adminId in the URL. (Make sure your Django URL pattern matches this.)
        fetch(`/super/supprimer_admin/${adminId}/`, {
            method: "POST", // Using POST for deletion to work with CSRF protection
            headers: {
                "X-CSRFToken": getCSRFToken() // Retrieve the CSRF token to include in the header
            }
        })
        // Parse the server response as JSON
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Admin supprimé !");
                // Redirect to the admin list page (here assumed to be "/restaurants/gestion_admin")
                window.location.href = "/super/gestion_admin/";
            } else {
                alert("Erreur lors de la suppression.");
            }
        })
        .catch(error => console.error("Erreur:", error)); // Log any errors to the console
    }
}

// Function to redirect to the admin edit page for the given ID
function editAdmin(id) {
    // Redirect to the URL for modifying an admin.
    // The URL is constructed dynamically using the admin's ID.
    window.location.href = `/super/modifier_admin/${id}/`;
}

// Function to get the CSRF token from the cookies
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
