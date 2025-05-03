document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("adminForm");

    form.addEventListener("submit", function(event) {
        event.preventDefault();  // Prevent the form from submitting normally

        const formData = new FormData(form);
        
        // Add CSRF token manually to the formData (this is needed for CSRF protection in Django)
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        // Send the request to the current page (window.location.href)
        fetch(window.location.href, {
            method: "POST",
            body: formData,
        })
        .then(response => {
            // Check if the response is successful
            if (!response.ok) {
                // If not, throw an error with the response status
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();  // We get text first to inspect the raw response
        })
        .then(text => {
            console.log(text);  // Log the raw text of the response (helps in debugging)
            
            // Try to parse the text as JSON
            try {
                const data = JSON.parse(text);
                if (data.success) {
                    alert("Admin mis à jour avec succès !");
                    window.location.href = "/super/gestion_admin/";  // Redirect after successful update
                } else {
                    alert("Une erreur est survenue.");
                }
            } catch (error) {
                // If the response is not valid JSON, log it and display an error
                console.error("Erreur de JSON:", error);
                alert("Une erreur est survenue, réponse du serveur invalide.");
            }
        })
        .catch(error => {
            console.error("Erreur:", error);
            alert("Une erreur est survenue. Veuillez réessayer plus tard.");
        });

        return false;  // This prevents the default form submission
    });
});

// Function to get the CSRF token from the hidden input field
function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}
