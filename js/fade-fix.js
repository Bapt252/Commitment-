/**
 * Script de correction pour l'animation fade-in
 * Ce script force tous les éléments avec la classe .fade-in à avoir la classe .visible
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Fade-in fix loaded!");
    
    // Force tous les éléments .fade-in à être visibles
    function forceFadeInVisibility() {
        const fadeInElements = document.querySelectorAll('.fade-in, .slide-in-right');
        console.log(`Forcing visibility on ${fadeInElements.length} elements...`);
        
        fadeInElements.forEach(function(element) {
            element.classList.add('visible');
        });
        
        console.log("Fade-in elements now visible!");
    }
    
    // Appliquer immédiatement
    forceFadeInVisibility();
    
    // Réappliquer après un court délai pour s'assurer que tous les éléments sont traités
    setTimeout(forceFadeInVisibility, 500);
});
