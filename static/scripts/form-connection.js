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
            
            // Vérifier si les données sont déjà en mémoire (priorité absolue)
            const realCvData = sessionStorage.getItem('REAL_CV_DATA');
            if (realCvData) {
                try {
                    const parsedRealData = JSON.parse(realCvData);
                    console.log("Form-connection: Données réelles trouvées dans sessionStorage");
                    // Marquer explicitement que ce sont des données réelles
                    parsedRealData.isRealData = true;
                    parsedRealData.isSimulated = false;
                    return parsedRealData;
                } catch (e) {
                    console.warn("Form-connection: Erreur lors du parsing des données réelles", e);
                }
            }
            
            // Si pas de données en mémoire, on essaie l'API
            try {
                console.log(`Form-connection: Tentative de récupération depuis l'API`);
                
                // Utiliser l'adaptateur API
                if (window.ApiAdapter) {
                    console.log(`Form-connection: Utilisation de l'adaptateur API`);
                    const apiResponse = await window.ApiAdapter.get(`/parsed_data/${id}`);
                    
                    if (apiResponse) {
                        console.log("Form-connection: Données reçues de l'API", apiResponse);
                        
                        // Si ce sont des données réelles, les stocker pour une utilisation future
                        if (!apiResponse.isSimulated) {
                            console.log("Form-connection: Stockage des données réelles");
                            // Stocker les données brutes
                            try {
                                sessionStorage.setItem('REAL_CV_DATA', JSON.stringify(apiResponse.data || apiResponse));
                                sessionStorage.setItem('REAL_CV_DATA_RECEIVED', 'true');
                            } catch (e) {
                                console.warn("Form-connection: Erreur lors du stockage des données", e);
                            }
                        }
                        
                        return apiResponse;
                    }
                }
            } catch (apiError) {
                console.warn("Form-connection: Erreur lors de l'appel API", apiError);
            }
            
            // Si nous sommes en mode démo ou si l'API a échoué
            if (IS_DEMO_ENV) {
                console.warn("Form-connection: Mode démo ou erreur API, tentative avec les données locales");
                
                // 1. D'abord, vérifier si nous avons des données réelles stockées localement
                const realDataKey = `real_parsed_data_${id}`;
                const storedRealData = localStorage.getItem(realDataKey) || sessionStorage.getItem(realDataKey);
                
                if (storedRealData) {
                    console.log("Form-connection: Données réelles trouvées dans le stockage local");
                    return JSON.parse(storedRealData);
                }
                
                // 2. Ensuite, simuler un appel API avec réponse simulée
                return new Promise((resolve) => {
                    setTimeout(() => {
                        // Charger les données mockées depuis sessionStorage
                        const storedData = sessionStorage.getItem('parsedCandidateData');
                        if (storedData) {
                            console.log("Form-connection: Données mockées récupérées avec succès");
                            const data = JSON.parse(storedData);
                            // Ajouter un marqueur de données simulées
                            data.isSimulated = true;
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
                    }, 300);
                });
            }
            
            return null;
        } catch (error) {
            console.error("Form-connection: Erreur lors de la récupération des données:", error);
            return null;
        }
    }
    
    // Fonction pour appliquer les données directement au formulaire
    function applyDirectFormFilling(data) {
        if (!data) return;
        
        console.log("Form-connection: Application directe des données au formulaire", data);
        
        try {
            // Déterminer la structure des données en fonction de la source
            const cvData = data.data || 
                          (data.fullData ? data.fullData.data : null) || 
                          data;
            
            if (!cvData) {
                console.error("Form-connection: Format de données non reconnu");
                return;
            }
            
            // Vérifier si le script de parsing CV a déjà reçu des données réelles
            const realDataFlag = sessionStorage.getItem('REAL_CV_DATA_RECEIVED');
            if (realDataFlag === 'true') {
                console.log("Form-connection: Le script CV-Parser a déjà reçu des données réelles, pas besoin de pré-remplir");
                return;
            }
            
            // Utiliser window.receiveCV pour transmettre les données directement au parser CV
            // Cela garantit que le pré-remplissage passe toujours par le parser CV
            if (window.receiveCV && typeof window.receiveCV === 'function') {
                console.log("Form-connection: Transmission des données au parser CV");
                window.receiveCV(cvData);
                return;
            }
            
            // Fallback: si pour une raison quelconque receiveCV n'est pas disponible
            console.warn("Form-connection: Fonction receiveCV non disponible, pré-remplissage manuel");
            
            // Informations personnelles
            if (cvData.personal_info) {
                if (cvData.personal_info.name) {
                    fillField('full-name', cvData.personal_info.name);
                }
                
                if (cvData.personal_info.address) {
                    fillField('address', cvData.personal_info.address);
                }
            } else if (cvData.name) {
                fillField('full-name', cvData.name);
            }
            
            // Appliquer le poste
            if (cvData.position) {
                fillField('job-title', cvData.position);
            } else if (cvData.current_position) {
                fillField('job-title', cvData.current_position);
            } else if (cvData.jobTitle) {
                fillField('job-title', cvData.jobTitle);
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
        if (document.querySelector('.demo-mode-indicator') || document.querySelector('.real-cv-indicator')) {
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
            
            console.log(`Form-connection: Champ ${id} rempli avec "${value}"`);
        } else {
            console.warn(`Form-connection: Champ ${id} non trouvé`);
        }
    }
    
    // Fonction pour sauvegarder les données parsées dans le stockage local
    function saveRealParsedData(id, data) {
        if (!id || !data) return;
        
        try {
            const storageKey = `real_parsed_data_${id}`;
            
            // Déterminer si ce sont des données réelles ou simulées
            const isRealData = !data.isSimulated;
            
            // Ne stocker que les données réelles
            if (isRealData) {
                console.log(`Form-connection: Sauvegarde des données réelles avec la clé ${storageKey}`);
                
                // Stocker dans sessionStorage (prioritaire)
                sessionStorage.setItem(storageKey, JSON.stringify(data));
                
                // Également dans localStorage pour persistance
                try {
                    localStorage.setItem(storageKey, JSON.stringify(data));
                } catch (e) {
                    console.warn("Form-connection: Impossible de stocker dans localStorage, continuons avec sessionStorage uniquement", e);
                }
                
                // Marquer explicitement que ce sont des données réelles
                if (data.data) {
                    sessionStorage.setItem('REAL_CV_DATA', JSON.stringify(data.data));
                    sessionStorage.setItem('REAL_CV_DATA_RECEIVED', 'true');
                }
                
                console.log(`Form-connection: Données réelles sauvegardées avec la clé ${storageKey}`);
            } else {
                console.log(`Form-connection: Données simulées non sauvegardées en tant que données réelles`);
            }
        } catch (e) {
            console.error("Form-connection: Erreur lors de la sauvegarde des données:", e);
        }
    }
    
    // Fonction principale d'initialisation
    async function initialize() {
        // Extraire l'ID des données parsées depuis l'URL
        parsedDataId = getParsedDataIdFromUrl();
        
        // Si nous avons déjà des données CV réelles, pas besoin de continuer
        const realDataFlag = sessionStorage.getItem('REAL_CV_DATA_RECEIVED');
        if (realDataFlag === 'true') {
            console.log("Form-connection: Données CV réelles déjà disponibles, traitement par CV-parser-integration.js");
            return;
        }
        
        if (parsedDataId) {
            console.log(`Form-connection: ID de données parsées trouvé: ${parsedDataId}`);
            
            // Charger les données depuis le backend
            const data = await loadParsedDataFromBackend(parsedDataId);
            
            // Appliquer les données au formulaire si disponibles
            if (data) {
                // Sauvegarder les données réelles parsées pour utilisation future
                saveRealParsedData(parsedDataId, data);
                
                // Utiliser le pré-remplisseur si disponible
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
            }
        } else {
            console.log("Form-connection: Aucun ID de données parsées dans l'URL, vérification des données locales");
            
            // Vérifier si nous avons des données CV réelles
            const realCvData = sessionStorage.getItem('REAL_CV_DATA');
            if (realCvData) {
                console.log("Form-connection: Données CV réelles trouvées dans sessionStorage");
                return; // Laisser le script cv-parser-integration gérer cela
            }
            
            // Essayons de trouver le dernier ID de données parsées utilisé
            const lastParsedId = sessionStorage.getItem('last_parsed_data_id');
            if (lastParsedId) {
                console.log(`Form-connection: Dernier ID de données trouvé: ${lastParsedId}, tentative de récupération`);
                
                // Chercher des données réelles avec cet ID
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
            }
            
            // Si aucune donnée réelle trouvée, vérifier le sessionStorage pour des données génériques
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
        }
    }
    
    // Exécuter l'initialisation une fois le DOM chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
})();