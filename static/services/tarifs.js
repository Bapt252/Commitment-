/**
 * NexTen - Scripts pour la page tarifs
 * Version améliorée avec onglets au lieu du toggle
 */

document.addEventListener('DOMContentLoaded', function() {
    // Gestion des onglets de période (mensuel, trimestriel, annuel)
    const pricingTabs = document.querySelectorAll('.pricing-tab');
    const priceContainers = document.querySelectorAll('.price-container');
    
    pricingTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Réinitialiser tous les onglets
            pricingTabs.forEach(t => t.classList.remove('active'));
            
            // Activer l'onglet courant
            this.classList.add('active');
            
            // Récupérer la période sélectionnée
            const period = this.getAttribute('data-period');
            
            // Mettre à jour l'affichage des prix
            priceContainers.forEach(container => {
                // Masquer tous les conteneurs de prix
                container.classList.add('hidden');
                
                // Afficher uniquement les conteneurs correspondant à la période sélectionnée
                if (container.getAttribute('data-period') === period) {
                    container.classList.remove('hidden');
                }
            });
        });
    });
    
    // Accordéon FAQ
    const accordionButtons = document.querySelectorAll('.accordion-button');
    
    accordionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const accordionItem = this.parentElement;
            
            // Toggle active state
            const isActive = accordionItem.classList.contains('active');
            
            // Fermer tous les items ouverts
            document.querySelectorAll('.accordion-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Si l'élément n'était pas actif, on l'active
            if (!isActive) {
                accordionItem.classList.add('active');
            }
        });
    });
    
    // Animation des cartes au scroll
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.pricing-card, .ppu-card, .ps-card');
        const windowHeight = window.innerHeight;
        
        elements.forEach((element, index) => {
            const elementTop = element.getBoundingClientRect().top;
            
            if (elementTop < windowHeight - 100) {
                // Ajouter un délai progressif basé sur l'index
                setTimeout(() => {
                    element.classList.add('fade-in');
                    element.classList.add('active');
                }, 150 * index);
            }
        });
    };
    
    // Ajouter la classe pour l'animation d'entrée
    document.querySelectorAll('.pricing-card, .ppu-card, .ps-card').forEach(card => {
        card.classList.add('fade-in');
    });
    
    // Déclencher l'animation au chargement et au défilement
    window.addEventListener('scroll', animateOnScroll);
    // Déclencher après un court délai au chargement initial
    setTimeout(animateOnScroll, 500);
});
