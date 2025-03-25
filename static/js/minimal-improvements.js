/**
 * Améliorations UI/UX minimalistes pour la page d'opportunités candidat
 * Version JavaScript simple et sûre qui ne risque pas de casser l'affichage
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ajouter le bouton de mode sombre
    addDarkModeToggle();
    
    // Améliorer les interactions des boutons
    enhanceButtonInteractions();
    
    // Améliorer les étapes de recrutement
    enhanceRecruitmentStages();
    
    // Améliorer l'accessibilité
    enhanceAccessibility();
});

/**
 * Ajoute un bouton toggle de mode sombre
 */
function addDarkModeToggle() {
    // Créer le bouton de toggle mode sombre
    const darkModeToggle = document.createElement('button');
    darkModeToggle.className = 'dark-mode-toggle';
    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    darkModeToggle.setAttribute('aria-label', 'Activer le mode sombre');
    
    // Ajouter au header
    const header = document.querySelector('header .container');
    if (header) {
        header.insertBefore(darkModeToggle, header.querySelector('nav'));
    }
    
    // Vérifier les préférences utilisateur
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedMode = localStorage.getItem('darkMode');
    
    // Appliquer le mode sombre si nécessaire
    if (savedMode === 'true' || (savedMode === null && prefersDarkMode)) {
        document.body.classList.add('dark-mode');
        darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // Gérer le clic sur le bouton
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        if (isDarkMode) {
            this.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            this.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        // Sauvegarder la préférence
        localStorage.setItem('darkMode', isDarkMode);
    });
}

/**
 * Améliore les interactions des boutons
 */
function enhanceButtonInteractions() {
    // Améliorer le survol des boutons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseover', function() {
            if (this.classList.contains('btn-primary')) {
                this.style.transform = 'translateY(-2px)';
            } else {
                this.style.transform = 'translateY(-1px)';
            }
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Améliorer le survol des filtres
    document.querySelectorAll('.filter-badge').forEach(badge => {
        badge.addEventListener('mouseover', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(-1px)';
            }
        });
        
        badge.addEventListener('mouseout', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });
}

/**
 * Améliore la visualisation des étapes de recrutement
 */
function enhanceRecruitmentStages() {
    // Mettre en évidence l'étape active
    document.querySelectorAll('.stage.active').forEach(stage => {
        // Créer un effet simple de pulse pour l'étape active
        const icon = stage.querySelector('.stage-icon');
        
        if (icon) {
            // Animation simple de pulse
            setInterval(() => {
                icon.style.transform = 'scale(1.15)';
                
                setTimeout(() => {
                    icon.style.transform = 'scale(1.1)';
                }, 1000);
            }, 2000);
            
            // Mettre en évidence la carte d'interviewer
            const card = stage.querySelector('.interviewer-card');
            if (card) {
                card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
            }
        }
    });
}

/**
 * Améliore l'accessibilité de la page
 */
function enhanceAccessibility() {
    // Ajouter un focus visible aux éléments interactifs
    document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])').forEach(el => {
        el.addEventListener('focus', function() {
            this.style.outline = '3px solid rgba(124, 58, 237, 0.5)';
            this.style.outlineOffset = '2px';
        });
        
        el.addEventListener('blur', function() {
            this.style.outline = 'none';
            this.style.outlineOffset = '0';
        });
    });
    
    // Améliorer le contraste des textes
    document.querySelectorAll('.status-label strong').forEach(el => {
        el.style.color = '#7c3aed';
    });
    
    // Ajouter un attribut ARIA aux éléments interactifs sans label
    document.querySelectorAll('.filter-badge').forEach((badge, index) => {
        if (!badge.getAttribute('aria-label')) {
            const text = badge.textContent.trim();
            badge.setAttribute('aria-label', `Filtre: ${text}`);
        }
    });
}
