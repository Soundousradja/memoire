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
            
            // Récupérer le token CSRF depuis le formulaire
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Récupérer les valeurs du formulaire
            const restaurant = document.getElementById('restaurant').value;
            const paiement = document.querySelector('input[name="paiement"]:checked').value;
            const plats = [];

            // Récupérer les plats du panier
            document.querySelectorAll('.plat-panier').forEach(platElem => {
                const id = parseInt(platElem.getAttribute('data-id'));
                const quantite = parseInt(platElem.querySelector('.quantity-input').value);
                plats.push({ id: id, quantite: quantite });
            });

            // Créer l'objet de données pour l'envoi
            const commandeData = {
                restaurant: restaurant,
                mode_paiement: paiement,
                plats: plats
            };

            // Envoi des données au serveur
            fetch('/restaurant/passer-commande/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(commandeData),
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                // Vérifier la présence du message de succès au lieu de la propriété 'success'
                if (data.message && data.message.includes('succès')) {
                    alert('Votre commande a été passée avec succès!');
                    window.location.href = '/restaurant/';
                } else {
                    alert('Une erreur est survenue: ' + (data.error || "Erreur inconnue"));
                }
            })
            .catch(error => {
                console.error('Erreur complète:', error);
                alert('Une erreur est survenue lors de la commande: ' + error.message);
            });
        });
    }
});