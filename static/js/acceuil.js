window.addEventListener('scroll', function () {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 100) {
      nav.classList.add('fixed-nav');
    } else {
      nav.classList.remove('fixed-nav');
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('menu-carousel');
    const prevButton = document.querySelector('.carousel-button.prev');
    const nextButton = document.querySelector('.carousel-button.next');
    const menuItems = document.querySelectorAll('.menu-item');
    
    let currentIndex = 0;
    const itemsToShow = 3; // Nombre d'éléments visibles à la fois
    const totalItems = menuItems.length;
    
    // Initialisation: cacher les éléments au-delà de itemsToShow
    function initCarousel() {
        // Définir la largeur du container
        const menuItemWidth = menuItems[0].offsetWidth;
        const menuItemMargin = 20; // Valeur de gap entre les items
        
        // Cacher les éléments qui ne devraient pas être visibles
        for (let i = itemsToShow; i < totalItems; i++) {
            menuItems[i].style.display = 'none';
        }
    }
    
    // Fonction pour afficher les bons éléments
    function updateCarousel() {
        for (let i = 0; i < totalItems; i++) {
            if (i >= currentIndex && i < currentIndex + itemsToShow) {
                menuItems[i].style.display = 'block';
            } else {
                menuItems[i].style.display = 'none';
            }
        }
    }
    
    // Bouton suivant
    nextButton.addEventListener('click', function() {
        if (currentIndex + itemsToShow < totalItems) {
            currentIndex++;
            updateCarousel();
        }
    });
    
    // Bouton précédent
    prevButton.addEventListener('click', function() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });
    
    // Initialiser le carrousel
    initCarousel();
  });

  ////
  document.addEventListener('DOMContentLoaded', function() {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.menu-slide');
    const slider = document.querySelector('.menu-slider');
    const totalSlides = slides.length;
    
    // Initialisation du slider
    slider.style.width = `${totalSlides * 100}%`;
    
    // Fonction pour déplacer le slider
    window.moveSlider = function(direction) {
        currentSlide += direction;
        
        // Gestion du débordement
        if (currentSlide >= totalSlides) {
            currentSlide = 0;
        } else if (currentSlide < 0) {
            currentSlide = totalSlides - 1;
        }
        
        // Déplacement du slider avec animation
        slider.style.transform = `translateX(-${currentSlide * 100}%)`;
        slider.style.transition = 'transform 0.5s ease';
    };
    
    // Réinitialisation de la transition après l'animation
    slider.addEventListener('transitionend', function() {
        if (currentSlide >= totalSlides || currentSlide < 0) {
            slider.style.transition = 'none';
            slider.style.transform = `translateX(-${currentSlide * 100}%)`;
        }
    });
});