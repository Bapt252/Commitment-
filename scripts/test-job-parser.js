/**
 * Script de test pour vérifier le fonctionnement du job parser corrigé
 * À exécuter dans la console du navigateur sur la page client-questionnaire.html
 */

async function testJobParser() {
    console.log('🧪 Début des tests du job parser...');
    
    // Test 1: Vérifier que l'API est chargée
    console.log('\n=== Test 1: Vérification de l\'API ===');
    
    if (window.JobParserAPI) {
        console.log('✅ window.JobParserAPI est disponible');
        
        // Créer une instance de test
        const testAPI = new window.JobParserAPI({
            apiUrl: 'http://localhost:5055/api/parse-job',
            debug: true
        });
        
        console.log('✅ Instance JobParserAPI créée avec succès');
    } else {
        console.error('❌ window.JobParserAPI non trouvée');
        return;
    }
    
    // Test 2: Vérifier que l'UI est initialisée
    console.log('\n=== Test 2: Vérification de l\'UI ===');
    
    if (window.JobParsingUI) {
        console.log('✅ window.JobParsingUI est disponible');
        
        if (window.JobParsingUI.jobParserInstance) {
            const instance = window.JobParsingUI.jobParserInstance();
            if (instance) {
                console.log('✅ Instance JobParser UI initialisée');
            } else {
                console.warn('⚠️ Instance JobParser UI non initialisée');
            }
        }
    } else {
        console.error('❌ window.JobParsingUI non trouvée');
    }
    
    // Test 3: Vérifier la disponibilité du backend
    console.log('\n=== Test 3: Test de connexion backend ===');
    
    try {
        const response = await fetch('http://localhost:5055/api/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend disponible:', data);
        } else {
            console.warn('⚠️ Backend répond mais avec erreur:', response.status);
        }
    } catch (error) {
        console.warn('⚠️ Backend non accessible:', error.message);
        console.log('💡 Le parser local devrait fonctionner en fallback');
    }
    
    // Test 4: Test d'analyse de texte simple
    console.log('\n=== Test 4: Analyse de texte test ===');
    
    const testText = `
    FICHE DE POSTE
    
    Intitulé: Développeur JavaScript Senior
    Entreprise: TechCorp
    Lieu: Paris 75001
    Contrat: CDI
    Salaire: 45-55K€ selon expérience
    
    Expérience requise: 3-5 ans en développement web
    
    Compétences:
    - JavaScript ES6+
    - React.js
    - Node.js
    - Git
    - SQL
    
    Missions:
    - Développement d'applications web modernes
    - Collaboration avec l'équipe produit
    - Code review et mentoring junior
    
    Avantages:
    - Télétravail 2j/semaine
    - Tickets restaurant
    - Mutuelle
    `;
    
    if (window.JobParsingUI && window.JobParsingUI.jobParserInstance) {
        const instance = window.JobParsingUI.jobParserInstance();
        if (instance) {
            try {
                console.log('🔍 Analyse du texte de test...');
                const result = await instance.parseJobText(testText);
                console.log('✅ Résultat de l\'analyse:', result);
                
                // Vérifier que les données ne sont pas génériques
                if (result.title && result.title !== 'Comptable Auxiliaire') {
                    console.log('✅ Titre extrait correctement:', result.title);
                } else {
                    console.warn('⚠️ Titre générique détecté, possible problème');
                }
                
                if (result.skills && result.skills.length > 0) {
                    console.log('✅ Compétences extraites:', result.skills);
                } else {
                    console.warn('⚠️ Aucune compétence extraite');
                }
                
            } catch (error) {
                console.error('❌ Erreur lors de l\'analyse:', error);
            }
        }
    }
    
    // Test 5: Vérifier les éléments DOM
    console.log('\n=== Test 5: Vérification des éléments DOM ===');
    
    const elements = {
        'recruitment-yes': document.getElementById('recruitment-yes'),
        'job-parsing-section': document.getElementById('job-parsing-section'),
        'job-description-text': document.getElementById('job-description-text'),
        'analyze-job-text': document.getElementById('analyze-job-text'),
        'job-info-container': document.getElementById('job-info-container')
    };
    
    Object.entries(elements).forEach(([name, element]) => {
        if (element) {
            console.log(`✅ Élément trouvé: ${name}`);
        } else {
            console.warn(`⚠️ Élément manquant: ${name}`);
        }
    });
    
    // Test 6: Simuler le workflow complet
    console.log('\n=== Test 6: Simulation du workflow ===');
    
    const recruitmentYes = document.getElementById('recruitment-yes');
    const jobParsingSection = document.getElementById('job-parsing-section');
    
    if (recruitmentYes && jobParsingSection) {
        console.log('📝 Simulation: sélection "Oui" pour recrutement...');
        
        // Simuler le clic sur "Oui"
        recruitmentYes.checked = true;
        recruitmentYes.dispatchEvent(new Event('change'));
        
        // Vérifier que la section apparaît
        setTimeout(() => {
            if (jobParsingSection.classList.contains('active')) {
                console.log('✅ Section de parsing affichée correctement');
            } else {
                console.warn('⚠️ Section de parsing non affichée');
            }
        }, 100);
    }
    
    console.log('\n🎉 Tests terminés !');
    console.log('\n📋 Résumé:');
    console.log('- Vérifiez les ✅ pour les tests réussis');
    console.log('- Corrigez les ❌ pour les erreurs critiques');
    console.log('- Examinez les ⚠️ pour les avertissements');
}

// Test rapide de l'API
async function quickAPITest() {
    console.log('⚡ Test rapide de l\'API...');
    
    if (!window.JobParserAPI) {
        console.error('❌ JobParserAPI non disponible');
        return;
    }
    
    const api = new window.JobParserAPI({
        apiUrl: 'http://localhost:5055/api/parse-job',
        debug: true
    });
    
    const simpleText = "Recherche développeur React avec 2 ans d'expérience minimum";
    
    try {
        const result = await api.parseJobText(simpleText);
        console.log('✅ Test rapide réussi:', result);
        return true;
    } catch (error) {
        console.error('❌ Test rapide échoué:', error);
        return false;
    }
}

// Test de connectivité backend
async function testBackendConnectivity() {
    console.log('🌐 Test de connectivité backend...');
    
    try {
        // Test health check
        const healthResponse = await fetch('http://localhost:5055/api/health');
        if (healthResponse.ok) {
            console.log('✅ Health check réussi');
        }
        
        // Test endpoint principal
        const formData = new FormData();
        formData.append('text', 'Test de connectivité');
        
        const parseResponse = await fetch('http://localhost:5055/api/parse-job', {
            method: 'POST',
            body: formData
        });
        
        if (parseResponse.ok) {
            const data = await parseResponse.json();
            console.log('✅ Endpoint de parsing accessible:', data);
        } else {
            console.warn('⚠️ Endpoint de parsing répond avec erreur:', parseResponse.status);
        }
        
    } catch (error) {
        console.error('❌ Backend non accessible:', error.message);
        console.log('💡 Conseil: Démarrez le backend avec "python job_parser_api.py"');
    }
}

// Commandes disponibles dans la console
console.log('🔧 Commandes de test disponibles:');
console.log('- testJobParser() : Test complet');
console.log('- quickAPITest() : Test rapide de l\'API');
console.log('- testBackendConnectivity() : Test de connectivité backend');

// Export pour utilisation dans la console
window.testJobParser = testJobParser;
window.quickAPITest = quickAPITest;
window.testBackendConnectivity = testBackendConnectivity;
