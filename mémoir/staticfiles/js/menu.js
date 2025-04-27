document.addEventListener("DOMContentLoaded", function () {
    // Éléments du DOM
    const categoriesContainer = document.getElementById('categories-container');
    const platsSection = document.getElementById('plats-section');
    const restaurantSelection = document.querySelector('.restaurant-selection');
    
    // Sélection du restaurant - Solution corrigée
    document.querySelectorAll("button.select-restaurant-btn, button:contains('Voir le menu')").forEach(button => {
        button.addEventListener("click", function() {
            // Récupérer l'ID du restaurant soit depuis data-id, soit depuis l'élément parent
            let restaurantId = this.getAttribute("data-id");
            if (!restaurantId) {
                const restaurantItem = this.closest('.restaurant-item');
                if (restaurantItem) {
                    restaurantId = restaurantItem.getAttribute("data-restaurant-id");
                }
            }
            
            if (restaurantId) {
                console.log("Restaurant sélectionné:", restaurantId); // Debug
                // Rediriger vers la page du menu avec le paramètre restaurant
                window.location.href = `/restaurant/M?restaurant=${restaurantId}`;
            }
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
    
    // Ajout d'une fonction pour sélectionner les boutons avec un texte spécifique
    // Cette partie est nécessaire pour jQuery-like :contains functionality
    if (!Element.prototype.matches) {
        Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                    Element.prototype.webkitMatchesSelector;
    }
    
    if (!document.querySelectorAll.prototype) {
        document.querySelectorAll = function(selectors) {
            var elements = document.querySelectorAll(selectors);
            return elements;
        };
    }
    
    // Sélectionner tous les éléments qui contiennent un texte spécifique
    document.querySelectorAll = function(selectors) {
        if (selectors.includes(":contains(")) {
            var match = selectors.match(/:contains\((['"])(.*?)\1\)/);
            if (match) {
                var text = match[2];
                var elements = Array.from(document.querySelectorAll("*"));
                return elements.filter(el => el.textContent.includes(text));
            }
        }
        return document.querySelectorAll(selectors);
    };
});
