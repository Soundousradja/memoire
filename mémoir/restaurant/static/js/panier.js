

document.addEventListener('DOMContentLoaded', function () {

    // Update cart count in the header
    function updateCartCount() {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            const cartRows = document.querySelectorAll('#panier-content table tbody tr');
            cartCountElement.innerHTML = cartRows ? cartRows.length : 0;
        }
    }

    // Call updateCartCount on page load
    updateCartCount();

    // Handle increment buttons
    document.querySelectorAll('.increment').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.quantity-input[data-id="${id}"]`);
            if (input) {
                const currentValue = parseInt(input.value) || 1;
                input.value = currentValue + 1;
                updateQuantity(id, parseInt(input.value));
            }
        });
    });

    // Handle decrement buttons
    document.querySelectorAll('.decrement').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.quantity-input[data-id="${id}"]`);
            if (input) {
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    updateQuantity(id, parseInt(input.value));
                }
            }
        });
    });

    // Handle direct quantity input change
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function () {
            const id = this.getAttribute('data-id');
            let newVal = parseInt(this.value);
            if (!newVal || newVal < 1) {
                this.value = 1;
                newVal = 1;
            }
            updateQuantity(id, newVal);
        });
    });

    // Update quantity via AJAX
    function updateQuantity(platId, quantity) {
        fetch(`/restaurant/modifier-panier/${platId}/${quantity}/`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                console.warn('Erreur de mise à jour:', data);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la requête:', error);
        });
    }

    // Handle order form submission
    const orderForm = document.getElementById('order-form');
    if (orderForm) {
        orderForm.addEventListener('submit', function (e) {
            console.log("Submit détecté");
            e.preventDefault();

            const restaurantSelect = document.getElementById('restaurant');
            const paymentRadio = document.querySelector('input[name="paiement"]:checked');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

            if (!restaurantSelect || !paymentRadio || !csrfToken) {
                alert("Veuillez remplir tous les champs requis.");
                return;
            }

            const restaurant = restaurantSelect.value;
            const paiement = paymentRadio.value;

            const commandeData = {
                restaurant: restaurant,
                mode_paiement: paiement,
            };

            console.log("Commande envoyée:", commandeData);

            fetch('/restaurant/passer-commande/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken.value,
                },
                body: JSON.stringify(commandeData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur HTTP ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Commande passée avec succès!');
                    window.location.href = '/restaurant/';
                } else {
                    alert('Erreur: ' + (data.error || 'Commande échouée'));
                }
            })
            .catch(error => {
                console.error('Erreur de commande:', error);
                alert('Erreur lors de la commande: ' + error.message);
            });
        });
    }
});
