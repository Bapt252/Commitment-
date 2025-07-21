// Backend Configuration Helper
// Aide pour la configuration du backend

class BackendConfigHelper {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('Backend Config Helper initialisé');
        this.setupHelpButton();
    }
    
    setupHelpButton() {
        const helpButton = document.getElementById('backend-help-btn');
        if (helpButton) {
            helpButton.addEventListener('click', () => {
                this.showConfigHelp();
            });
        }
    }
    
    showConfigHelp() {
        const helpMessage = `Configuration du parser local :
        
1. Vérifiez que tous les scripts sont chargés
2. L'analyse fonctionne en mode local
3. Aucune configuration supplémentaire requise
        
Le système fonctionne correctement !`;
        
        if (window.questionnaireNav) {
            window.questionnaireNav.showNotification('info', 'Configuration', helpMessage);
        }
    }
}

// Initialiser
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.backendConfigHelper = new BackendConfigHelper();
    }, 500);
});