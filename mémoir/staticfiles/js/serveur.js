let panier = [];


function ajouterAuPanier(id, name, price) {

    price = parseFloat(price);
    
    const plat = panier.find(p => p.id === id);
    if (plat) {
        plat.quantité += 1;
    } else {
        panier.push({id, name, price, quantité: 1});
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
        plat.quantité += delta;
        if (plat.quantité <= 0) {
            supprimerDuPanier(id);
        } else {
            afficherPanier();
        }
    }
}


function calculerTotal() {
    return panier.reduce((total, plat) => total + (plat.price * plat.quantité), 0).toFixed(2);
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
        <span>${p.quantité}</span>
        <button onclick="modifierQuantite('${p.id}', 1)">+</button>
        <button class="supprimer" onclick="supprimerDuPanier('${p.id}')">X</button>
    </div>
    <div class="prix">${(p.price * p.quantité).toFixed(2)} DA</div>
   
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
    // Récupérer le token CSRF depuis les cookies
    const csrftoken = getCookie('csrftoken');
    
    fetch("/restaurant/serveur/envoyer-commande/", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            table_id: tableId,
            plats: panier
        })
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error("Erreur lors de l'envoi de la commande !");
    })
    .then(data => {
        alert(`Commande N°${data.commande_id} envoyée avec succès !`);
        annulerCommande();
    })
    .catch(error => {
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


 // Script pour vérifier la disponibilité des tables
 document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    const timeInput = document.getElementById('time');
    
    // Vérifier la disponibilité quand la date ou l'heure change
    dateInput.addEventListener('change', checkAvailability);
    timeInput.addEventListener('change', checkAvailability);
    
    function checkAvailability() {
        const date = dateInput.value;
        const time = timeInput.value;
        
        if (date && time) {
            // Appel AJAX pour vérifier la disponibilité
            fetch(`/restaurant/check-availability/?date=${date}&time=${time}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('disponibilite-tables').innerHTML = 
                            `<p class="error-message">${data.error}</p>`;
                        return;
                    }
                    
                    // Générer dynamiquement la liste des disponibilités
                    let disponibiliteHTML = '';
                    
                    // Trier les clés pour afficher les tables par ordre de capacité
                    const keys = Object.keys(data).sort((a, b) => {
                        // Extraire les nombres de "disponibles_X"
                        const numA = parseInt(a.split('_')[1]);
                        const numB = parseInt(b.split('_')[1]);
                        return numA - numB;
                    });
                    
                    // Générer le HTML pour chaque capacité
                    keys.forEach(key => {
                        const capacite = key.split('_')[1];
                        disponibiliteHTML += `<p>Tables pour ${capacite} personnes: <span>${data[key]} disponible(s)</span></p>`;
                    });
                    
                    document.getElementById('disponibilite-tables').innerHTML = disponibiliteHTML;
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    document.getElementById('disponibilite-tables').innerHTML = 
                        '<p class="error-message">Erreur lors de la vérification de disponibilité</p>';
                });
        }
    }
});