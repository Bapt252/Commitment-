/**
 * Script pour la connexion entre le backend (parsing CV) et le frontend (formulaire)
 * Ce script vérifie si des données de CV parsées sont disponibles et les applique au formulaire
 * Il ne pré-remplit que si des données réelles existent
 */

(function() {
    console.log("Form-connection: Initialisation du système de connexion backend/frontend");
    
    // Variable pour stocker l'ID des données parsées
    let parsedDataId = null;
    
    // Fonction pour extraire l'ID depuis l'URL
    function getParsedDataIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const id = urlParams.get('parsed_data_id');
        return id;
    }
    
    // Fonction pour charger les données depuis l'API backend
    async function loadParsedDataFromBackend(id) {
        try {
            console.log(`Form-connection: Tentative de récupération des données avec l'ID ${id}`);
            
            // URL de l'API - à adapter selon votre backend
            const apiUrl = `../api/parsed_data/${id}`;
            
            // Appel à l'API
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            // Récupération des données
            const data = await response.json();
            console.log("Form-connection: Données reçues du backend:", data);
            
            return data;
        } catch (error) {
            console.error("Form-connection: Erreur lors de la récupération des données:", error);
            
            // En mode développement, on essaie de récupérer des données depuis sessionStorage
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.includes('github.io')) {
                console.warn("Form-connection: Environnement de développement détecté, tentative de récupération depuis sessionStorage");
                try {
                    const storedData = sessionStorage.getItem('parsedCandidateData');
                    if (storedData) {
                        return JSON.parse(storedData);
                    }
                } catch (storageError) {
                    console.error("Form-connection: Erreur lors de la récupération depuis sessionStorage:", storageError);
                }
            }
            
            return null;
        }
    }
    
    // Fonction pour appliquer les données au formulaire
    function applyDataToForm(data) {
        if (!data || !data.data) {
            console.warn("Form-connection: Données invalides pour le pré-remplissage");
            return;
        }
        
        console.log("Form-connection: Application des données au formulaire");
        
        // Utiliser FormPrefiller si disponible
        if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
            window.FormPrefiller.initialize(data);
            console.log("Form-connection: Données appliquées via FormPrefiller");
        } else {
            console.warn("Form-connection: FormPrefiller non disponible, application manuelle des données");
            applyDataManually(data);
        }
        
        // Afficher une notification si disponible
        if (window.showNotification) {
            window.showNotification("Formulaire pré-rempli avec les données de votre CV", "success");
        }
    }
    
    // Fonction pour appliquer manuellement les données au formulaire si FormPrefiller n'est pas disponible
    function applyDataManually(data) {
        const cvData = data.data;
        
        try {
            // Appliquer les informations personnelles de base
            if (cvData.personal_info) {
                if (cvData.personal_info.name) {
                    fillField('full-name', cvData.personal_info.name);
                }
                
                if (cvData.personal_info.address) {
                    fillField('address', cvData.personal_info.address);
                }
            }
            
            // Appliquer le poste
            if (cvData.position) {
                fillField('job-title', cvData.position);
            }
            
            console.log("Form-connection: Données de base appliquées manuellement");
        } catch (error) {
            console.error("Form-connection: Erreur lors de l'application manuelle des données:", error);
        }
    }
    
    // Fonction utilitaire pour remplir un champ
    function fillField(id, value) {
        const field = document.getElementById(id);
        if (field) {
            field.value = value;
            
            // Déclencher un événement pour activer les validations
            const event = new Event('input', { bubbles: true });
            field.dispatchEvent(event);
            
            console.log(`Form-connection: Champ ${id} rempli avec ${value}`);
        } else {
            console.warn(`Form-connection: Champ ${id} non trouvé`);
        }
    }
    
    // Fonction principale d'initialisation
    async function initialize() {
        // Extraire l'ID des données parsées depuis l'URL
        parsedDataId = getParsedDataIdFromUrl();
        
        if (parsedDataId) {
            console.log(`Form-connection: ID de données parsées trouvé: ${parsedDataId}`);
            
            // Charger les données depuis le backend
            const data = await loadParsedDataFromBackend(parsedDataId);
            
            // Appliquer les données au formulaire si disponibles
            if (data) {
                applyDataToForm(data);
            } else {
                console.warn("Form-connection: Aucune donnée disponible pour cet ID");
            }
        } else {
            console.log("Form-connection: Aucun ID de données parsées dans l'URL, pas de pré-remplissage");
        }
    }
    
    // Exécuter l'initialisation une fois le DOM chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})();