/**
 * Script pour la connexion entre le backend (parsing CV) et le frontend (formulaire)
 * Ce script vérifie si des données de CV parsées sont disponibles et les applique au formulaire
 * Il utilise l'adaptateur API pour permettre un fonctionnement sur GitHub Pages
 */

(function() {
    console.log("Form-connection: Initialisation du système de connexion backend/frontend");
    
    // Variable pour stocker l'ID des données parsées
    let parsedDataId = null;
    
    // Constante pour la détection de l'environnement
    const IS_DEMO_ENV = window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1' || 
                      window.location.hostname.includes('github.io');
    
    // Fonction pour extraire l'ID depuis l'URL
    function getParsedDataIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const id = urlParams.get('parsed_data_id');
        
        if (id) {
            console.log(`Form-connection: ID de données trouvé dans l'URL: ${id}`);
            // Stocker l'ID pour référence ultérieure
            sessionStorage.setItem('last_parsed_data_id', id);
        }
        
        return id;
    }
    
    // Fonction pour charger les données depuis l'API backend
    async function loadParsedDataFromBackend(id) {
        try {
            console.log(`Form-connection: Tentative de récupération des données avec l'ID ${id}`);
            
            // Code pour l'environnement de production (prioritaire même en démo)
            try {
                console.log(`Form-connection: Tentative de récupération depuis l'API réelle`);
                
                // Utiliser l'adaptateur API si disponible
                if (window.ApiAdapter && !IS_DEMO_ENV) {
                    console.log(`Form-connection: Utilisation de l'adaptateur API réel`);
                    const realData = await window.ApiAdapter.get(`/parsed_data/${id}`);
                    if (realData && !realData.isSimulated) {
                        console.log(`Form-connection: Données réelles récupérées avec succès`);
                        return realData;
                    }
                }
                
                // Si ce n'est pas API Adapter ou si en démo, essayer l'API directe
                const apiUrl = `../api/parsed_data/${id}`;
                const response = await fetch(apiUrl);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log("Form-connection: Données réelles reçues du backend:", data);
                    return data;
                }
            } catch (apiError) {
                console.warn("Form-connection: Erreur lors de l'appel API réel, continuons avec les fallbacks", apiError);
            }
            
            // Si nous sommes sur GitHub Pages ou en dev local ou si l'API réelle a échoué
            if (IS_DEMO_ENV) {
                console.warn("Form-connection: Mode démo, tentative avec les données locales d'abord");
                
                // 1. D'abord, vérifier si nous avons des données réelles stockées localement
                try {
                    const realDataKey = `real_parsed_data_${id}`;
                    const storedRealData = localStorage.getItem(realDataKey) || sessionStorage.getItem(realDataKey);
                    
                    if (storedRealData) {
                        console.log("Form-connection: Données réelles trouvées dans le stockage local");
                        return JSON.parse(storedRealData);
                    }
                } catch (e) {
                    console.warn("Form-connection: Erreur lors de la récupération des données réelles stockées", e);
                }
                
                // 2. Ensuite, simuler un appel API avec réponse simulée
                return new Promise((resolve) => {
                    setTimeout(() => {
                        // Charger les données mockées depuis sessionStorage
                        try {
                            const storedData = sessionStorage.getItem('parsedCandidateData');
                            if (storedData) {
                                console.log("Form-connection: Données mockées récupérées avec succès");
                                const data = JSON.parse(storedData);
                                // Ajouter un marqueur de données simulées
                                if (data && !data.isSimulated) {
                                    data.isSimulated = true;
                                }
                                resolve(data);
                            } else {
                                // Si pas de données, utiliser l'exemple par défaut
                                console.warn("Form-connection: Aucune donnée trouvée, utilisation des données par défaut");
                                // Charger dynamiquement les données par défaut
                                const script = document.createElement('script');
                                script.src = "../static/scripts/parsed-data-example.js";
                                script.onload = function() {
                                    if (typeof mockParsedData !== 'undefined') {
                                        // Ajouter un marqueur de données simulées
                                        mockParsedData.isSimulated = true;
                                        sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
                                        resolve(mockParsedData);
                                    } else {
                                        resolve(null);
                                    }
                                };
                                document.head.appendChild(script);
                            }
                        } catch (error) {
                            console.error("Form-connection: Erreur lors de la récupération des données mockées", error);
                            resolve(null);
                        }
                    }, 500); // Simule un léger délai réseau
                });
            }
            
            return null;
        } catch (error) {
            console.error("Form-connection: Erreur lors de la récupération des données:", error);
            return null;
        }
    }
    
    // Fonction pour appliquer les données directement au formulaire - Approche simplifiée
    function applyDirectFormFilling(data) {
        if (!data) return;
        
        console.log("Form-connection: Application directe des données au formulaire");
        
        try {
            const cvData = data.data || (data.fullData ? data.fullData.data : null);
            
            if (!cvData) {
                console.error("Form-connection: Format de données non reconnu");
                return;
            }
            
            // Informations personnelles
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
            
            // Transport (cocher transport en commun par défaut)
            const publicTransportCheckbox = document.querySelector('input[name="transport-method"][value="public-transport"]');
            if (publicTransportCheckbox) {
                publicTransportCheckbox.checked = true;
                publicTransportCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
            
            // Ajouter indicateur visuel mode démo
            if (data.isSimulated || IS_DEMO_ENV) {
                addDemoModeIndicator();
            }
            
            // Notification
            if (window.showNotification) {
                const message = (data.isSimulated || IS_DEMO_ENV) 
                    ? "Formulaire pré-rempli avec des données d'exemple (mode démo)" 
                    : "Formulaire pré-rempli avec les données de votre CV";
                    
                const type = (data.isSimulated || IS_DEMO_ENV) ? "info" : "success";
                window.showNotification(message, type);
            }
            
            console.log("Form-connection: Données appliquées avec succès");
        } catch (error) {
            console.error("Form-connection: Erreur lors de l'application des données:", error);
        }
    }
    
    // Ajouter un indicateur visuel de mode démo
    function addDemoModeIndicator() {
        // Vérifier si l'indicateur existe déjà
        if (document.querySelector('.demo-mode-indicator')) {
            return;
        }
        
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            const demoIndicator = document.createElement('div');
            demoIndicator.className = 'demo-mode-indicator';
            demoIndicator.innerHTML = '<i class="fas fa-info-circle"></i> Mode démonstration - Données simulées';
            demoIndicator.style.background = 'rgba(124, 58, 237, 0.1)';
            demoIndicator.style.color = 'var(--purple)';
            demoIndicator.style.padding = '8px 12px';
            demoIndicator.style.borderRadius = '4px';
            demoIndicator.style.marginBottom = '15px';
            demoIndicator.style.textAlign = 'center';
            formContainer.insertBefore(demoIndicator, formContainer.firstChild);
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
    
    // Fonction pour sauvegarder les données parsées dans le stockage local
    function saveRealParsedData(id, data) {
        if (!id || !data) return;
        
        try {
            const storageKey = `real_parsed_data_${id}`;
            
            // Stocker dans sessionStorage (prioritaire)
            sessionStorage.setItem(storageKey, JSON.stringify(data));
            
            // Également dans localStorage pour persistance
            try {
                localStorage.setItem(storageKey, JSON.stringify(data));
            } catch (e) {
                console.warn("Impossible de stocker dans localStorage, continuons avec sessionStorage uniquement");
            }
            
            console.log(`Données réelles sauvegardées avec la clé ${storageKey}`);
        } catch (e) {
            console.error("Erreur lors de la sauvegarde des données:", e);
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
                // Sauvegarder les données réelles parsées pour utilisation future
                if (!data.isSimulated) {
                    saveRealParsedData(parsedDataId, data);
                }
                
                if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                    try {
                        console.log("Form-connection: Utilisation du FormPrefiller");
                        window.FormPrefiller.initialize(data);
                    } catch (error) {
                        console.error("Form-connection: Erreur avec FormPrefiller, fallback sur méthode directe", error);
                        applyDirectFormFilling(data);
                    }
                } else {
                    console.log("Form-connection: FormPrefiller non disponible, utilisation de la méthode directe");
                    applyDirectFormFilling(data);
                }
            } else {
                console.warn("Form-connection: Aucune donnée disponible pour cet ID");
                // Ne pas charger les données d'exemple ici, car nous voulons privilégier les données réelles
            }
        } else {
            console.log("Form-connection: Aucun ID de données parsées dans l'URL, vérification des données locales");
            
            // Essayons de trouver le dernier ID de données parsées utilisé
            const lastParsedId = sessionStorage.getItem('last_parsed_data_id');
            if (lastParsedId) {
                console.log(`Form-connection: Dernier ID de données trouvé: ${lastParsedId}, tentative de récupération`);
                
                // Chercher des données réelles avec cet ID
                try {
                    const realDataKey = `real_parsed_data_${lastParsedId}`;
                    const storedRealData = localStorage.getItem(realDataKey) || sessionStorage.getItem(realDataKey);
                    
                    if (storedRealData) {
                        console.log("Form-connection: Données réelles précédentes trouvées, application au formulaire");
                        const realData = JSON.parse(storedRealData);
                        
                        if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                            window.FormPrefiller.initialize(realData);
                        } else {
                            applyDirectFormFilling(realData);
                        }
                        
                        return; // Sortir de la fonction car nous avons appliqué les données
                    }
                } catch (e) {
                    console.warn("Erreur lors de la récupération des données réelles précédentes:", e);
                }
            }
            
            // Si aucune donnée réelle trouvée, vérifier le sessionStorage pour des données génériques
            try {
                const storedData = sessionStorage.getItem('parsedCandidateData');
                if (storedData) {
                    console.log("Form-connection: Données génériques trouvées dans sessionStorage");
                    const data = JSON.parse(storedData);
                    // Marquer comme données simulées
                    data.isSimulated = true;
                    
                    if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                        try {
                            window.FormPrefiller.initialize(data);
                        } catch (error) {
                            console.error("Form-connection: Erreur avec FormPrefiller, fallback sur méthode directe", error);
                            applyDirectFormFilling(data);
                        }
                    } else {
                        applyDirectFormFilling(data);
                    }
                } else if (IS_DEMO_ENV) {
                    // En mode démo, charger directement les données d'exemple
                    console.log("Form-connection: Mode démo, chargement des données d'exemple");
                    
                    // Attente pour s'assurer que le DOM est prêt
                    setTimeout(function() {
                        const script = document.createElement('script');
                        script.src = "../static/scripts/parsed-data-example.js";
                        document.head.appendChild(script);
                    }, 500);
                } else {
                    console.log("Form-connection: Aucune donnée trouvée, pas de pré-remplissage");
                }
            } catch (error) {
                console.error("Form-connection: Erreur lors de la récupération des données locales:", error);
            }
        }
    }
    
    // Exécuter l'initialisation une fois le DOM chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})();