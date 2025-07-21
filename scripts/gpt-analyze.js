// GPT Analyze Script
// Placeholder pour l'analyse GPT (fonctionnalité future)

class GPTAnalyzer {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('GPT Analyzer initialisé (mode développement)');
        this.setupGPTButton();
    }
    
    setupGPTButton() {
        const gptButton = document.getElementById('analyze-with-gpt');
        if (gptButton) {
            gptButton.addEventListener('click', () => {
                this.showNotification('info', 'Fonctionnalité en développement', 'L\'analyse GPT sera bientôt disponible. Utilisez l\'analyse standard pour le moment.');
            });
        }
    }
    
    showNotification(type, title, message) {
        if (window.questionnaireNav) {
            window.questionnaireNav.showNotification(type, title, message);
        } else {
            console.log(`${type.toUpperCase()}: ${title} - ${message}`);
        }
    }
}

// Initialiser
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.gptAnalyzer = new GPTAnalyzer();
    }, 400);
});