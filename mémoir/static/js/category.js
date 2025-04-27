function selectCategorie(categorieId) {
    // Rediriger vers la page des plats de cette catégorie
    window.location.href = `/super/categorie_plats/${categorieId}/`;
}
document.addEventListener("DOMContentLoaded", function() {
    const modifierButtons = document.querySelectorAll(".modifier-btn");
    
    modifierButtons.forEach(button => {
        button.addEventListener("click", function() {
            const platId = button.getAttribute("data-plat-id");
            window.location.href = `/super/plat/modifier/${platId}`;
        });
    });
});
