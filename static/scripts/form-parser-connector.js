/**
 * Script de connexion spécifique pour intégrer les données parsées d'un CV
 * directement avec le formulaire. Ce script sert de pont entre le système 
 * de parsing de CV et l'interface utilisateur du formulaire candidat.
 */

(function() {
    console.log("FormParserConnector: Initialisation du connecteur de parsing");
    
    // Fonction pour recevoir les données de parsing et les injecter dans le formulaire
    window.receiveParsingData = function(parsedData) {
        if (!parsedData || typeof parsedData !== 'object') {
            console.error("FormParserConnector: Données invalides reçues", parsedData);
            return false;
        }
        
        try {
            console.log("FormParserConnector: Données de parsing reçues", parsedData);
            
            // 1. Stocker les données brutes pour utilisation ultérieure
            const storageKey = `parsed_data_${Date.now()}`;
            sessionStorage.setItem(storageKey, JSON.stringify(parsedData));
            localStorage.setItem(storageKey, JSON.stringify(parsedData));
            
            // 2. Stocker également avec une clé fixe pour faciliter la récupération
            sessionStorage.setItem('latest_real_parsed_data', JSON.stringify(parsedData));
            
            // 3. Signal visuel que les données ont été reçues
            addParsingCompletedIndicator();
            
            // 4. Tentative directe d'application au formulaire
            if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                try {
                    console.log("FormParserConnector: Utilisation du FormPrefiller");
                    window.FormPrefiller.initialize(parsedData);
                    return true;
                } catch (prefillError) {
                    console.error("FormParserConnector: Erreur avec FormPrefiller, tentative avec méthode directe", prefillError);
                }
            }
            
            // 5. Méthode directe en cas d'échec de FormPrefiller
            return applyParsedDataDirectly(parsedData);
            
        } catch (error) {
            console.error("FormParserConnector: Erreur lors du traitement des données", error);
            return false;
        }
    };
    
    // Fonction pour appliquer directement les données au formulaire
    function applyParsedDataDirectly(data) {
        try {
            console.log("FormParserConnector: Application directe des données au formulaire");
            
            // Extraire les données à utiliser
            const cvData = data.data || (data.fullData ? data.fullData.data : null) || data;
            
            // Nom et prénom
            if (cvData.personal_info && cvData.personal_info.name) {
                fillField('full-name', cvData.personal_info.name);
            } else if (cvData.name) {
                fillField('full-name', cvData.name);
            }
            
            // Poste souhaité 
            if (cvData.position) {
                fillField('job-title', cvData.position);
            } else if (cvData.current_position) {
                fillField('job-title', cvData.current_position);
            } else if (cvData.jobTitle) {
                fillField('job-title', cvData.jobTitle);
            }
            
            // Adresse
            if (cvData.personal_info && cvData.personal_info.address) {
                fillField('address', cvData.personal_info.address);
            } else if (cvData.address) {
                fillField('address', cvData.address);
            }
            
            // Notification du succès
            if (window.showNotification) {
                window.showNotification("Formulaire pré-rempli avec les données de votre CV", "success");
            }
            
            console.log("FormParserConnector: Pré-remplissage direct terminé avec succès");
            return true;
        } catch (error) {
            console.error("FormParserConnector: Erreur lors de l'application directe des données", error);
            return false;
        }
    }
    
    // Fonction pour ajouter un indicateur visuel de réussite du parsing
    function addParsingCompletedIndicator() {
        const formContainer = document.querySelector('.form-container');
        if (!formContainer) return;
        
        // Supprimer tout indicateur de démo existant
        const demoIndicator = document.querySelector('.demo-mode-indicator');
        if (demoIndicator) {
            demoIndicator.remove();
        }
        
        // Créer l'indicateur de parsing réussi
        const parseIndicator = document.createElement('div');
        parseIndicator.className = 'parsing-success-indicator';
        parseIndicator.innerHTML = '<i class="fas fa-check-circle"></i> CV parsé avec succès - Formulaire pré-rempli';
        parseIndicator.style.background = 'rgba(16, 185, 129, 0.1)';
        parseIndicator.style.color = '#10B981';
        parseIndicator.style.padding = '12px 16px';
        parseIndicator.style.borderRadius = '8px';
        parseIndicator.style.marginBottom = '20px';
        parseIndicator.style.textAlign = 'center';
        parseIndicator.style.fontWeight = '500';
        
        formContainer.insertBefore(parseIndicator, formContainer.firstChild);
    }
    
    // Fonction utilitaire pour remplir un champ de formulaire
    function fillField(id, value) {
        if (!value) return;
        
        const field = document.getElementById(id);
        if (field) {
            field.value = value;
            
            // Déclencher un événement pour activer les validations
            const event = new Event('input', { bubbles: true });
            field.dispatchEvent(event);
            
            console.log(`FormParserConnector: Champ ${id} rempli avec "${value}"`);
        }
    }
    
    // Vérifier au chargement s'il y a des données récemment parsées à appliquer
    document.addEventListener('DOMContentLoaded', function() {
        try {
            // Priorité aux dernières données réelles
            const latestRealData = sessionStorage.getItem('latest_real_parsed_data');
            if (latestRealData) {
                console.log("FormParserConnector: Données réelles récentes trouvées");
                const data = JSON.parse(latestRealData);
                window.receiveParsingData(data);
            }
        } catch (e) {
            console.warn("FormParserConnector: Erreur lors de la vérification des données récentes", e);
        }
    });
    
    console.log("FormParserConnector: Connecteur initialisé et prêt à recevoir des données");
})();