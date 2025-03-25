/**
 * Version simplifiée des améliorations UI/UX
 * Ce script contient les fonctionnalités essentielles sans les animations complexes
 * qui pourraient causer des problèmes d'affichage
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour améliorer l'interaction avec les boutons
    function enhanceButtonInteraction() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('mouseover', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseout', function() {
                this.style.transform = 'translateY(0)';
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
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // Fonction pour améliorer la navigation avec le clavier
    function enhanceKeyboardNavigation() {
        const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        document.querySelectorAll(focusableElements).forEach(el => {
            el.addEventListener('focus', function() {
                this.style.outline = '3px solid rgba(124, 58, 237, 0.4)';
                this.style.outlineOffset = '2px';
            });
            
            el.addEventListener('blur', function() {
                this.style.outline = 'none';
            });
        });
    }
    
    // Fonction pour ajouter un feedback visuel aux actions utilisateur
    function enhanceUserFeedback() {
        // Améliorer les boutons de sauvegarde
        document.querySelectorAll('.btn-save').forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.closest('.note-input-container').querySelector('input');
                
                if (input.value.trim() !== '') {
                    // Changer l'icône brièvement
                    const originalIcon = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i>';
                    
                    // Afficher un message de succès
                    const message = document.createElement('div');
                    message.textContent = 'Note enregistrée';
                    message.style.position = 'absolute';
                    message.style.right = '40px';
                    message.style.top = '50%';
                    message.style.transform = 'translateY(-50%)';
                    message.style.color = 'green';
                    message.style.fontSize = '0.85rem';
                    message.style.opacity = '0';
                    message.style.transition = 'opacity 0.3s ease';
                    
                    input.parentNode.appendChild(message);
                    
                    // Animer le message
                    setTimeout(() => {
                        message.style.opacity = '1';
                    }, 50);
                    
                    // Restaurer l'icône originale et supprimer le message
                    setTimeout(() => {
                        this.innerHTML = originalIcon;
                        message.style.opacity = '0';
                        setTimeout(() => {
                            message.remove();
                        }, 300);
                    }, 1500);
                }
            });
        });
        
        // Ajouter confirmation simple à l'annulation d'une candidature
        document.querySelectorAll('.btn-outline-danger').forEach(btn => {
            btn.addEventListener('click', function(e) {
                if (!confirm('Êtes-vous sûr de vouloir annuler cette candidature ? Cette action est irréversible.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Fonction pour améliorer les filtres
    function enhanceFilters() {
        document.querySelectorAll('.filter-badge').forEach(badge => {
            badge.addEventListener('mouseover', function() {
                if (!this.classList.contains('active')) {
                    this.style.backgroundColor = '#f0e6ff';
                    this.style.transform = 'translateY(-2px)';
                }
            });
            
            badge.addEventListener('mouseout', function() {
                if (!this.classList.contains('active')) {
                    this.style.backgroundColor = '';
                    this.style.transform = '';
                }
            });
        });
    }
    
    // Ajouter un mode sombre simplifié
    function setupSimpleDarkMode() {
        // Créer le bouton toggle
        const darkModeToggle = document.createElement('button');
        darkModeToggle.className = 'simple-dark-mode-toggle';
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        darkModeToggle.style.background = 'none';
        darkModeToggle.style.border = 'none';
        darkModeToggle.style.fontSize = '1.2rem';
        darkModeToggle.style.color = '#5046E5';
        darkModeToggle.style.cursor = 'pointer';
        darkModeToggle.style.marginRight = '15px';
        darkModeToggle.setAttribute('aria-label', 'Activer le mode sombre');
        
        // Ajouter au header
        const header = document.querySelector('header .container');
        if (header) {
            header.insertBefore(darkModeToggle, header.querySelector('nav'));
        }
        
        // Préférence système
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedMode = localStorage.getItem('darkMode');
        
        // Définir l'état initial
        if (savedMode === 'true' || (savedMode === null && prefersDarkMode)) {
            document.body.classList.add('dark-mode');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            darkModeToggle.style.color = '#f39c12';
        }
        
        // Style pour le mode sombre
        const style = document.createElement('style');
        style.textContent = `
            body.dark-mode {
                background-color: #1a1a2e;
                color: #e6e6e6;
            }
            
            body.dark-mode header {
                background-color: #16213e;
            }
            
            body.dark-mode .candidate-dashboard-section {
                background-color: #16213e;
            }
            
            body.dark-mode .opportunity-card {
                background-color: #1a1a2e;
                border-color: #5046E5;
            }
            
            body.dark-mode .company-name, 
            body.dark-mode .section-heading,
            body.dark-mode .job-title {
                color: #e6e6e6;
            }
            
            body.dark-mode .form-control {
                background-color: #16213e;
                border-color: #444;
                color: #e6e6e6;
            }
            
            body.dark-mode footer {
                background-color: #16213e;
            }
        `;
        document.head.appendChild(style);
        
        // Gérer le toggle
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            
            if (isDarkMode) {
                this.innerHTML = '<i class="fas fa-sun"></i>';
                this.style.color = '#f39c12';
            } else {
                this.innerHTML = '<i class="fas fa-moon"></i>';
                this.style.color = '#5046E5';
            }
            
            localStorage.setItem('darkMode', isDarkMode);
        });
    }
    
    // Appliquer toutes les améliorations
    enhanceButtonInteraction();
    enhanceSmoothScrolling();
    enhanceKeyboardNavigation();
    enhanceUserFeedback();
    enhanceFilters();
    setupSimpleDarkMode();
});
