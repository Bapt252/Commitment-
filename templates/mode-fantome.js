/**
 * Script pour le mode fantôme - Commitment Project
 * Gère les fonctionnalités liées au mode fantôme sur le tableau de bord candidat
 */

// Fonction pour afficher la popup d'info
function showGhostInfo() {
    console.log("Fonction showGhostInfo() appelée");
    var popup = document.getElementById('ghost-popup');
    if (popup) {
        popup.style.display = 'flex';
        setTimeout(function() {
            popup.classList.add('active');
            document.body.style.overflow = 'hidden';
        }, 10);
    }
    return false;
}

// Fonction pour fermer la popup
function closeGhostPopup() {
    var popup = document.getElementById('ghost-popup');
    if (popup) {
        popup.classList.remove('active');
        setTimeout(function() {
            popup.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }
}

// Fonction pour activer le mode fantôme
function enableGhostMode(showNotification) {
    showNotification = showNotification !== false; // Par défaut à true
    var ghostToggle = document.getElementById('ghost-mode-toggle');
    var ghostBadge = document.getElementById('ghost-badge');
    var profilePhoto = document.querySelector('.profile-photo');
    
    if (ghostToggle) ghostToggle.checked = true;
    if (ghostBadge) ghostBadge.style.display = 'flex';
    
    if (profilePhoto) {
        profilePhoto.classList.add('ghost-active');
    }
    
    localStorage.setItem('ghostModeEnabled', 'true');
    
    if (showNotification) {
        showToast(
            'Mode fantôme activé', 
            'Votre profil est invisible aux recruteurs de vos entreprises actuelles et passées.'
        );
    }
}

// Fonction pour désactiver le mode fantôme
function disableGhostMode() {
    var ghostToggle = document.getElementById('ghost-mode-toggle');
    var ghostBadge = document.getElementById('ghost-badge');
    var profilePhoto = document.querySelector('.profile-photo');
    
    if (ghostToggle) ghostToggle.checked = false;
    if (ghostBadge) ghostBadge.style.display = 'none';
    
    if (profilePhoto) {
        profilePhoto.classList.remove('ghost-active');
    }
    
    localStorage.setItem('ghostModeEnabled', 'false');
    
    showToast(
        'Mode fantôme désactivé', 
        'Votre profil est à nouveau visible à tous les recruteurs.'
    );
}

// Fonction pour afficher un toast
function showToast(title, message, duration) {
    duration = duration || 5000;
    var ghostToast = document.getElementById('ghost-toast');
    var ghostToastTitle = document.getElementById('ghost-toast-title');
    var ghostToastText = document.getElementById('ghost-toast-text');
    
    if (ghostToast && ghostToastTitle && ghostToastText) {
        ghostToastTitle.textContent = title;
        ghostToastText.textContent = message;
        ghostToast.style.display = 'block';
        
        setTimeout(function() {
            ghostToast.classList.add('active');
        }, 10);
        
        setTimeout(function() {
            ghostToast.classList.remove('active');
            setTimeout(function() {
                ghostToast.style.display = 'none';
            }, 300);
        }, duration);
    }
}

// Initialisation lors du chargement du document
document.addEventListener('DOMContentLoaded', function() {
    // Attacher l'événement clic au bouton d'info
    var infoButton = document.getElementById('ghost-info-trigger');
    if (infoButton) {
        console.log('Bouton info trouvé, ajout du gestionnaire');
        infoButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Bouton info cliqué');
            showGhostInfo();
            return false;
        });
    }
    
    // Vérifier l'état du mode fantôme au chargement
    var ghostModeEnabled = localStorage.getItem('ghostModeEnabled') === 'true';
    if (ghostModeEnabled) {
        enableGhostMode(false); // Activer sans notification
    }
    
    // Attacher les autres événements
    var ghostModeToggle = document.getElementById('ghost-mode-toggle');
    if (ghostModeToggle) {
        ghostModeToggle.addEventListener('change', function() {
            if (this.checked) {
                enableGhostMode();
            } else {
                disableGhostMode();
            }
        });
    }
    
    var closeButton = document.getElementById('ghost-popup-close');
    if (closeButton) {
        closeButton.addEventListener('click', closeGhostPopup);
    }
    
    var activateButton = document.getElementById('activate-ghost-mode');
    if (activateButton) {
        activateButton.addEventListener('click', function() {
            enableGhostMode();
            closeGhostPopup();
        });
    }
    
    var laterButton = document.getElementById('ghost-popup-later');
    if (laterButton) {
        laterButton.addEventListener('click', closeGhostPopup);
    }
    
    var toastCloseButton = document.getElementById('ghost-toast-close');
    if (toastCloseButton) {
        toastCloseButton.addEventListener('click', function() {
            var ghostToast = document.getElementById('ghost-toast');
            if (ghostToast) {
                ghostToast.classList.remove('active');
                setTimeout(function() {
                    ghostToast.style.display = 'none';
                }, 300);
            }
        });
    }
});

// Exposer les fonctions globalement après leur définition
window.showGhostInfo = showGhostInfo;
window.closeGhostPopup = closeGhostPopup;
window.enableGhostMode = enableGhostMode;
window.disableGhostMode = disableGhostMode;
window.showToast = showToast;