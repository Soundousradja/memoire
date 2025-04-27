document.getElementById("addRestaurant").addEventListener("click", function() {
    const name = document.getElementById("restaurantName").value;
    const address = document.getElementById("restaurantAddress").value;
    const fileInput = document.getElementById("fileInput").files[0];

    if (!name || !address || !fileInput) {
        alert("Veuillez remplir tous les champs et choisir une image !");
        return;
    }

    const formData = new FormData();  //creating a formdata to send the data
    formData.append("name", name); //adding this info to the formdata
    formData.append("address", address);
    formData.append("image", fileInput);

    fetch("/super/ajouter_restaurant/", { //send data using fetch() 
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Restaurant ajouté avec succès !");
            window.location.href ="/super/restaurants/";
        } else {
            alert("Erreur lors de l'ajout du restaurant.");
        }
    })
    .catch(error => console.error("Erreur:", error));
});


function getCSRFToken() {
    return document.querySelector("input[name='csrfmiddlewaretoken']").value;
}