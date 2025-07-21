// Fix Job Parser Conflicts - Désactive l'ancien système et active ChatGPT
// Ce script corrige le conflit entre l'ancien parsing et le nouveau ChatGPT

console.log('🔧 Correction des conflits Job Parser...');

// 1. Désactiver l'ancien système JobParsingUI
if (window.jobParsingUI) {
    console.log('❌ Désactivation de l\'ancien JobParsingUI...');
    
    // Supprimer les event listeners de l'ancien système
    const oldInstance = window.jobParsingUI;
    
    // Nettoyer les événements sur les éléments DOM
    const elementsToClean = [
        'job-file-input',
        'job-drop-zone', 
        'analyze-job-text',
        'remove-file'
    ];
    
    elementsToClean.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            // Remplacer l'élément par un clone pour supprimer tous les event listeners
            const newElement = element.cloneNode(true);
            element.parentNode.replaceChild(newElement, element);
        }
    });
    
    // Supprimer la référence globale
    window.jobParsingUI = null;
    console.log('✅ Ancien système désactivé');
}

// 2. Fonction pour forcer l'initialisation du ChatGPT
function initializeChatGPTParser() {
    console.log('🤖 Initialisation forcée du ChatGPT Parser...');
    
    // Vérifier que JobParserGPT est disponible
    if (!window.JobParserGPT) {
        console.error('❌ JobParserGPT non trouvé');
        return;
    }
    
    // Créer ou recréer l'instance ChatGPT
    if (window.jobParsingUIGPT) {
        console.log('🔄 Remplacement de l\'instance ChatGPT existante...');
    }
    
    // Créer la nouvelle instance
    window.jobParsingUIGPT = new JobParserUIIntegration();
    
    console.log('✅ ChatGPT Parser activé et fonctionnel !');
    
    // Test de santé
    setTimeout(() => {
        const analyzeBtn = document.getElementById('analyze-job-text');
        if (analyzeBtn) {
            console.log('✅ Bouton d\'analyse trouvé et prêt');
        }
        
        const configSection = document.getElementById('gpt-config-section');
        if (configSection) {
            console.log('✅ Section de configuration ChatGPT active');
        } else {
            console.log('⚠️ Section de configuration non trouvée - création...');
            if (window.jobParsingUIGPT) {
                window.jobParsingUIGPT.createApiConfigUI();
            }
        }
    }, 100);
}

// 3. Attendre que JobParserUIIntegration soit disponible
function waitForJobParserUIIntegration() {
    if (window.JobParserUIIntegration) {
        initializeChatGPTParser();
    } else {
        console.log('⏳ Attente de JobParserUIIntegration...');
        setTimeout(waitForJobParserUIIntegration, 200);
    }
}

// 4. Lancer la correction
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(waitForJobParserUIIntegration, 100);
    });
} else {
    setTimeout(waitForJobParserUIIntegration, 100);
}

// 5. Fonction de diagnostic pour debug
window.diagnoseChatGPTParser = function() {
    console.log('🔍 Diagnostic ChatGPT Parser:');
    console.log('- JobParserGPT disponible:', !!window.JobParserGPT);
    console.log('- JobParserUIIntegration disponible:', !!window.JobParserUIIntegration);
    console.log('- Instance ChatGPT active:', !!window.jobParsingUIGPT);
    console.log('- Ancien système:', !!window.jobParsingUI);
    
    const apiKeyInput = document.getElementById('openai-api-key');
    console.log('- Champ clé API:', !!apiKeyInput);
    if (apiKeyInput) {
        console.log('- Clé API saisie:', !!apiKeyInput.value);
    }
    
    const analyzeBtn = document.getElementById('analyze-job-text');
    console.log('- Bouton analyser:', !!analyzeBtn);
    
    if (window.jobParsingUIGPT && window.jobParsingUIGPT.gptParser) {
        console.log('- Parser GPT initialisé:', true);
        console.log('- Clé API configurée:', window.jobParsingUIGPT.gptParser.hasApiKey());
    }
};

// 6. Fonction de test pour l'utilisateur
window.testChatGPTParser = async function() {
    console.log('🧪 Test du ChatGPT Parser...');
    
    if (!window.jobParsingUIGPT) {
        console.error('❌ ChatGPT Parser non initialisé');
        return;
    }
    
    if (!window.jobParsingUIGPT.gptParser) {
        console.error('❌ Parser GPT non trouvé');
        return;
    }
    
    if (!window.jobParsingUIGPT.gptParser.hasApiKey()) {
        console.error('❌ Clé API non configurée');
        return;
    }
    
    try {
        const testText = `Poste: Développeur Frontend
Entreprise: TechCorp
Lieu: Paris  
Contrat: CDI
Expérience: 3 ans
Formation: Bac+3 informatique
Compétences: React, JavaScript, TypeScript
Missions: Développement interfaces utilisateur
Salaire: 45-50k€
Avantages: Télétravail, mutuelle`;
        
        console.log('🔄 Test en cours...');
        const result = await window.jobParsingUIGPT.gptParser.parseJobText(testText);
        console.log('✅ Test réussi !', result);
        return result;
    } catch (error) {
        console.error('❌ Test échoué:', error.message);
        return null;
    }
};

console.log('🎯 Correction des conflits terminée !');
console.log('💡 Utilisez diagnoseChatGPTParser() pour diagnostiquer');
console.log('🧪 Utilisez testChatGPTParser() pour tester');
