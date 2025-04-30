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
        
        // Vérifier si nous sommes sur GitHub Pages (ou en développement local)
        if (IS_DEMO_ENV) {
            // En mode démo, stocker un identifiant factice si présent
            if (id) {
                sessionStorage.setItem('last_parsed_data_id', id);
            }
        }
        
        return id;
    }
    
    // Fonction pour charger les données depuis l'API backend
    async function loadParsedDataFromBackend(id) {
        try {
            console.log(`Form-connection: Tentative de récupération des données avec l'ID ${id}`);
            
            // Utiliser l'adaptateur API si disponible
            if (window.ApiAdapter) {
                console.log(`Form-connection: Utilisation de l'adaptateur API`);
                return await window.ApiAdapter.get(`/parsed_data/${id}`);
            }
            
            // Vérifier si nous sommes sur GitHub Pages ou en dev local
            if (IS_DEMO_ENV) {
                console.warn("Form-connection: Environnement de démonstration détecté");
                
                // Simuler un appel API avec réponse simulée
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
            
            // Code pour l'environnement de production
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
            if (IS_DEMO_ENV) {
                console.warn("Form-connection: Environnement de développement détecté, tentative de récupération depuis sessionStorage");
                try {
                    const storedData = sessionStorage.getItem('parsedCandidateData');
                    if (storedData) {
                        const data = JSON.parse(storedData);
                        // Ajouter un marqueur de données simulées
                        if (data && !data.isSimulated) {
                            data.isSimulated = true;
                        }
                        return data;
                    }
                } catch (storageError) {
                    console.error("Form-connection: Erreur lors de la récupération depuis sessionStorage:", storageError);
                }
            }
            
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
                
                // En mode démo, charger les données d'exemple
                if (IS_DEMO_ENV) {
                    console.log("Form-connection: Mode démo, chargement des données d'exemple");
                    
                    // Attente pour s'assurer que le DOM est prêt
                    setTimeout(function() {
                        const script = document.createElement('script');
                        script.src = "../static/scripts/parsed-data-example.js";
                        document.head.appendChild(script);
                    }, 500);
                }
            }
        } else {
            console.log("Form-connection: Aucun ID de données parsées dans l'URL, vérification des données locales");
            
            // Vérifier si des données sont disponibles dans le sessionStorage
            try {
                const storedData = sessionStorage.getItem('parsedCandidateData');
                if (storedData) {
                    console.log("Form-connection: Données trouvées dans sessionStorage");
                    const data = JSON.parse(storedData);
                    // Marquer comme données simulées si en mode démo
                    if (IS_DEMO_ENV && !data.isSimulated) {
                        data.isSimulated = true;
                    }
                    
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