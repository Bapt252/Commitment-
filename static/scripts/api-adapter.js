/**
 * API Adapter pour permettre de simuler des appels d'API sur GitHub Pages
 * Permet une transition fluide entre l'environnement de démonstration et de production
 */
window.ApiAdapter = (function() {
    // Détection de l'environnement
    const GITHUB_PAGES_MODE = window.location.hostname.includes('github.io') || 
                              window.location.hostname === 'localhost' || 
                              window.location.hostname === '127.0.0.1';
    
    // Configuration API
    const API_BASE_URL = '/api/v1';
    const API_TIMEOUT = 15000; // 15 secondes de timeout pour les appels API
    
    // Stockage des informations de session
    const SESSION_ID = generateSessionId();
    
    console.log(`API Adapter: Initialisation en mode ${GITHUB_PAGES_MODE ? 'GitHub Pages (démo)' : 'Production'}`);
    console.log(`API Adapter: Session ID: ${SESSION_ID}`);
    
    // Méthodes simulées d'API
    const mockApiMethods = {
        // Simuler le parsing d'un CV
        async parseCV(file) {
            console.log("API Adapter: Simulation du parsing de CV", file.name);
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Charger les données mockées
                    const script = document.createElement('script');
                    script.src = "../static/scripts/parsed-data-example.js";
                    script.onload = function() {
                        if (typeof mockParsedData !== 'undefined') {
                            // Générer un ID unique
                            const parsedId = 'mock-' + Date.now();
                            const result = {
                                id: parsedId,
                                status: 'success',
                                ...mockParsedData
                            };
                            // Stocker les données pour une utilisation ultérieure
                            sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
                            sessionStorage.setItem(`parsed_data_${parsedId}`, JSON.stringify(result));
                            resolve(result);
                        } else {
                            resolve({
                                id: null,
                                status: 'error',
                                message: 'Données mockées non disponibles'
                            });
                        }
                    };
                    document.head.appendChild(script);
                }, 2000); // Simuler un délai de traitement
            });
        },
        
        // Récupérer les données parsées par ID
        async getParsedData(id) {
            console.log(`API Adapter: Récupération des données parsées ${id}`);
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Vérifier d'abord les données parsées spécifiques
                    const storedData = sessionStorage.getItem(`parsed_data_${id}`);
                    if (storedData) {
                        const parsedData = JSON.parse(storedData);
                        console.log("API Adapter: Données trouvées pour l'ID:", id);
                        resolve(parsedData);
                        return;
                    }
                    
                    // Ensuite, vérifier les données réelles génériques
                    const realData = sessionStorage.getItem('REAL_CV_DATA');
                    if (realData) {
                        console.log("API Adapter: Données CV réelles trouvées");
                        const data = JSON.parse(realData);
                        resolve({
                            id: id,
                            status: 'success',
                            data: data.data || data,
                            isRealData: true
                        });
                        return;
                    }
                    
                    // Enfin, fallback sur les données génériques
                    const genericData = sessionStorage.getItem('parsedCandidateData');
                    if (genericData) {
                        console.log("API Adapter: Utilisation des données génériques");
                        const data = JSON.parse(genericData);
                        data.isSimulated = true;
                        resolve({
                            id: id,
                            status: 'success',
                            ...data
                        });
                        return;
                    }
                    
                    // Si aucune donnée n'est disponible, charger les données par défaut
                    console.log("API Adapter: Aucune donnée trouvée, chargement des données par défaut");
                    const script = document.createElement('script');
                    script.src = "../static/scripts/parsed-data-example.js";
                    script.onload = function() {
                        if (typeof mockParsedData !== 'undefined') {
                            mockParsedData.isSimulated = true;
                            resolve({
                                id: id,
                                status: 'success',
                                ...mockParsedData
                            });
                        } else {
                            resolve(null);
                        }
                    };
                    document.head.appendChild(script);
                }, 500);
            });
        }
    };
    
    // Génère un ID de session unique
    function generateSessionId() {
        const storedId = sessionStorage.getItem('API_SESSION_ID');
        if (storedId) return storedId;
        
        const newId = Date.now().toString(36) + Math.random().toString(36).substr(2);
        sessionStorage.setItem('API_SESSION_ID', newId);
        return newId;
    }
    
    // Appelle la vraie API ou la version mockée
    async function callApi(method, endpoint, data) {
        // Ajouter des logs pour le debugging
        console.log(`API Adapter: Appel ${method} ${endpoint}`);
        
        try {
            if (GITHUB_PAGES_MODE) {
                // Mode GitHub Pages - utiliser les mocks
                console.log(`API Adapter: Appel API simulé - ${method} ${endpoint}`);
                
                if (endpoint === '/parse' && method === 'POST') {
                    return mockApiMethods.parseCV(data.get('file'));
                }
                
                if (endpoint.startsWith('/parsed_data/') && method === 'GET') {
                    const id = endpoint.split('/').pop();
                    return mockApiMethods.getParsedData(id);
                }
                
                return Promise.reject(new Error(`Endpoint non pris en charge en mode simulé: ${endpoint}`));
            } else {
                // Mode production - appeler la vraie API
                const url = `${API_BASE_URL}${endpoint}`;
                
                const options = {
                    method: method,
                    headers: {
                        'X-Session-ID': SESSION_ID
                    },
                    // Ajouter un timeout pour éviter les requêtes bloquées
                    signal: AbortSignal.timeout(API_TIMEOUT)
                };
                
                if (data) {
                    if (data instanceof FormData) {
                        options.body = data;
                    } else {
                        options.headers['Content-Type'] = 'application/json';
                        options.body = JSON.stringify(data);
                    }
                }
                
                console.log(`API Adapter: Envoi requête à ${url}`);
                const response = await fetch(url, options);
                
                if (!response.ok) {
                    console.error(`API Adapter: Erreur API ${response.status} - ${response.statusText}`);
                    
                    // En cas d'erreur 404, revenir automatiquement au mode simulé
                    if (response.status === 404) {
                        console.warn("API Adapter: Endpoint non trouvé, tentative en mode simulé");
                        
                        if (endpoint.startsWith('/parsed_data/')) {
                            const id = endpoint.split('/').pop();
                            return mockApiMethods.getParsedData(id);
                        }
                    }
                    
                    throw new Error(`API error: ${response.status} ${response.statusText}`);
                }
                
                // Traiter la réponse
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    const responseData = await response.json();
                    console.log("API Adapter: Réponse JSON reçue", responseData);
                    return responseData;
                } else {
                    const textResponse = await response.text();
                    console.log("API Adapter: Réponse texte reçue");
                    return { text: textResponse, status: response.status };
                }
            }
        } catch (error) {
            console.error("API Adapter: Erreur lors de l'appel API", error);
            
            // En cas d'erreur de connexion, essayer de revenir au mode simulé
            if (error.name === 'AbortError' || error.name === 'TypeError' || error.message.includes('Failed to fetch')) {
                console.warn("API Adapter: Erreur réseau, passage en mode simulé");
                
                if (endpoint.startsWith('/parsed_data/')) {
                    const id = endpoint.split('/').pop();
                    return mockApiMethods.getParsedData(id);
                }
            }
            
            throw error;
        }
    }
    
    return {
        get: (endpoint) => callApi('GET', endpoint),
        post: (endpoint, data) => callApi('POST', endpoint, data),
        put: (endpoint, data) => callApi('PUT', endpoint, data),
        delete: (endpoint) => callApi('DELETE', endpoint),
        isGitHubPages: GITHUB_PAGES_MODE,
        sessionId: SESSION_ID
    };
})();
