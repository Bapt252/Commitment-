// fix-job-parser-priority.js
// Script pour forcer la priorité du nouveau système ChatGPT sur l'ancien

console.log('🔧 Fix Job Parser Priority - Résolution des conflits...');

// Fonction pour désactiver l'ancien système
function disableOldJobParser() {
    console.log('❌ Désactivation ancien job parser...');
    
    // Supprimer l'ancienne instance
    if (window.jobParsingUI) {
        window.jobParsingUI = null;
        console.log('✅ Ancienne instance JobParsingUI supprimée');
    }
    
    // Nettoyer les event listeners de l'ancien système
    const fileInput = document.getElementById('job-file-input');
    const dropZone = document.getElementById('job-drop-zone');
    const textArea = document.getElementById('job-description-text');
    const analyzeButton = document.getElementById('analyze-job-text');
    
    if (fileInput) {
        fileInput.replaceWith(fileInput.cloneNode(true));
    }
    if (dropZone) {
        const newDropZone = dropZone.cloneNode(true);
        dropZone.parentNode.replaceChild(newDropZone, dropZone);
    }
    if (analyzeButton) {
        analyzeButton.replaceWith(analyzeButton.cloneNode(true));
    }
    
    console.log('✅ Event listeners de l\'ancien système nettoyés');
}

// Fonction pour forcer l'initialisation du nouveau système
function forceNewJobParserInit() {
    console.log('🤖 Initialisation forcée du nouveau système ChatGPT...');
    
    // Vérifier que les dépendances sont chargées
    if (!window.JobParserGPT) {
        console.error('❌ JobParserGPT pas encore chargé');
        return false;
    }
    
    if (!window.JobParserUIIntegration) {
        console.error('❌ JobParserUIIntegration pas encore chargé');
        return false;
    }
    
    // Créer la nouvelle instance en forçant
    try {
        window.jobParsingUIGPT = new window.JobParserUIIntegration();
        console.log('✅ Nouveau système ChatGPT initialisé avec succès !');
        
        // Ajouter une bannière pour confirmer
        addSuccessBanner();
        return true;
    } catch (error) {
        console.error('❌ Erreur initialisation nouveau système:', error);
        return false;
    }
}

// Ajouter une bannière de confirmation
function addSuccessBanner() {
    const existingBanner = document.getElementById('chatgpt-success-banner');
    if (existingBanner) return;
    
    const banner = document.createElement('div');
    banner.id = 'chatgpt-success-banner';
    banner.style.cssText = `
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 12px 20px;
        margin: 10px 0;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    `;
    banner.innerHTML = '🎉 <strong>ChatGPT Parser activé !</strong> Configurez votre clé API et testez avec un fichier ou du texte.';
    
    // Insérer après le header
    const header = document.querySelector('.header');
    if (header && header.parentNode) {
        header.parentNode.insertBefore(banner, header.nextSibling);
    }
    
    // Auto-masquer après 8 secondes
    setTimeout(() => {
        banner.style.transition = 'opacity 0.5s ease';
        banner.style.opacity = '0';
        setTimeout(() => banner.remove(), 500);
    }, 8000);
}

// Fonction de test rapide
function testChatGPTSystem() {
    console.log('🧪 Test du système ChatGPT...');
    
    if (!window.jobParsingUIGPT) {
        console.error('❌ Système ChatGPT non initialisé');
        return false;
    }
    
    if (!window.jobParsingUIGPT.gptParser) {
        console.error('❌ Parser GPT non disponible');
        return false;
    }
    
    console.log('✅ Système ChatGPT prêt !');
    console.log('🔑 Clé API configurée:', window.jobParsingUIGPT.gptParser.hasApiKey() ? 'Oui' : 'Non');
    
    return true;
}

// Exporter les fonctions pour utilisation externe
window.fixJobParserPriority = {
    disableOld: disableOldJobParser,
    forceNew: forceNewJobParserInit,
    test: testChatGPTSystem
};

// Fonction principale de fix
function executeJobParserFix() {
    console.log('🚀 Exécution du fix Job Parser...');
    
    // Étape 1: Désactiver l'ancien
    disableOldJobParser();
    
    // Étape 2: Attendre un peu puis forcer le nouveau
    setTimeout(() => {
        const success = forceNewJobParserInit();
        
        if (success) {
            console.log('🎉 Fix Job Parser terminé avec succès !');
            
            // Test du système
            setTimeout(testChatGPTSystem, 500);
        } else {
            console.error('❌ Fix Job Parser échoué');
            
            // Réessayer dans 2 secondes
            setTimeout(executeJobParserFix, 2000);
        }
    }, 300);
}

// Auto-exécution quand tout est chargé
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(executeJobParserFix, 500);
    });
} else {
    setTimeout(executeJobParserFix, 500);
}

console.log('🔧 Fix Job Parser Priority script chargé - Auto-exécution programmée');