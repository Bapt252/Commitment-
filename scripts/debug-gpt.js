/**
 * debug-gpt.js
 * Script auxiliaire pour le débogage du système de parsing GPT
 */

// Configuration de débogage
const DEBUG_GPT_CONFIG = {
    enabled: false,
    logLevel: 'info' // 'error', 'info', 'debug'
};

// Fonction pour activer le débogage
function enableGptDebugMode() {
    DEBUG_GPT_CONFIG.enabled = true;
    
    // Créer ou obtenir la section de débogage
    let debugSection = document.getElementById('debug-section');
    
    // Si la section n'existe pas, la créer
    if (!debugSection) {
        debugSection = document.createElement('div');
        debugSection.id = 'debug-section';
        debugSection.className = 'debug-section';
        
        const heading = document.createElement('h3');
        heading.textContent = 'Informations de débogage GPT';
        
        const content = document.createElement('div');
        content.id = 'debug-content';
        
        debugSection.appendChild(heading);
        debugSection.appendChild(content);
        
        // Insérer la section après le header s'il existe, sinon au début du document
        const header = document.querySelector('header');
        if (header && header.parentNode) {
            header.parentNode.insertBefore(debugSection, header.nextSibling);
        } else {
            document.body.insertBefore(debugSection, document.body.firstChild);
        }
    }
    
    // Afficher la section
    debugSection.style.display = 'block';
    
    // Ajouter un premier message
    logDebugMessage('Mode débogage GPT activé');
    
    // Rediriger les erreurs console vers la section de débogage
    const originalConsoleError = console.error;
    console.error = function() {
        originalConsoleError.apply(console, arguments);
        const errorMessage = Array.from(arguments).join(' ');
        logDebugMessage(`ERREUR: ${errorMessage}`, 'error');
    };
    
    // Rediriger les logs console vers la section de débogage si niveau debug
    if (DEBUG_GPT_CONFIG.logLevel === 'debug') {
        const originalConsoleLog = console.log;
        console.log = function() {
            originalConsoleLog.apply(console, arguments);
            const logMessage = Array.from(arguments).join(' ');
            logDebugMessage(`LOG: ${logMessage}`, 'debug');
        };
    }
    
    return true;
}

// Fonction pour désactiver le débogage
function disableGptDebugMode() {
    DEBUG_GPT_CONFIG.enabled = false;
    
    // Masquer la section de débogage
    const debugSection = document.getElementById('debug-section');
    if (debugSection) {
        debugSection.style.display = 'none';
    }
    
    return true;
}

// Fonction pour journaliser un message de débogage
function logDebugMessage(message, level = 'info') {
    // Vérifier si le débogage est activé
    if (!DEBUG_GPT_CONFIG.enabled) return;
    
    // Vérifier si le niveau de log est suffisant
    const levels = { 'error': 3, 'info': 2, 'debug': 1 };
    const configLevel = levels[DEBUG_GPT_CONFIG.logLevel] || 2;
    const messageLevel = levels[level] || 2;
    
    if (messageLevel < configLevel) return;
    
    // Obtenir le conteneur de débogage
    const debugContent = document.getElementById('debug-content');
    if (!debugContent) return;
    
    // Créer l'élément de message
    const messageElement = document.createElement('p');
    messageElement.className = `debug-message debug-${level}`;
    
    // Ajouter un timestamp
    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${now.getMilliseconds().toString().padStart(3, '0')}`;
    
    // Formater le message
    messageElement.innerHTML = `<span class="debug-timestamp">[${timestamp}]</span> ${message}`;
    
    // Ajouter une classe de couleur selon le niveau
    if (level === 'error') {
        messageElement.style.color = '#e74c3c';
    } else if (level === 'debug') {
        messageElement.style.color = '#7f8c8d';
    }
    
    // Ajouter le message au conteneur
    debugContent.appendChild(messageElement);
    
    // Faire défiler vers le bas
    debugContent.scrollTop = debugContent.scrollHeight;
}

// Fonction pour effacer les messages de débogage
function clearGptDebugMessages() {
    const debugContent = document.getElementById('debug-content');
    if (debugContent) {
        debugContent.innerHTML = '';
    }
}

// Fonction pour journaliser des informations sur l'API
function logApiCall(url, data, response) {
    if (!DEBUG_GPT_CONFIG.enabled) return;
    
    logDebugMessage(`API Call: ${url}`, 'info');
    
    if (data) {
        if (typeof data === 'object') {
            logDebugMessage(`Request Data: ${JSON.stringify(data)}`, 'debug');
        } else {
            logDebugMessage(`Request Data: ${data}`, 'debug');
        }
    }
    
    if (response) {
        if (typeof response === 'object') {
            try {
                logDebugMessage(`Response: ${JSON.stringify(response)}`, 'debug');
            } catch (e) {
                logDebugMessage(`Response: [Object cannot be stringified]`, 'debug');
            }
        } else {
            logDebugMessage(`Response: ${response}`, 'debug');
        }
    }
}

// Vérifier automatiquement les paramètres d'URL au chargement
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Activer le débogage si le paramètre est présent
    if (urlParams.has('debug')) {
        enableGptDebugMode();
        
        // Configurer le niveau de log
        if (urlParams.has('logLevel')) {
            const level = urlParams.get('logLevel');
            if (['error', 'info', 'debug'].includes(level)) {
                DEBUG_GPT_CONFIG.logLevel = level;
                logDebugMessage(`Niveau de log défini sur: ${level}`);
            }
        }
        
        // Ajouter quelques informations utiles
        const apiUrl = urlParams.get('apiUrl') || 'Default API URL';
        logDebugMessage(`URL de l'API GPT configurée: ${apiUrl}`);
        
        // Vérifier si sessionStorage contient des données de parsing
        const parsedJobData = sessionStorage.getItem('parsedJobData');
        if (parsedJobData) {
            logDebugMessage('Données de parsing trouvées dans sessionStorage');
        } else {
            logDebugMessage('Aucune donnée de parsing trouvée dans sessionStorage');
        }
    }
    
    // Exposer les fonctions de débogage globalement
    window.gptDebug = {
        enable: enableGptDebugMode,
        disable: disableGptDebugMode,
        log: logDebugMessage,
        clear: clearGptDebugMessages,
        logApi: logApiCall
    };
});