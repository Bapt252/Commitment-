// Debug spécifique pour l'analyse ChatGPT - Tracer tous les appels
// Ce script va intercepter et afficher tous les appels pour identifier le problème

console.log('🔍 Debug ChatGPT Analysis - Chargement...');

// Intercepter les appels à l'API ChatGPT
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const [url, options] = args;
    
    // Intercepter les appels OpenAI
    if (url && url.includes('openai.com')) {
        console.log('🔗 Appel API OpenAI intercepté:');
        console.log('URL:', url);
        console.log('Options:', {
            method: options?.method,
            headers: options?.headers,
            bodyLength: options?.body?.length
        });
        
        try {
            const response = await originalFetch.apply(this, args);
            console.log('📥 Réponse OpenAI:');
            console.log('Status:', response.status);
            console.log('StatusText:', response.statusText);
            
            if (!response.ok) {
                const errorText = await response.clone().text();
                console.error('❌ Erreur API OpenAI:', errorText);
            } else {
                const responseData = await response.clone().json();
                console.log('✅ Réponse OpenAI réussie:', responseData);
            }
            
            return response;
        } catch (error) {
            console.error('❌ Erreur appel OpenAI:', error);
            throw error;
        }
    }
    
    return originalFetch.apply(this, args);
};

// Intercepter les méthodes d'affichage des résultats
function interceptDisplayMethods() {
    // Attendre que l'instance soit disponible
    if (!window.jobParsingUIGPT) {
        setTimeout(interceptDisplayMethods, 500);
        return;
    }
    
    const instance = window.jobParsingUIGPT;
    
    // Intercepter displayResults
    const originalDisplayResults = instance.displayResults;
    instance.displayResults = function(results) {
        console.log('🎨 displayResults appelé avec:', results);
        
        // Vérifier le conteneur de résultats
        const container = document.getElementById('job-info-container');
        console.log('📦 Conteneur résultats:', container ? 'Trouvé' : 'MANQUANT');
        
        if (container) {
            console.log('👁️ Visibilité conteneur avant:', container.style.display);
        }
        
        // Appeler la méthode originale
        const result = originalDisplayResults.call(this, results);
        
        if (container) {
            console.log('👁️ Visibilité conteneur après:', container.style.display);
        }
        
        // Vérifier chaque champ
        const fields = [
            'job-title-value',
            'job-contract-value', 
            'job-location-value',
            'job-skills-value'
        ];
        
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                console.log(`🏷️ ${fieldId}: "${field.textContent}"`);
            } else {
                console.error(`❌ Champ ${fieldId} MANQUANT`);
            }
        });
        
        return result;
    };
    
    // Intercepter analyzeJobText
    const originalAnalyzeJobText = instance.analyzeJobText;
    instance.analyzeJobText = async function(text) {
        console.log('📝 analyzeJobText appelé avec texte longueur:', text.length);
        console.log('📝 Aperçu texte:', text.substring(0, 200) + '...');
        
        try {
            const result = await originalAnalyzeJobText.call(this, text);
            console.log('✅ analyzeJobText terminé avec succès');
            return result;
        } catch (error) {
            console.error('❌ Erreur dans analyzeJobText:', error);
            throw error;
        }
    };
    
    // Intercepter analyzeFile  
    const originalAnalyzeFile = instance.analyzeFile;
    instance.analyzeFile = async function(file) {
        console.log('📄 analyzeFile appelé avec fichier:', {
            name: file.name,
            size: file.size,
            type: file.type
        });
        
        try {
            const result = await originalAnalyzeFile.call(this, file);
            console.log('✅ analyzeFile terminé avec succès');
            return result;
        } catch (error) {
            console.error('❌ Erreur dans analyzeFile:', error);
            throw error;
        }
    };
    
    console.log('✅ Méthodes d\'analyse interceptées');
}

// Intercepter le parser GPT
function interceptGPTParser() {
    if (!window.jobParsingUIGPT?.gptParser) {
        setTimeout(interceptGPTParser, 500);
        return;
    }
    
    const parser = window.jobParsingUIGPT.gptParser;
    
    // Intercepter parseJobText
    const originalParseJobText = parser.parseJobText;
    parser.parseJobText = async function(text) {
        console.log('🤖 parseJobText GPT appelé avec:', {
            longueur: text.length,
            apercu: text.substring(0, 100) + '...'
        });
        
        try {
            const result = await originalParseJobText.call(this, text);
            console.log('🎉 parseJobText GPT résultat:', result);
            return result;
        } catch (error) {
            console.error('💥 Erreur parseJobText GPT:', error);
            throw error;
        }
    };
    
    // Intercepter parseJobFile
    const originalParseJobFile = parser.parseJobFile;
    parser.parseJobFile = async function(file) {
        console.log('📁 parseJobFile GPT appelé avec:', file.name);
        
        try {
            const result = await originalParseJobFile.call(this, file);
            console.log('🎉 parseJobFile GPT résultat:', result);
            return result;
        } catch (error) {
            console.error('💥 Erreur parseJobFile GPT:', error);
            throw error;
        }
    };
    
    console.log('✅ Parser GPT intercepté');
}

// Fonction de test complet
window.testCompleteFlow = async function() {
    console.log('🧪 === TEST COMPLET DU FLUX ===');
    
    if (!window.jobParsingUIGPT) {
        console.error('❌ jobParsingUIGPT non disponible');
        return;
    }
    
    if (!window.jobParsingUIGPT.gptParser) {
        console.error('❌ gptParser non disponible');
        return;
    }
    
    if (!window.jobParsingUIGPT.gptParser.hasApiKey()) {
        console.error('❌ Clé API non configurée');
        return;
    }
    
    const testText = `Poste: Comptable Assistant
Entreprise: Bcom HR
Localisation: Paris
Type de contrat: CDI
Expérience: 2 ans minimum
Formation: BTS Comptabilité
Compétences: Excel, SAP, Sage
Missions: Saisie comptable, rapprochements bancaires, déclarations TVA
Rémunération: 28-32k€
Avantages: Mutuelle, tickets restaurant`;
    
    try {
        console.log('🚀 Lancement test avec texte...');
        await window.jobParsingUIGPT.analyzeJobText(testText);
    } catch (error) {
        console.error('💥 Erreur test complet:', error);
    }
};

// Démarrer les interceptions
setTimeout(() => {
    interceptDisplayMethods();
    interceptGPTParser();
    
    console.log('🔍 Debug ChatGPT Analysis activé !');
    console.log('💡 Utilisez testCompleteFlow() pour tester le flux complet');
}, 1000);
