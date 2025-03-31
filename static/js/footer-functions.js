// Fonction pour le bouton de retour en haut
document.addEventListener('DOMContentLoaded', function() {
  const backToTopButton = document.getElementById('back-to-top');
  
  // Afficher/masquer le bouton en fonction de la position de défilement
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
  });
  
  // Défilement fluide vers le haut lorsque le bouton est cliqué
  backToTopButton.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
});