/**
 * Script pour améliorer l'expérience utilisateur
 * Adds UI improvements for the candidate opportunities page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour ajouter un effet de carte animée au survol
    function enhanceCardInteraction() {
        const cards = document.querySelectorAll('.opportunity-card');
        
        cards.forEach(card => {
            // Ajouter l'effet tilt 3D
            card.addEventListener('mousemove', function(e) {
                const cardRect = card.getBoundingClientRect();
                const cardCenterX = cardRect.left + cardRect.width / 2;
                const cardCenterY = cardRect.top + cardRect.height / 2;
                const mouseX = e.clientX - cardCenterX;
                const mouseY = e.clientY - cardCenterY;
                
                // Calcul de l'angle de rotation (limité à 5 degrés maximum)
                const rotateY = (mouseX / (cardRect.width / 2)) * 3;
                const rotateX = -((mouseY / (cardRect.height / 2)) * 3);
                
                // Appliquer l'effet seulement sur les appareils non tactiles
                if (window.matchMedia('(hover: hover)').matches) {
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
                    
                    // Effet de lumière
                    const glarePosition = `${50 + (mouseX / cardRect.width) * 40}% ${50 + (mouseY / cardRect.height) * 40}%`;
                    card.style.backgroundImage = `radial-gradient(circle at ${glarePosition}, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 60%)`;
                }
            });
            
            // Réinitialiser à la sortie du survol
            card.addEventListener('mouseleave', function() {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0)';
                card.style.backgroundImage = 'none';
            });
        });
    }
    
    // Fonction pour améliorer l'interaction avec les boutons
    function enhanceButtonInteraction() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            // Ajouter l'effet de ripple sur les boutons
            button.classList.add('ripple-effect');
            
            button.addEventListener('click', function(e) {
                const rect = button.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const clickY = e.clientY - rect.top;
                
                // Création de l'élément ripple
                const ripple = document.createElement('span');
                ripple.className = 'ripple';
                ripple.style.width = ripple.style.height = `${Math.max(rect.width, rect.height) * 2}px`;
                ripple.style.left = `${clickX - Math.max(rect.width, rect.height)}px`;
                ripple.style.top = `${clickY - Math.max(rect.width, rect.height)}px`;
                
                // Insertion dans le bouton et suppression après animation
                button.appendChild(ripple);
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
    
    // Fonction pour ajouter un défilement fluide aux ancres
    function enhanceSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === "#") return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // Fonction pour améliorer la navigation avec le clavier
    function enhanceKeyboardNavigation() {
        // Ajouter focus-visible à tous les éléments focusables
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        document.querySelectorAll(focusableElements).forEach(el => {
            el.classList.add('focus-visible-element');
        });
        
        // Ajouter des sauts de navigation pour l'accessibilité
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-to-content';
        skipLink.textContent = 'Aller au contenu principal';
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Ajouter des attributs ARIA pour améliorer l'accessibilité
        document.querySelectorAll('.filter-badge').forEach(badge => {
            badge.setAttribute('role', 'button');
            badge.setAttribute('tabindex', '0');
            badge.setAttribute('aria-pressed', badge.classList.contains('active'));
            
            badge.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    badge.click();
                }
            });
            
            badge.addEventListener('click', () => {
                document.querySelectorAll('.filter-badge').forEach(b => {
                    b.setAttribute('aria-pressed', 'false');
                });
                badge.setAttribute('aria-pressed', 'true');
            });
        });
    }
    
    // Fonction pour ajouter des animations de chargement
    function enhanceLoadingAnimations() {
        // Ajouter une classe au body pour indiquer que la page est chargée
        setTimeout(() => {
            document.body.classList.add('page-loaded');
        }, 300);
        
        // Animer séquentiellement les cartes d'opportunités
        const cards = document.querySelectorAll('.opportunity-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1 + 0.3}s`;
            card.classList.add('animate-entry');
        });
    }
    
    // Fonction pour ajouter un feedback visuel aux actions utilisateur
    function enhanceUserFeedback() {
        // Ajouter une notification de succès pour les actions de sauvegarde
        document.querySelectorAll('.btn-save').forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.closest('.note-input-container').querySelector('input');
                
                if (input.value.trim() !== '') {
                    // Créer la notification de succès
                    const notification = document.createElement('div');
                    notification.className = 'notification-toast';
                    notification.innerHTML = `
                        <div class="notification-content">
                            <i class="fas fa-check-circle"></i>
                            <span>Note enregistrée avec succès!</span>
                        </div>
                        <button class="close-notification" aria-label="Fermer la notification">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    // Ajouter au DOM
                    document.body.appendChild(notification);
                    
                    // Animation d'entrée
                    setTimeout(() => {
                        notification.classList.add('show');
                    }, 10);
                    
                    // Supprimer après délai
                    setTimeout(() => {
                        notification.classList.remove('show');
                        setTimeout(() => {
                            notification.remove();
                        }, 300);
                    }, 3000);
                    
                    // Fermeture manuelle
                    notification.querySelector('.close-notification').addEventListener('click', function() {
                        notification.classList.remove('show');
                        setTimeout(() => {
                            notification.remove();
                        }, 300);
                    });
                }
            });
        });
        
        // Ajouter confirmation lors de l'annulation d'une candidature
        document.querySelectorAll('.btn-outline-danger').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Créer la modal de confirmation
                const modal = document.createElement('div');
                modal.className = 'confirmation-modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Confirmation</h3>
                            <button class="close-modal" aria-label="Fermer">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p>Êtes-vous sûr de vouloir annuler cette candidature ?</p>
                            <p class="text-muted">Cette action est irréversible.</p>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-outline modal-cancel">Annuler</button>
                            <button class="btn btn-outline-danger modal-confirm">Confirmer l'annulation</button>
                        </div>
                    </div>
                `;
                
                // Ajouter au DOM
                document.body.appendChild(modal);
                
                // Animation d'entrée
                setTimeout(() => {
                    modal.classList.add('show');
                }, 10);
                
                // Gérer les événements de la modal
                modal.querySelector('.close-modal').addEventListener('click', closeModal);
                modal.querySelector('.modal-cancel').addEventListener('click', closeModal);
                modal.querySelector('.modal-confirm').addEventListener('click', function() {
                    // Simuler l'annulation (ici juste un retour visuel)
                    const card = btn.closest('.opportunity-card');
                    card.style.opacity = '0.5';
                    card.style.pointerEvents = 'none';
                    
                    // Fermer la modal
                    closeModal();
                    
                    // Afficher une notification
                    const notification = document.createElement('div');
                    notification.className = 'notification-toast warning';
                    notification.innerHTML = `
                        <div class="notification-content">
                            <i class="fas fa-exclamation-circle"></i>
                            <span>Candidature annulée avec succès</span>
                        </div>
                    `;
                    
                    document.body.appendChild(notification);
                    setTimeout(() => {
                        notification.classList.add('show');
                    }, 10);
                    
                    setTimeout(() => {
                        notification.classList.remove('show');
                        setTimeout(() => {
                            notification.remove();
                        }, 300);
                    }, 3000);
                });
                
                // Fonction pour fermer la modal
                function closeModal() {
                    modal.classList.remove('show');
                    setTimeout(() => {
                        modal.remove();
                    }, 300);
                }
                
                // Fermer la modal en cliquant en dehors
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        closeModal();
                    }
                });
                
                // Fermer la modal avec Echap
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        closeModal();
                    }
                });
            });
        });
    }
    
    // Fonction pour ajouter les styles nécessaires
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Styles pour les animations de cartes */
            .animate-entry {
                opacity: 0;
                transform: translateY(20px);
                animation: fadeInUp 0.6s forwards;
                animation-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
            }
            
            .opportunity-card {
                transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.3s ease, background-image 0.3s ease !important;
            }
            
            /* Effet ripple pour les boutons */
            .ripple-effect {
                position: relative;
                overflow: hidden;
            }
            
            .ripple {
                position: absolute;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.4);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
                z-index: 1;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            
            /* Styles pour la notification toast */
            .notification-toast {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 15px 20px;
                background-color: var(--success);
                color: white;
                border-radius: 8px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: space-between;
                width: auto;
                max-width: 350px;
                transform: translateY(100px);
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
                z-index: 9999;
            }
            
            .notification-toast.show {
                transform: translateY(0);
                opacity: 1;
            }
            
            .notification-toast.warning {
                background-color: var(--danger);
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .notification-content i {
                font-size: 1.2rem;
            }
            
            .close-notification {
                background: transparent;
                border: none;
                color: white;
                cursor: pointer;
                margin-left: 15px;
                opacity: 0.7;
                transition: opacity 0.3s ease;
            }
            
            .close-notification:hover {
                opacity: 1;
            }
            
            /* Styles pour la modal de confirmation */
            .confirmation-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                z-index: 9999;
            }
            
            .confirmation-modal.show {
                opacity: 1;
                visibility: visible;
            }
            
            .modal-content {
                background-color: white;
                border-radius: 12px;
                width: 90%;
                max-width: 500px;
                box-shadow: 0 15px 30px rgba(0,0,0,0.2);
                transform: scale(0.9);
                transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                overflow: hidden;
            }
            
            .confirmation-modal.show .modal-content {
                transform: scale(1);
            }
            
            .modal-header {
                padding: 15px 20px;
                border-bottom: 1px solid var(--gray-200);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                margin: 0;
                color: var(--primary);
            }
            
            .close-modal {
                background: transparent;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                color: var(--gray-600);
                transition: all 0.3s ease;
            }
            
            .close-modal:hover {
                color: var(--primary);
                transform: rotate(90deg);
            }
            
            .modal-body {
                padding: 20px;
            }
            
            .modal-body p {
                margin-top: 0;
            }
            
            .text-muted {
                color: var(--gray-500);
                font-size: 0.9rem;
            }
            
            .modal-footer {
                padding: 15px 20px;
                border-top: 1px solid var(--gray-200);
                display: flex;
                justify-content: flex-end;
                gap: 10px;
            }
            
            /* Adaptation mode sombre */
            body.dark-mode .notification-toast {
                box-shadow: 0 5px 15px rgba(0,0,0,0.4);
            }
            
            body.dark-mode .modal-content {
                background-color: var(--gray-800);
                box-shadow: 0 15px 30px rgba(0,0,0,0.4);
            }
            
            body.dark-mode .modal-header {
                border-bottom-color: var(--gray-700);
            }
            
            body.dark-mode .modal-header h3 {
                color: var(--primary-light);
            }
            
            body.dark-mode .close-modal {
                color: var(--gray-400);
            }
            
            body.dark-mode .text-muted {
                color: var(--gray-400);
            }
            
            body.dark-mode .modal-footer {
                border-top-color: var(--gray-700);
            }
            
            /* Focus visible pour l'accessibilité */
            .focus-visible-element:focus-visible {
                outline: 3px solid rgba(124, 58, 237, 0.4);
                outline-offset: 2px;
            }
            
            /* Skip to content link */
            .skip-to-content {
                position: absolute;
                top: -40px;
                left: 0;
                padding: 8px 16px;
                background-color: var(--primary);
                color: white;
                font-weight: 600;
                transition: top 0.3s;
                z-index: 10000;
            }
            
            .skip-to-content:focus {
                top: 0;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .notification-toast {
                    bottom: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    // Appliquer toutes les améliorations
    function applyEnhancements() {
        addStyles();
        enhanceCardInteraction();
        enhanceButtonInteraction();
        enhanceSmoothScrolling();
        enhanceKeyboardNavigation();
        enhanceLoadingAnimations();
        enhanceUserFeedback();
    }
    
    // Initialiser après un court délai pour s'assurer que le DOM est complètement prêt
    setTimeout(applyEnhancements, 100);
});
