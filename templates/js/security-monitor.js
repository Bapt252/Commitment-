// 🛡️ COMMITMENT SECURITY MONITOR - Baptiste COMA
// Système de surveillance des accès non autorisés
// ⚠️ ACCÈS RESTREINT - Propriété de Bapt252

(function() {
    'use strict';
    
    // Watermark de protection
    const projectOwner = 'Baptiste COMA - Bapt252';
    const projectRepo = 'https://github.com/Bapt252/Commitment-';
    const unauthorizedUsers = ['Axclgrd', 'axel.guillouard', 'axelguillouard'];
    
    // Détection de tentatives d'accès suspect
    function detectSuspiciousAccess() {
        const userAgent = navigator.userAgent;
        const referrer = document.referrer;
        const currentUrl = window.location.href;
        
        // Log de sécurité
        const accessLog = {
            timestamp: new Date().toISOString(),
            userAgent: userAgent,
            referrer: referrer,
            url: currentUrl,
            ip: 'detected via browser'
        };
        
        // Vérification de patterns suspects
        const suspiciousPatterns = [
            /axel/i,
            /guillouard/i,
            /axclgrd/i
        ];
        
        let isSuspicious = false;
        suspiciousPatterns.forEach(pattern => {
            if (pattern.test(userAgent) || pattern.test(referrer)) {
                isSuspicious = true;
            }
        });
        
        if (isSuspicious) {
            // Envoi d'alerte (remplacer par votre webhook si nécessaire)
            console.warn('🚨 ACCÈS SUSPECT DÉTECTÉ', accessLog);
            
            // Redirection vers page de blocage
            showBlockedMessage();
        }
    }
    
    // Affichage du message de blocage
    function showBlockedMessage() {
        document.body.innerHTML = `
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-family: Arial, sans-serif;
                text-align: center;
            ">
                <div>
                    <h1>🚫 ACCÈS RESTREINT</h1>
                    <p>Cet accès a été détecté comme non autorisé.</p>
                    <p>Propriétaire: ${projectOwner}</p>
                    <p>Repository: <a href="${projectRepo}" style="color: #fff;">${projectRepo}</a></p>
                    <hr style="margin: 20px 0; opacity: 0.5;">
                    <small>Access logged at ${new Date().toLocaleString()}</small>
                </div>
            </div>
        `;
    }
    
    // Protection contre les DevTools
    let devtools = {open: false, orientation: null};
    setInterval(function() {
        if (window.outerHeight - window.innerHeight > 150 || 
            window.outerWidth - window.innerWidth > 150) {
            if (!devtools.open) {
                devtools.open = true;
                console.warn('🔍 DevTools détectés - Accès surveillé');
            }
        } else {
            devtools.open = false;
        }
    }, 500);
    
    // Watermark invisible dans le DOM
    const watermark = document.createElement('div');
    watermark.style.display = 'none';
    watermark.setAttribute('data-owner', projectOwner);
    watermark.setAttribute('data-repo', projectRepo);
    watermark.setAttribute('data-protected', 'true');
    document.body.appendChild(watermark);
    
    // Exécution de la détection
    detectSuspiciousAccess();
    
    // Protection du code source
    document.addEventListener('keydown', function(e) {
        // Désactiver F12, Ctrl+Shift+I, Ctrl+U
        if (e.keyCode === 123 || 
            (e.ctrlKey && e.shiftKey && e.keyCode === 73) ||
            (e.ctrlKey && e.keyCode === 85)) {
            e.preventDefault();
            console.warn('🚫 Tentative d\'inspection du code détectée');
            return false;
        }
    });
    
    // Désactiver clic droit
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        console.warn('🚫 Clic droit désactivé');
        return false;
    });
    
    console.log(`🛡️ COMMITMENT SECURITY ACTIVE - ${projectOwner}`);
})();