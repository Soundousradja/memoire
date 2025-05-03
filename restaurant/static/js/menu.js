document.addEventListener("DOMContentLoaded", function () {
    // Sélection des éléments DOM principaux
    const restaurantSelection = document.querySelector('.restaurant-selection');
    const categoriesContainer = document.getElementById('categories-container');
    const platsSection = document.getElementById('plats-section');
    const platsContainer = document.getElementById('plats-container');

    // Gestionnaire pour les boutons de sélection de restaurant
    document.querySelectorAll(".select-restaurant-btn").forEach(button => {
        button.addEventListener("click", function() {
            const restaurantId = this.getAttribute("data-id");
            window.location.href = `/restaurant/M?restaurant=${restaurantId}`;
        });
    });
    
    // Vérifier si un restaurant est sélectionné dans l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const selectedRestaurantId = urlParams.get('restaurant');

    if (selectedRestaurantId) {
        // Afficher les sections des catégories et des plats
        restaurantSelection.style.display = "none";
        categoriesContainer.style.display = "block";
        platsSection.style.display = "block";
        
        console.log("Restaurant sélectionné, affichage des catégories et plats");
        
        // Afficher tous les plats initialement
        showAllPlats();
       
        // Gestionnaire pour les clics sur les catégories
        const categories = document.querySelectorAll('.categorie-item');
        categories.forEach(categorie => {
            categorie.addEventListener("click", function () {
                const categorieId = this.getAttribute("data-categorie-id");
                
                console.log("Catégorie sélectionnée:", categorieId);
                
                // Mettre en évidence la catégorie sélectionnée
                categories.forEach(cat => cat.classList.remove('active'));
                this.classList.add('active');
                
                // Créer une nouvelle URL avec les paramètres
                const url = `/restaurant/M?restaurant=${selectedRestaurantId}&categorie=${categorieId}`;
                
                // Mettre à jour l'URL sans rafraîchir la page
                window.history.pushState({}, '', url);
                
                // Charger les plats de la catégorie via AJAX
                fetch(url, {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    // Mettre à jour le contenu des plats
                    platsContainer.innerHTML = data;
                    
                    // Réinitialiser les gestionnaires d'événements pour les nouveaux boutons d'ajout
                    setupAddToCartButtons();
                })
                .catch(error => {
                    console.error('Erreur lors du chargement des plats:', error);
                });
            });
        });

        // Option 1: Afficher tous les plats au début
        // Option 2: Activer la première catégorie par défaut
        if (categories.length > 0) {
            console.log("Activation de la première catégorie");
            categories[0].classList.add('active');
            // Option: simuler un clic sur la première catégorie
            // categories[0].click();
        }
    } else {
        console.log("Aucun restaurant sélectionné");
    }
})
// Fonction pour afficher tous les plats initialement
function showAllPlats() {
    const plats = document.querySelectorAll('.plat');
    if (plats.length > 0) {
        console.log(`Affichage de ${plats.length} plats`);
        plats.forEach(plat => {
            plat.style.display = 'block';
        });
    } else {
        console.log("Aucun plat trouvé à afficher");
        // Si aucun plat n'est chargé, on peut essayer de recharger la page
        const urlParams = new URLSearchParams(window.location.search);
        const selectedRestaurantId = urlParams.get('restaurant');
        if (selectedRestaurantId) {
            fetch(`/restaurant/M?restaurant=${selectedRestaurantId}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(data => {
                platsContainer.innerHTML = data;
                setupAddToCartButtons();
            })
            .catch(error => {
                console.error('Erreur lors du chargement des plats:', error);
            });
        }
    }
}