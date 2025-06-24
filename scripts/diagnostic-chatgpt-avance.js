// diagnostic-chatgpt-avance.js
// Script pour diagnostiquer en profondeur pourquoi ChatGPT ne parse pas

console.log('🔍 Diagnostic ChatGPT avancé - Identification du problème...');

// Fonction de diagnostic complet
function diagnoseProblemChatGPT() {
    console.log('\n🔍 === DIAGNOSTIC CHATGPT COMPLET ===');
    
    // 1. Vérifier les instances
    console.log('\n📋 1. VÉRIFICATION DES INSTANCES:');
    console.log('window.JobParserGPT:', typeof window.JobParserGPT);
    console.log('window.jobParserGPTInstance:', !!window.jobParserGPTInstance);
    console.log('window.JobParserUIIntegration:', typeof window.JobParserUIIntegration);
    console.log('window.jobParsingUIGPT:', !!window.jobParsingUIGPT);
    
    // 2. Vérifier l'instance active
    console.log('\n🤖 2. INSTANCE ACTIVE:');
    if (window.jobParsingUIGPT) {
        console.log('✅ Instance UI active trouvée');
        console.log('gptParser:', !!window.jobParsingUIGPT.gptParser);
        if (window.jobParsingUIGPT.gptParser) {
            console.log('hasApiKey:', window.jobParsingUIGPT.gptParser.hasApiKey());
            console.log('apiKey présente:', !!window.jobParsingUIGPT.gptParser.apiKey);
        }
    } else {
        console.log('❌ Aucune instance UI active');
    }
    
    // 3. Vérifier les éléments DOM
    console.log('\n🎛️ 3. ÉLÉMENTS DOM:');
    const elements = {
        'job-file-input': document.getElementById('job-file-input'),
        'job-description-text': document.getElementById('job-description-text'),
        'analyze-job-text': document.getElementById('analyze-job-text'),
        'job-info-container': document.getElementById('job-info-container'),
        'openai-api-key': document.getElementById('openai-api-key')
    };
    
    Object.entries(elements).forEach(([name, el]) => {
        console.log(`${name}:`, !!el);
    });
    
    // 4. Tester l'API OpenAI directement
    console.log('\n🔑 4. TEST API OPENAI:');
    testOpenAIDirectly();
    
    // 5. Simuler une analyse
    console.log('\n🧪 5. SIMULATION D\'ANALYSE:');
    simulateAnalysis();
}

// Test direct de l'API OpenAI
async function testOpenAIDirectly() {
    const apiKeyInput = document.getElementById('openai-api-key');
    if (!apiKeyInput || !apiKeyInput.value) {
        console.log('❌ Pas de clé API dans le champ');
        return;
    }
    
    const apiKey = apiKeyInput.value.trim();
    console.log('🔑 Clé API format:', apiKey.startsWith('sk-') ? 'Correct' : 'Incorrect');
    
    try {
        console.log('📡 Test connexion OpenAI...');
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [
                    { role: 'user', content: 'Dis juste "test ok"' }
                ],
                max_tokens: 10
            })
        });
        
        console.log('📡 Statut réponse:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API OpenAI fonctionne !');
            console.log('Réponse:', data.choices[0].message.content);
        } else {
            const error = await response.text();
            console.log('❌ Erreur API:', error);
        }
    } catch (error) {
        console.log('❌ Erreur connexion:', error);
    }
}

// Simulation d'analyse
function simulateAnalysis() {
    if (!window.jobParsingUIGPT) {
        console.log('❌ Instance UI non disponible');
        return;
    }
    
    const testText = `
    FICHE DE POSTE - DÉVELOPPEUR FULL STACK
    
    Entreprise: TechCorp
    Localisation: Paris
    Type de contrat: CDI
    Expérience: 3-5 ans
    Formation: Bac+5 informatique
    Salaire: 50-60k€
    
    Compétences requises:
    - JavaScript, React, Node.js
    - SQL, MongoDB
    - Git, Docker
    
    Missions:
    - Développement d'applications web
    - Maintenance et évolution des systèmes
    - Collaboration avec les équipes
    
    Avantages:
    - Télétravail partiel
    - Mutuelle
    - Formation continue
    `;
    
    console.log('🧪 Test avec texte simulé...');
    console.log('Texte:', testText.substring(0, 100) + '...');
    
    // Tenter l'analyse
    if (window.jobParsingUIGPT.analyzeJobText) {
        console.log('🚀 Lancement analyse simulée...');
        window.jobParsingUIGPT.analyzeJobText(testText)
            .then(result => {
                console.log('✅ Analyse réussie:', result);
            })
            .catch(error => {
                console.log('❌ Analyse échouée:', error);
            });
    } else {
        console.log('❌ Méthode analyzeJobText non disponible');
    }
}

// Test de l'affichage des résultats
function testResultDisplay() {
    console.log('\n🎨 TEST AFFICHAGE RÉSULTATS:');
    
    const mockResult = {
        title: 'Développeur Test',
        contract_type: 'CDI',
        location: 'Paris',
        experience: '3 ans',
        education: 'Bac+5',
        salary: '50k€',
        skills: ['JavaScript', 'React', 'Node.js'],
        responsibilities: 'Développement applications web',
        benefits: 'Télétravail, mutuelle'
    };
    
    if (window.jobParsingUIGPT && window.jobParsingUIGPT.displayResults) {
        console.log('🎨 Test affichage avec données mockées...');
        window.jobParsingUIGPT.displayResults(mockResult);
        console.log('✅ Affichage testé');
    } else {
        console.log('❌ Méthode displayResults non disponible');
    }
}

// Vérifier les event listeners
function checkEventListeners() {
    console.log('\n🎯 VÉRIFICATION EVENT LISTENERS:');
    
    const fileInput = document.getElementById('job-file-input');
    const textArea = document.getElementById('job-description-text');
    const analyzeBtn = document.getElementById('analyze-job-text');
    
    // Test d'upload de fichier simulé
    if (fileInput) {
        console.log('📁 Test event listener fichier...');
        // On ne peut pas vraiment tester sans fichier, mais on peut vérifier si les listeners sont attachés
        const listeners = getEventListeners ? getEventListeners(fileInput) : 'Non disponible';
        console.log('Listeners fichier:', listeners);
    }
    
    // Test textarea
    if (textArea) {
        console.log('📝 Test event listener textarea...');
        const listeners = getEventListeners ? getEventListeners(textArea) : 'Non disponible';
        console.log('Listeners textarea:', listeners);
        
        // Simuler saisie de texte
        textArea.value = 'Test de saisie pour déclencher analyse';
        textArea.dispatchEvent(new Event('input', { bubbles: true }));
        console.log('Événement input déclenché');
    }
}

// Fonction principale
function runCompleteDiagnosis() {
    diagnoseProblemChatGPT();
    
    setTimeout(() => {
        testResultDisplay();
    }, 1000);
    
    setTimeout(() => {
        checkEventListeners();
    }, 2000);
    
    console.log('\n🎯 DIAGNOSTIC TERMINÉ - Vérifiez les résultats ci-dessus');
}

// Export pour utilisation
window.diagnoseChatGPTProblem = runCompleteDiagnosis;

// Auto-run
console.log('🚀 Lancement diagnostic automatique dans 3 secondes...');
setTimeout(runCompleteDiagnosis, 3000);