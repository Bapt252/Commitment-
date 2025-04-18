/**
 * NexTen - Scripts pour la page tarifs
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle entre mensuel et annuel
    const billingToggle = document.getElementById('billing-toggle');
    const monthlyLabels = document.querySelectorAll('.toggle-label')[0];
    const annualLabels = document.querySelectorAll('.toggle-label')[1];
    const monthlyContainers = document.querySelectorAll('.price-container.monthly');
    const annualContainers = document.querySelectorAll('.price-container.annually');
    
    if (billingToggle) {
        billingToggle.addEventListener('change', function() {
            if (this.checked) {
                // Annuel
                monthlyLabels.classList.remove('active');
                annualLabels.classList.add('active');
                
                monthlyContainers.forEach(container => {
                    container.classList.add('hidden');
                });
                
                annualContainers.forEach(container => {
                    container.classList.remove('hidden');
                });
            } else {
                // Mensuel
                monthlyLabels.classList.add('active');
                annualLabels.classList.remove('active');
                
                monthlyContainers.forEach(container => {
                    container.classList.remove('hidden');
                });
                
                annualContainers.forEach(container => {
                    container.classList.add('hidden');
                });
            }
        });
    }
    
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
    
    // Highlight des options de prix au survol
    const pricingOptions = document.querySelectorAll('.pricing-options .option');
    
    pricingOptions.forEach(option => {
        option.addEventListener('mouseover', function() {
            const parentCard = this.closest('.pricing-card');
            const allOptions = parentCard.querySelectorAll('.option');
            
            allOptions.forEach(opt => {
                opt.style.opacity = '0.6';
            });
            
            this.style.opacity = '1';
        });
        
        option.addEventListener('mouseout', function() {
            const parentCard = this.closest('.pricing-card');
            const allOptions = parentCard.querySelectorAll('.option');
            
            allOptions.forEach(opt => {
                opt.style.opacity = '1';
            });
        });
    });
    
    // Animation au défilement
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.pricing-card, .offer-card');
        const windowHeight = window.innerHeight;
        
        elements.forEach((element, index) => {
            const elementTop = element.getBoundingClientRect().top;
            
            if (elementTop < windowHeight - 100) {
                // Ajouter un délai progressif basé sur l'index
                setTimeout(() => {
                    element.classList.add('animate-in');
                }, 100 * index);
            }
        });
    };
    
    // Déclencher l'animation au chargement et au défilement
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Déclencher au chargement initial
});