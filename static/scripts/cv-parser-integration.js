/**
 * CV PARSER INTEGRATION SCRIPT
 * 
 * Ce script est le SEUL point d'entrée pour les données de CV parsées.
 * Il a priorité absolue sur tous les autres scripts de pré-remplissage.
 */

// Fonction globale pour recevoir les données de CV
window.receiveCV = function(cvData) {
    console.log("CV PARSER INTEGRATION: Données de CV reçues", cvData);
    
    if (!cvData) {
        console.error("CV PARSER INTEGRATION: Données CV invalides");
        return false;
    }
    
    try {
        // 1. ÉTAPE CRITIQUE: Marquer explicitement que nous avons reçu des données réelles
        sessionStorage.setItem('REAL_CV_DATA_RECEIVED', 'true');
        
        // 2. Stocker les données brutes
        sessionStorage.setItem('REAL_CV_DATA', JSON.stringify(cvData));
        
        // 3. Application immédiate des données au formulaire (sans attendre)
        return applyCVData(cvData);
    } catch (error) {
        console.error("CV PARSER INTEGRATION: Erreur lors du traitement", error);
        return false;
    }
};

// Fonction d'application directe des données au formulaire
function applyCVData(cvData) {
    // Extraire les données selon différents formats possibles
    const data = cvData.data || cvData.fullData || cvData;
    
    try {
        // DONNÉES PERSONNELLES
        if (data.personal_info && data.personal_info.name) {
            fillField('full-name', data.personal_info.name);
        } else if (data.name) {
            fillField('full-name', data.name);
        }
        
        // POSTE
        if (data.position) {
            fillField('job-title', data.position);
        } else if (data.current_position) {
            fillField('job-title', data.current_position);
        } else if (data.jobTitle) {
            fillField('job-title', data.jobTitle);
        }
        
        // ADRESSE
        if (data.personal_info && data.personal_info.address) {
            fillField('address', data.personal_info.address);
        } else if (data.address) {
            fillField('address', data.address);
        }
        
        // Mode transport par défaut
        const publicTransportCheckbox = document.querySelector('input[name="transport-method"][value="public-transport"]');
        if (publicTransportCheckbox) {
            publicTransportCheckbox.checked = true;
            // Déclencher événement
            const event = new Event('change', { bubbles: true });
            publicTransportCheckbox.dispatchEvent(event);
        }
        
        // Ajouter indicateur visuel
        addRealCVIndicator();
        
        console.log("CV PARSER INTEGRATION: Formulaire pré-rempli avec succès");
        return true;
    } catch (error) {
        console.error("CV PARSER INTEGRATION: Erreur lors du pré-remplissage", error);
        return false;
    }
}

// Utilitaire pour remplir un champ
function fillField(id, value) {
    if (!value) return;
    
    const field = document.getElementById(id);
    if (field) {
        field.value = value;
        // Déclencher un événement input pour activer validations
        const event = new Event('input', { bubbles: true });
        field.dispatchEvent(event);
        
        // Ajouter classe spéciale pour indiquer données réelles
        field.classList.add('real-cv-data');
        
        console.log(`CV PARSER INTEGRATION: Champ ${id} rempli avec "${value}"`);
    }
}

// Ajouter un indicateur visuel de CV parsé
function addRealCVIndicator() {
    // Supprimer tout indicateur de démo existant
    const demoIndicator = document.querySelector('.demo-mode-indicator');
    if (demoIndicator) {
        demoIndicator.remove();
    }
    
    // Chercher un indicateur existant
    if (document.querySelector('.real-cv-indicator')) {
        return; // Déjà présent
    }
    
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
        const indicator = document.createElement('div');
        indicator.className = 'real-cv-indicator';
        indicator.innerHTML = '<i class="fas fa-check-circle"></i> <strong>CV PARSÉ AVEC SUCCÈS</strong> - Formulaire pré-rempli avec vos données';
        indicator.style.background = 'rgba(16, 185, 129, 0.1)';
        indicator.style.color = '#10B981';
        indicator.style.padding = '12px 16px';
        indicator.style.borderRadius = '8px';
        indicator.style.marginBottom = '20px';
        indicator.style.textAlign = 'center';
        indicator.style.fontWeight = '500';
        indicator.style.border = '2px solid #10B981';
        indicator.style.animation = 'pulseCVIndicator 2s infinite';
        
        // Ajouter style d'animation si nécessaire
        if (!document.getElementById('cv-indicator-style')) {
            const style = document.createElement('style');
            style.id = 'cv-indicator-style';
            style.textContent = `
                @keyframes pulseCVIndicator {
                    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
                    70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
                }
                .real-cv-data {
                    background-color: rgba(16, 185, 129, 0.05) !important;
                    border-color: #10B981 !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        formContainer.insertBefore(indicator, formContainer.firstChild);
        
        // Notification
        if (window.showNotification) {
            window.showNotification("Formulaire pré-rempli avec les données de votre CV", "success");
        }
    }
}

// Vérifier au chargement si des données CV réelles sont disponibles
document.addEventListener('DOMContentLoaded', function() {
    console.log("CV PARSER INTEGRATION: Vérification des données au chargement");
    
    // Vérifier si des données sont disponibles
    const realDataFlag = sessionStorage.getItem('REAL_CV_DATA_RECEIVED');
    if (realDataFlag === 'true') {
        try {
            const storedData = sessionStorage.getItem('REAL_CV_DATA');
            if (storedData) {
                console.log("CV PARSER INTEGRATION: Données réelles trouvées, application");
                const data = JSON.parse(storedData);
                applyCVData(data);
            }
        } catch (e) {
            console.warn("CV PARSER INTEGRATION: Erreur lors de la récupération des données", e);
        }
    } else {
        console.log("CV PARSER INTEGRATION: Pas de données CV réelles disponibles");
    }
});

console.log("CV PARSER INTEGRATION: Script chargé et prêt à recevoir des données");
