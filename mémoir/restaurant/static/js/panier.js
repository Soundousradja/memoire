document.addEventListener("DOMContentLoaded", function () {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let cartContainer = document.getElementById("cart-container");

    function displayCart() {
        cartContainer.innerHTML = "";
        cart.forEach((item, index) => {
            let div = document.createElement("div");
            div.classList.add("cart-item");
            div.innerHTML = `
                <p>${item.nom} - ${item.prix} DA</p>
                <input type="number" value="${item.quantity}" min="1" data-index="${index}" class="quantity-input">
                <button class="remove-btn" data-index="${index}">Supprimer</button>
            `;
            cartContainer.appendChild(div);
        });

        document.querySelectorAll(".quantity-input").forEach(input => {
            input.addEventListener("change", updateQuantity);
        });

        document.querySelectorAll(".remove-btn").forEach(button => {
            button.addEventListener("click", removeFromCart);
        });
    }

    function updateQuantity(event) {
        let index = event.target.getAttribute("data-index");
        cart[index].quantity = parseInt(event.target.value);
        localStorage.setItem("cart", JSON.stringify(cart));
    }

    function removeFromCart(event) {
        let index = event.target.getAttribute("data-index");
        cart.splice(index, 1);
        localStorage.setItem("cart", JSON.stringify(cart));
        displayCart();
    }

    document.getElementById("order-form").addEventListener("submit", function (event) {
        event.preventDefault();
        
        let order = {
            nom: document.getElementById("nom").value,
            prenom: document.getElementById("prenom").value,
            adresse: document.getElementById("adresse").value,
            telephone: document.getElementById("telephone").value,
            restaurant: document.getElementById("restaurant").value,
            plats: cart
        };

        fetch("/restaurant/passer-commande/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(order)
        }).then(response => {
            if (response.ok) {
                alert("Commande envoyée !");
                localStorage.removeItem("cart");
                window.location.href = "/resturant/";
            }
        });
    });

    displayCart();
});
//Mise à jour de panier.js pour gérer la modification des quantités et l'envoi du formulaire
document.addEventListener("DOMContentLoaded", function () {
    // Gérer les boutons de quantité
    document.querySelectorAll('.increment').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.quantity-input[data-id="${id}"]`);
            input.value = parseInt(input.value) + 1;
            updateQuantity(id, parseInt(input.value));
        });
    });

    document.querySelectorAll('.decrement').forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.quantity-input[data-id="${id}"]`);
            if (parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
                updateQuantity(id, parseInt(input.value));
            }
        });
    });

    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const id = this.getAttribute('data-id');
            if (parseInt(this.value) < 1) {
                this.value = 1;
            }
            updateQuantity(id, parseInt(this.value));
        });
    });

    // Fonction pour mettre à jour la quantité d'un plat
    function updateQuantity(platId, quantity) {
        // Envoyer la requête au serveur
        fetch(`/restaurant/modifier-panier/${platId}/${quantity}/`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            // Recharger la page pour mettre à jour les totaux
            if (data.success) {
                window.location.reload();
            }
        })
        .catch(error => console.error('Erreur:', error));
    }

    if (document.getElementById('order-form')) {
        document.getElementById('order-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les valeurs du formulaire
            const nom = document.getElementById('nom').value;
            const adresse = document.getElementById('adresse').value;
            const telephone = document.getElementById('telephone').value;
            const restaurant = document.getElementById('restaurant').value;
            const paiement = document.querySelector('input[name="paiement"]:checked').value;
            
            // Créer l'objet de données pour l'envoi
            const commandeData = {
                nom: nom,
                adresse: adresse,
                telephone: telephone,
                restaurant: restaurant,
                mode_paiement: paiement
            };
            
            console.log("Données à envoyer:", commandeData);  // Pour débogage
            
            // Envoi au serveur
            fetch('/restaurant/passer-commande/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(commandeData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur HTTP ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Votre commande a été passée avec succès!');
                    window.location.href = '/restaurant/';
                } else {
                    alert('Une erreur est survenue: ' + (data.error || "Erreur inconnue"));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue lors de la commande: ' + error.message);
            });
        });
    }
});