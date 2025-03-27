/**
 * Script de correction pour les choice-cards
 * Ce script réimplémente le gestionnaire d'événements pour les choice-cards
 * qui ne fonctionnent pas correctement dans le formulaire post-job.html
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Choice cards fix loaded!");
    
    // Fonction pour initialiser les choice-cards
    function initChoiceCards() {
        const choiceCards = document.querySelectorAll('.choice-card');
        console.log(`Initializing ${choiceCards.length} choice cards...`);
        
        choiceCards.forEach(function(card) {
            // Supprimer les gestionnaires d'événements existants
            const newCard = card.cloneNode(true);
            card.parentNode.replaceChild(newCard, card);
            
            const input = newCard.querySelector('input');
            
            // Initialiser l'état visuel
            if (input.checked) {
                newCard.classList.add('selected');
            }
            
            // Ajouter le nouveau gestionnaire d'événements
            newCard.addEventListener('click', function(e) {
                console.log(`Card clicked! Type: ${input.type}, Name: ${input.name}, Value: ${input.value}`);
                
                // Basculer l'état de la checkbox si le clic n'est pas directement sur l'input
                if (e.target !== input) {
                    input.checked = !input.checked;
                    console.log(`Input state toggled to: ${input.checked}`);
                }
                
                if (input.type === 'checkbox') {
                    // Mettre à jour la classe et le style
                    this.classList.toggle('selected', input.checked);
                    console.log(`Class 'selected' toggled: ${this.classList.contains('selected')}`);
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
            });
        });
        
        console.log("Choice cards initialized!");
    }
    
    // Initialiser les choice-cards au chargement de la page
    initChoiceCards();
    
    // Réinitialiser si le DOM change (par exemple, après l'ajout dynamique d'éléments)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // Vérifier si de nouveaux choice-cards ont été ajoutés
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && (node.classList.contains('choice-card') || node.querySelector('.choice-card'))) {
                        console.log("New choice cards detected, reinitializing...");
                        initChoiceCards();
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});
