/**
 * API Adapter pour permettre de simuler des appels d'API sur GitHub Pages
 * Permet une transition fluide entre l'environnement de démonstration et de production
 */
window.ApiAdapter = (function() {
    const GITHUB_PAGES_MODE = window.location.hostname.includes('github.io') || 
                              window.location.hostname === 'localhost' || 
                              window.location.hostname === '127.0.0.1';
    
    // Méthodes simulées d'API
    const mockApiMethods = {
        // Simuler le parsing d'un CV
        async parseCV(file) {
            console.log("API Adapter: Simulation du parsing de CV", file.name);
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Charger les données mockées
                    const script = document.createElement('script');
                    script.src = "/static/scripts/parsed-data-example.js";
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
                    const storedData = sessionStorage.getItem(`parsed_data_${id}`);
                    if (storedData) {
                        resolve(JSON.parse(storedData));
                    } else {
                        // Fallback sur les données génériques
                        const genericData = sessionStorage.getItem('parsedCandidateData');
                        if (genericData) {
                            resolve(JSON.parse(genericData));
                        } else {
                            resolve(null);
                        }
                    }
                }, 500);
            });
        }
    };
    
    // Appelle la vraie API ou la version mockée
    async function callApi(method, endpoint, data) {
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
            const apiBaseUrl = '/api/v1';
            const url = `${apiBaseUrl}${endpoint}`;
            
            const options = {
                method: method,
                headers: {}
            };
            
            if (data) {
                if (data instanceof FormData) {
                    options.body = data;
                } else {
                    options.headers['Content-Type'] = 'application/json';
                    options.body = JSON.stringify(data);
                }
            }
            
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            return response.json();
        }
    }
    
    return {
        get: (endpoint) => callApi('GET', endpoint),
        post: (endpoint, data) => callApi('POST', endpoint, data),
        isGitHubPages: GITHUB_PAGES_MODE
    };
})();