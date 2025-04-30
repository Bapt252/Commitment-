/**
 * Script de pré-remplissage direct du formulaire pour assurer une compatibilité maximale
 * avec GitHub Pages et pour servir de solution de secours si le système principal échoue.
 */

(function() {
    console.log("DirectPrefiller: Initialisation du système de pré-remplissage direct");
    
    // Détecter l'environnement
    const IS_DEMO_ENV = window.location.hostname.includes('github.io') || 
                      window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
    
    // Fonction pour essayer de charger les données depuis différentes sources
    function loadFormData() {
        // D'abord, essayer de récupérer depuis sessionStorage
        try {
            const storedData = sessionStorage.getItem('parsedCandidateData');
            if (storedData) {
                console.log("DirectPrefiller: Données trouvées dans sessionStorage");
                return JSON.parse(storedData);
            }
        } catch (e) {
            console.warn("DirectPrefiller: Erreur lors de l'accès à sessionStorage:", e);
        }
        
        // Si aucune donnée trouvée et en mode démo, charger des données statiques
        if (IS_DEMO_ENV) {
            console.log("DirectPrefiller: Utilisation des données statiques (mode démo)");
            return {
                data: {
                    personal_info: {
                        name: "Thomas Dupont",
                        address: "15 Rue de la République, 75001 Paris"
                    },
                    position: "Développeur Full Stack JavaScript"
                },
                isSimulated: true
            };
        }
        
        return null;
    }
    
    // Fonction pour remplir directement le formulaire
    function applyDirectFormFilling() {
        console.log("DirectPrefiller: Tentative de pré-remplissage direct");
        
        // Charger les données
        const data = loadFormData();
        if (!data) {
            console.warn("DirectPrefiller: Aucune donnée disponible pour le pré-remplissage");
            return;
        }
        
        try {
            // Extraire les données à utiliser
            const cvData = data.data || (data.fullData ? data.fullData.data : null);
            if (!cvData) {
                console.warn("DirectPrefiller: Format de données non reconnu");
                return;
            }
            
            // Pré-remplir les champs de base
            if (cvData.personal_info) {
                // Nom
                if (cvData.personal_info.name) {
                    fillField('full-name', cvData.personal_info.name);
                }
                
                // Adresse
                if (cvData.personal_info.address) {
                    fillField('address', cvData.personal_info.address);
                }
            }
            
            // Poste
            if (cvData.position) {
                fillField('job-title', cvData.position);
            }
            
            // Transport (cocher transport en commun par défaut)
            const publicTransportCheckbox = document.querySelector('input[name="transport-method"][value="public-transport"]');
            if (publicTransportCheckbox) {
                publicTransportCheckbox.checked = true;
                // Déclencher l'événement change
                const event = new Event('change', { bubbles: true });
                publicTransportCheckbox.dispatchEvent(event);
            }
            
            // Ajouter un indicateur pour les données simulées si nécessaire
            if (data.isSimulated || IS_DEMO_ENV) {
                addDemoModeIndicator();
            }
            
            console.log("DirectPrefiller: Pré-remplissage direct terminé avec succès");
            
            // Afficher une notification si la fonction est disponible
            if (window.showNotification) {
                const message = (data.isSimulated || IS_DEMO_ENV) 
                    ? "Formulaire pré-rempli avec des données d'exemple" 
                    : "Formulaire pré-rempli avec vos informations";
                window.showNotification(message, "success");
            }
        } catch (error) {
            console.error("DirectPrefiller: Erreur lors du pré-remplissage:", error);
        }
    }
    
    // Ajouter un indicateur visuel de mode démo
    function addDemoModeIndicator() {
        if (document.querySelector('.demo-mode-indicator')) {
            return; // L'indicateur existe déjà
        }
        
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            const demoIndicator = document.createElement('div');
            demoIndicator.className = 'demo-mode-indicator';
            demoIndicator.innerHTML = '<i class="fas fa-info-circle"></i> Mode démonstration - Données simulées';
            demoIndicator.style.background = 'rgba(124, 58, 237, 0.1)';
            demoIndicator.style.color = 'var(--purple)';
            demoIndicator.style.padding = '12px 16px';
            demoIndicator.style.borderRadius = '8px';
            demoIndicator.style.marginBottom = '20px';
            demoIndicator.style.textAlign = 'center';
            demoIndicator.style.fontWeight = '500';
            formContainer.insertBefore(demoIndicator, formContainer.firstChild);
        }
    }
    
    // Fonction utilitaire pour remplir un champ
    function fillField(id, value) {
        const field = document.getElementById(id);
        if (field) {
            field.value = value;
            
            // Déclencher un événement input pour activer les validations
            const event = new Event('input', { bubbles: true });
            field.dispatchEvent(event);
            
            console.log(`DirectPrefiller: Champ ${id} rempli avec "${value}"`);
        } else {
            console.warn(`DirectPrefiller: Champ ${id} non trouvé dans le DOM`);
        }
    }
    
    // Exécuter le pré-remplissage une fois le DOM chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(applyDirectFormFilling, 500); // Léger délai pour s'assurer que tout est chargé
        });
    } else {
        // Le DOM est déjà chargé
        setTimeout(applyDirectFormFilling, 500);
    }
    
    // Ajouter une vérification supplémentaire lors du chargement complet de la page
    window.addEventListener('load', function() {
        // Vérifier si le formulaire a été rempli
        const fullNameField = document.getElementById('full-name');
        if (fullNameField && !fullNameField.value) {
            console.log("DirectPrefiller: Le formulaire n'a pas été rempli après le chargement, nouvelle tentative");
            applyDirectFormFilling();
        }
    });
    
    // Exposer la fonction pour une utilisation externe
    window.DirectPrefiller = {
        applyFormFilling: applyDirectFormFilling
    };
})();