/**
 * Cache Buster pour JobParserAPI v2.5
 * Ce script force le rechargement de la nouvelle version de l'API en cas de problème de cache
 */

(function() {
    'use strict';
    
    const EXPECTED_VERSION = 'v2.5';
    const CACHE_BUST_KEY = 'jobParserApiVersion';
    
    // Fonction pour vérifier et forcer le rechargement si nécessaire
    function checkAndBustCache() {
        console.log('🔍 Vérification de la version JobParserAPI...');
        
        // Vérifier si JobParserAPI est disponible
        if (typeof window.JobParserAPI !== 'function') {
            console.warn('❌ JobParserAPI non trouvée, rechargement de la page...');
            reloadPage();
            return;
        }
        
        // Créer une instance temporaire pour vérifier la version
        try {
            const testInstance = new window.JobParserAPI({ debug: true });
            
            // Vérifier les logs de console pour la version
            const currentVersion = getCurrentVersion();
            const lastKnownVersion = localStorage.getItem(CACHE_BUST_KEY);
            
            console.log('📋 Version actuelle détectée:', currentVersion);
            console.log('📋 Dernière version connue:', lastKnownVersion);
            
            if (currentVersion !== EXPECTED_VERSION || lastKnownVersion !== EXPECTED_VERSION) {
                console.log('🔄 Mise à jour détectée, nettoyage du cache...');
                bustCache();
            } else {
                console.log('✅ Version à jour détectée');
                localStorage.setItem(CACHE_BUST_KEY, EXPECTED_VERSION);
            }
            
        } catch (error) {
            console.error('❌ Erreur lors de la vérification de version:', error);
            bustCache();
        }
    }
    
    // Fonction pour déterminer la version actuelle
    function getCurrentVersion() {
        // Chercher dans les logs de console ou dans le code
        const scripts = document.querySelectorAll('script[src*="job-parser-api.js"]');
        
        // Vérifier les messages de console récents
        if (window.console && window.console.log) {
            // Cette méthode est limitée car on ne peut pas lire l'historique de console
            // Mais on peut vérifier les caractéristiques de l'API
            
            if (window.JobParserAPI) {
                const prototype = window.JobParserAPI.prototype;
                
                // Vérifier la présence de méthodes spécifiques à v2.5
                if (prototype.extractJobTitle && 
                    prototype.segmentJobText && 
                    prototype.analyzeJobLocally) {
                    
                    // Vérifier le contenu de la fonction extractJobTitle pour v2.5
                    const extractTitleString = prototype.extractJobTitle.toString();
                    if (extractTitleString.includes('Ultra-enhanced title extraction v2.5')) {
                        return 'v2.5';
                    }
                    if (extractTitleString.includes('Enhanced title extraction v2.4')) {
                        return 'v2.4';
                    }
                }
            }
        }
        
        return 'unknown';
    }
    
    // Fonction pour nettoyer le cache
    function bustCache() {
        console.log('🧹 Nettoyage du cache en cours...');
        
        // Nettoyer le localStorage spécifique à l'application
        const keysToRemove = ['jobParserApiVersion', 'parsedJobData', 'clientFormData'];
        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
        });
        
        // Forcer un rechargement dur de la page avec cache busting
        const timestamp = Date.now();
        const currentUrl = window.location.href;
        const separator = currentUrl.includes('?') ? '&' : '?';
        const newUrl = `${currentUrl}${separator}_cacheBust=${timestamp}`;
        
        console.log('🔄 Rechargement forcé de la page...');
        window.location.href = newUrl;
    }
    
    // Fonction pour recharger la page
    function reloadPage() {
        console.log('🔄 Rechargement de la page...');
        window.location.reload(true); // Force reload
    }
    
    // Fonction pour afficher des informations de debug
    function showDebugInfo() {
        const debugSection = document.getElementById('debug-section');
        const debugContent = document.getElementById('debug-content');
        
        if (debugSection && debugContent) {
            const info = {
                version: getCurrentVersion(),
                apiAvailable: typeof window.JobParserAPI === 'function',
                cacheTimestamp: localStorage.getItem(CACHE_BUST_KEY),
                userAgent: navigator.userAgent.slice(0, 50) + '...'
            };
            
            debugContent.innerHTML = `
                <p><strong>Version JobParserAPI:</strong> ${info.version}</p>
                <p><strong>API disponible:</strong> ${info.apiAvailable ? 'Oui' : 'Non'}</p>
                <p><strong>Cache timestamp:</strong> ${info.cacheTimestamp || 'Non défini'}</p>
                <p><strong>User Agent:</strong> ${info.userAgent}</p>
                <button onclick="window.CacheBuster.forceBustCache()" style="margin-top: 10px; padding: 5px 10px; background: #ff6b6b; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    🔄 Forcer le rechargement
                </button>
            `;
            
            debugSection.style.display = 'block';
        }
    }
    
    // Attendre que le DOM soit prêt
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkAndBustCache);
        } else {
            // DOM déjà prêt
            setTimeout(checkAndBustCache, 100);
        }
        
        // Afficher les infos de debug après un délai
        setTimeout(showDebugInfo, 500);
    }
    
    // Exposer les fonctions publiques
    window.CacheBuster = {
        checkAndBustCache,
        forceBustCache: bustCache,
        getCurrentVersion,
        showDebugInfo
    };
    
    // Initialiser
    init();
    
    console.log('✅ Cache Buster pour JobParserAPI v2.5 initialisé');
    
})();
