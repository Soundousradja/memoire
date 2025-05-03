document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("filtrer").addEventListener("click", () => {
        const restaurantId = document.getElementById("restaurant").value;
        const startDate = document.getElementById("startDate").value;
        const endDate = document.getElementById("endDate").value;

        if (!restaurantId || !startDate || !endDate) {
            alert("Tous les champs sont requis !");
            return;
        }

        fetch(`/api/ventes/?restaurant=${restaurantId}&start=${startDate}&end=${endDate}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("montant").textContent = data.montant;
                document.getElementById("depense").textContent = data.depense;
                document.getElementById("retenu").textContent = data.retenu;
            })
            .catch(err => {
                console.error("Erreur :", err);
                alert("Impossible de récupérer les données.");
            });
    });
});
