document.addEventListener("DOMContentLoaded", function () {
    const ingredientList = document.getElementById("ingredientList");
    const addedIngredients = [];

    document.getElementById("addIngredientBtn").addEventListener("click", function () {
        const select = document.getElementById("ingredientSelect");
        const quantity = document.getElementById("ingredientQuantity").value;

        const id = select.value;
        const name = select.options[select.selectedIndex].text;

        if (!addedIngredients.find(i => i.id === id)) {
            addedIngredients.push({ id, quantity });

            const li = document.createElement("li");
            li.textContent = `${name} - ${quantity}`;
            ingredientList.appendChild(li);
        }
    });

    document.getElementById("platForm").addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append("plat_name", document.getElementById("platName").value);
        formData.append("price", document.getElementById("platPrice").value);
        formData.append("description", document.getElementById("description").value);
        formData.append("image", document.getElementById("fileInput").files[0]);

        addedIngredients.forEach((ingredient, index) => {
            formData.append(`ingredients[${index}][id]`, ingredient.id);
            formData.append(`ingredients[${index}][quantity]`, ingredient.quantity);
        });

        fetch("/restaurants/menu/ajouter/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Plat ajouté avec succès !");
                window.location.reload();
            } else {
                alert("Erreur : " + JSON.stringify(data.errors));
            }
        })
        .catch(err => console.error("Erreur lors de l'envoi:", err));
    });
});
