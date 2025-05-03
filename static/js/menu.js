document.addEventListener("DOMContentLoaded", function () {
    // Éléments du DOM
    const restaurants = document.querySelectorAll('.restaurant-item');
    const categoriesContainer = document.getElementById('categories-container');
    const platsSection = document.getElementById('plats-section');
    const restaurantSelection = document.querySelector('.restaurant-selection');
    
    // Sélection du restaurant
    document.querySelectorAll(".select-restaurant-btn").forEach(button => {
        button.addEventListener("click", function() {
            const restaurantId = this.getAttribute("data-id");
            
            // Rediriger vers la même page avec le paramètre restaurant_id
            window.location.href = `/restaurant/M?restaurant=${restaurantId}`;
        });
    });
    
    // Si un restaurant est déjà sélectionné (vérifie l'URL)
    const urlParams = new URLSearchParams(window.location.search);
    const selectedRestaurantId = urlParams.get('restaurant');
    
    if (selectedRestaurantId) {
        // Masquer la sélection de restaurant et afficher les catégories et plats
        restaurantSelection.style.display = "none";
        categoriesContainer.style.display = "block";
        platsSection.style.display = "block";
        
        // Filtrer les plats pour la première catégorie
        const categories = document.querySelectorAll('.categorie-item');
        let plats = document.querySelectorAll('.plat');
        
        // Fonction pour afficher les plats d'une catégorie
        function filterPlats(categorieId) {
            plats.forEach(plat => {
                if (plat.dataset.categorieId === categorieId) {
                    plat.style.display = "block";  // Afficher les plats de la catégorie sélectionnée
                } else {
                    plat.style.display = "none";  // Masquer les autres plats
                }
            });
        }
    
        // Ajouter un événement à chaque catégorie
        categories.forEach(categorie => {
            categorie.addEventListener("click", function () {
                let categorieId = this.getAttribute("data-categorie-id");
                filterPlats(categorieId);
                
                // Ajouter une classe 'active' à la catégorie sélectionnée
                categories.forEach(cat => cat.classList.remove('active'));
                this.classList.add('active');
            });
        });
    
        // Afficher les plats de la première catégorie au chargement
        if (categories.length > 0) {
            let firstCategoryId = categories[0].getAttribute("data-categorie-id");
            filterPlats(firstCategoryId);
            categories[0].classList.add('active');
        }
    }
    
    // Gestion du panier
    document.querySelectorAll(".add-btn").forEach(button => {
        button.addEventListener("click", function () {
            let platId = this.getAttribute("data-id");
            fetch(`/restaurant/ajouter-au-panier/${platId}/`, {
                method: "GET",
            }).then(response => response.json())
              .then(data => {
                  // Mise à jour du compteur
                  let cartCount = document.getElementById("cart-count");
                  cartCount.textContent = parseInt(cartCount.textContent || "0") + 1;
              });
        });
    });
});