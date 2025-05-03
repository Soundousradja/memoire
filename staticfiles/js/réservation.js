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
            fetch(`/check-availability/?date=${date}&time=${time}`)
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
