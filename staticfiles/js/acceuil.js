window.addEventListener('scroll', function () {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 100) {
      nav.classList.add('fixed-nav');
    } else {
      nav.classList.remove('fixed-nav');
    }
  });