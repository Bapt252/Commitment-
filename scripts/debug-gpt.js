/**
 * Module d'initialisation du backend GPT Parse Job Posting
 * Ce fichier assure la connexion entre le frontend et l'API de parsing GPT
 */

// Fonction d'initialisation exécutée quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DEBUG-GPT] Initialisation du module de parsing GPT');
    
    // Récupération de l'URL de l'API à partir des paramètres d'URL
    const urlParams = new URLSearchParams(window.location.search);
    let apiUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
    const debugMode = urlParams.has('debug');
    
    // Logs de débogage si le mode debug est activé
    if (debugMode) {
        console.log('[DEBUG-GPT] Mode debug activé');
        console.log('[DEBUG-GPT] API URL:', apiUrl);
    }
    
    // S'assurer que l'API URL est bien formatée
    if (!apiUrl.startsWith('http')) {
        apiUrl = 'http://' + apiUrl;
    }
    
    // Stocker l'URL de l'API pour qu'elle soit accessible globalement
    window.gptApiUrl = apiUrl;
    
    // Enregistrement de l'événement de chargement de page
    logEvent('page_loaded', { page: window.location.pathname });
    
    // Vérification du statut de l'API
    checkApiStatus();
});

/**
 * Vérifie si l'API est accessible
 */
async function checkApiStatus() {
    try {
        const apiUrl = window.gptApiUrl;
        const healthEndpoint = `${apiUrl}/api/health`;
        
        console.log('[DEBUG-GPT] Vérification du statut de l\'API:', healthEndpoint);
        
        const response = await fetch(healthEndpoint, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            },
            signal: AbortSignal.timeout(3000) // Timeout de 3 secondes
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('[DEBUG-GPT] API accessible:', data);
            
            // Déclencher un événement personnalisé pour informer l'application
            const event = new CustomEvent('gptApiReady', { 
                detail: { 
                    url: window.gptApiUrl,
                    status: data
                } 
            });
            window.dispatchEvent(event);
            
            // Afficher un badge de connexion si en mode debug
            if (new URLSearchParams(window.location.search).has('debug')) {
                showApiStatusBadge(true, 'Connexion à l\'API GPT établie');
            }
        } else {
            console.warn('[DEBUG-GPT] API non accessible, statut:', response.status);
            showApiStatusBadge(false, 'API GPT non accessible');
        }
    } catch (error) {
        console.error('[DEBUG-GPT] Erreur lors de la vérification de l\'API:', error);
        showApiStatusBadge(false, `API GPT non accessible: ${error.message}`);
    }
}

/**
 * Affiche un badge de statut de l'API
 * @param {boolean} success - État de la connexion
 * @param {string} message - Message à afficher
 */
function showApiStatusBadge(success, message) {
    // Vérifier si la section de debug existe
    let debugSection = document.getElementById('debug-section');
    if (!debugSection) {
        debugSection = document.createElement('div');
        debugSection.id = 'debug-section';
        debugSection.className = 'debug-section';
        debugSection.style.display = 'block';
        
        // Créer le contenu debug s'il n'existe pas
        let debugContent = document.createElement('div');
        debugContent.id = 'debug-content';
        debugSection.appendChild(debugContent);
        
        // Insérer la section avant le main ou en haut de page
        const mainElement = document.querySelector('main');
        if (mainElement) {
            mainElement.parentNode.insertBefore(debugSection, mainElement);
        } else {
            document.body.insertBefore(debugSection, document.body.firstChild);
        }
    }
    
    // Créer et ajouter le badge
    const badge = document.createElement('div');
    badge.className = `api-status-badge ${success ? 'success' : 'error'}`;
    badge.innerHTML = `
        <i class="fas ${success ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Ajouter le badge à la section debug
    const debugContent = document.getElementById('debug-content');
    if (debugContent) {
        debugContent.appendChild(badge);
    }
    
    // Ajouter du style au badge
    const style = document.createElement('style');
    style.textContent = `
        .api-status-badge {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .api-status-badge.success {
            background-color: #d1fae5;
            color: #065f46;
            border-left: 4px solid #10b981;
        }
        .api-status-badge.error {
            background-color: #fee2e2;
            color: #991b1b;
            border-left: 4px solid #ef4444;
        }
        .api-status-badge i {
            margin-right: 8px;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Enregistre un événement pour le suivi d'utilisation
 * @param {string} eventName - Nom de l'événement
 * @param {Object} eventData - Données associées à l'événement
 */
function logEvent(eventName, eventData = {}) {
    const event = {
        event: eventName,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        ...eventData
    };
    
    console.log('[DEBUG-GPT] Event:', event);
    
    // Si l'API est définie, on peut envoyer l'événement
    if (window.gptApiUrl) {
        fetch(`${window.gptApiUrl}/api/log-event`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(event),
            // Ne pas attendre la réponse pour ne pas bloquer
            keepalive: true
        }).catch(err => console.warn('[DEBUG-GPT] Erreur lors de l\'envoi de l\'événement:', err));
    }
}
