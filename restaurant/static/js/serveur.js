let panier = [];

function ajouterAuPanier(id, name, price) {
    price = parseFloat(price);
    
    const plat = panier.find(p => p.id === id);
    if (plat) {
        plat.quantite += 1; // Changé "quantité" en "quantite" (sans accent)
    } else {
        panier.push({id, name, price, quantite: 1}); // Changé "quantité" en "quantite" (sans accent)
    }
    afficherPanier();
}

function supprimerDuPanier(id) {
    panier = panier.filter(p => p.id !== id);
    afficherPanier();
}

function modifierQuantite(id, delta) {
    const plat = panier.find(p => p.id === id);
    if (plat) {
        plat.quantite += delta; // Changé "quantité" en "quantite" (sans accent)
        if (plat.quantite <= 0) {
            supprimerDuPanier(id);
        } else {
            afficherPanier();
        }
    }
}

function calculerTotal() {
    return panier.reduce((total, plat) => total + (plat.price * plat.quantite), 0).toFixed(2); // Changé "quantité" en "quantite" (sans accent)
}

function afficherPanier() {
    const panierDiv = document.getElementById('panier');
    panierDiv.innerHTML = '';
    
    if (panier.length === 0) {
        panierDiv.innerHTML = '<p>Votre panier est vide</p>';
    } else {
        panier.forEach(p => {
            const platDiv = document.createElement('div');
            platDiv.className = 'panier-item';
            platDiv.innerHTML = `
                <h3>${p.name}</h3>
                <div class="quantite-controle">
                    <button onclick="modifierQuantite('${p.id}', -1)">-</button>
                    <span>${p.quantite}</span>
                    <button onclick="modifierQuantite('${p.id}', 1)">+</button>
                    <button class="supprimer" onclick="supprimerDuPanier('${p.id}')">X</button>
                </div>
                <div class="prix">${(p.price * p.quantite).toFixed(2)} DA</div>
            `;
            panierDiv.appendChild(platDiv);
        });
        
        const totalDiv = document.createElement('div');
        totalDiv.className = 'total-section';
        totalDiv.innerHTML = `Total: <span id="montant-total">${calculerTotal()}</span> DA`;
        panierDiv.appendChild(totalDiv);
    }
}

// Fonction pour annuler la commande
function annulerCommande() {
    panier = [];
    afficherPanier();
}

function envoyerCommande() {
    if (panier.length === 0) {
        alert("Le panier est vide !");
        return;
    }
    
    const tableId = document.getElementById('table').value;
    if (!tableId) {
        alert("Veuillez sélectionner une table.");
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    // Préparation des données de plats sans accents
    const platsData = panier.map(p => ({
        id: p.id,
        quantite: p.quantite // Changé "quantité" en "quantite" (sans accent)
    }));
    
    console.log("Données envoyées:", JSON.stringify({
        table_id: tableId,
        plats: platsData
    }));
    
    fetch("/restaurant/serveur/envoyer-commande/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            table_id: tableId,
            plats: platsData
        })
    })
    
    
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                console.error("Erreur serveur:", text);
                throw new Error("Erreur lors de l'envoi de la commande: " + response.status);
            });
        }
        return response.json();
    })
    .then(data => {
        alert(`Commande N°${data.commande_id} envoyée avec succès !`);
        annulerCommande();
    })
    .catch(error => {
        console.error("Erreur détaillée:", error);
        alert(error.message);
    });
}

// Fonction pour obtenir un cookie (pour le token CSRF)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Gestion du filtrage par catégorie
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner tous les boutons de catégorie
    const categoryButtons = document.querySelectorAll('.category-btn');
    
    // Ajouter un écouteur d'événement pour chaque bouton
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Retirer la classe 'active' de tous les boutons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            
            // Ajouter la classe 'active' au bouton cliqué
            this.classList.add('active');
            
            // Récupérer l'ID de la catégorie
            const categoryId = this.getAttribute('data-category');
            
            // Filtrer les plats
            const plats = document.querySelectorAll('.plat');
            plats.forEach(plat => {
                if (plat.getAttribute('data-category') === categoryId) {
                    plat.style.display = 'block';
                } else {
                    plat.style.display = 'none';
                }
            });
        });
    });
    
    // Déclencher un clic sur le premier bouton de catégorie pour filtrer dès le chargement
    if (categoryButtons.length > 0) {
        categoryButtons[0].click();
    }
    
    // Afficher le panier vide au chargement
    afficherPanier();
});