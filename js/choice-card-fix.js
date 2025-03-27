/**
 * Correction pour les cartes de choix (choice cards)
 * Ce script corrige le problème de sélection des délais de recrutement
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner toutes les cartes de choix
    const choiceCards = document.querySelectorAll('.choice-card');
    
    // Appliquer le gestionnaire d'événements à chaque carte
    choiceCards.forEach(function(card) {
        const input = card.querySelector('input');
        
        // Initialiser l'état
        if (input.checked) {
            card.classList.add('selected');
        }
        
        // Fixer le problème de sélection des délais de recrutement
        card.addEventListener('click', function(e) {
            const input = this.querySelector('input');
            if (e.target !== input) {
                input.checked = !input.checked;
            }
            
            if (input.type === 'checkbox') {
                this.classList.toggle('selected', input.checked);
            } else if (input.type === 'radio') {
                // Désélectionner tous les autres radios du même groupe
                const name = input.getAttribute('name');
                document.querySelectorAll(`input[name="${name}"]`).forEach(function(r) {
                    const parentCard = r.closest('.choice-card');
                    if (parentCard) {
                        parentCard.classList.toggle('selected', r.checked);
                    }
                });
                
                // Déclencher l'événement change pour les logiques conditionnelles
                const event = new Event('change');
                input.dispatchEvent(event);
            }
            
            // Mise à jour de la barre de progression après sélection
            if (typeof updateProgressBar === 'function') {
                updateProgressBar();
            }
        });
    });
});