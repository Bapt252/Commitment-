// Debug GPT Script
// Outils de debug pour les fonctionnalités GPT

class DebugGPT {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('Debug GPT initialisé');
        this.checkGPTStatus();
    }
    
    checkGPTStatus() {
        // Simuler la vérification du statut GPT
        const gptStatus = {
            available: false,
            reason: 'Fonctionnalité en développement'
        };
        
        console.log('Statut GPT:', gptStatus);
        return gptStatus;
    }
    
    logGPTRequest(request) {
        console.log('Requête GPT:', request);
    }
    
    logGPTResponse(response) {
        console.log('Réponse GPT:', response);
    }
    
    showGPTError(error) {
        console.error('Erreur GPT:', error);
        
        if (window.questionnaireNav) {
            window.questionnaireNav.showNotification('error', 'Erreur GPT', 'Une erreur est survenue avec l\'analyse GPT.');
        }
    }
}

// Initialiser
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.debugGPT = new DebugGPT();
    }, 600);
});