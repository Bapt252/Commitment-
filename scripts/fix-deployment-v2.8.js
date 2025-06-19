/**
 * Script de test et déploiement - JobParserAPI v2.8 DÉFINITIVE
 * Ce script teste la correction et la déploie automatiquement
 */

// ===== TESTS DE VALIDATION =====
function runComprehensiveTests() {
    console.log('🧪 DÉBUT DES TESTS COMPLETS v2.8 DÉFINITIVE');
    console.log('=' .repeat(60));
    
    const testCases = [
        {
            name: "Cas de test principal",
            input: "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...",
            expectedTitle: "Assistant Juridique",
            maxLength: 25
        },
        {
            name: "Assistant commercial",
            input: "Assistant(e) commercial Notre entreprise recherche un profil dynamique...",
            expectedTitle: "Assistant Commercial",
            maxLength: 25
        },
        {
            name: "Responsable marketing",
            input: "Responsable marketing digital Nous recherchons un professionnel expérimenté...",
            expectedTitle: "Responsable Marketing",
            maxLength: 25
        },
        {
            name: "Chef de projet",
            input: "Chef de projet informatique (H/F) Dans le cadre de notre développement...",
            expectedTitle: "Chef De Projet",
            maxLength: 25
        },
        {
            name: "Texte très long au début",
            input: "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua Assistant juridique recherché...",
            expectedMaxLength: 25
        }
    ];
    
    const parser = new JobParserAPI({ debug: true });
    let testsReussits = 0;
    let testsTotal = testCases.length;
    
    testCases.forEach((testCase, index) => {
        console.log(`\n📋 TEST ${index + 1}: ${testCase.name}`);
        console.log('📝 Input preview:', testCase.input.substring(0, 50) + '...');
        
        try {
            const result = parser.analyzeJobLocally(testCase.input);
            const extractedTitle = result.title;
            
            console.log('🎯 Titre extrait:', extractedTitle);
            console.log('📏 Longueur:', extractedTitle.length);
            
            // Vérifications
            const lengthOk = extractedTitle.length <= (testCase.maxLength || 25);
            const notFullText = extractedTitle !== testCase.input;
            const notEmpty = extractedTitle.length >= 3;
            const expectedMatch = testCase.expectedTitle ? 
                extractedTitle.toLowerCase().includes(testCase.expectedTitle.toLowerCase()) : true;
            
            const testPassed = lengthOk && notFullText && notEmpty && expectedMatch;
            
            if (testPassed) {
                console.log('✅ TEST RÉUSSI');
                testsReussits++;
            } else {
                console.log('❌ TEST ÉCHOUÉ');
                if (!lengthOk) console.log('  - Longueur excessive:', extractedTitle.length);
                if (!notFullText) console.log('  - Retourne tout le texte');
                if (!notEmpty) console.log('  - Titre vide ou trop court');
                if (!expectedMatch) console.log('  - Ne correspond pas au titre attendu');
            }
            
        } catch (error) {
            console.log('❌ ERREUR LORS DU TEST:', error);
        }
        
        console.log('-'.repeat(40));
    });
    
    console.log('\n📊 RÉSULTATS FINAUX:');
    console.log(`✅ Tests réussis: ${testsReussits}/${testsTotal}`);
    console.log(`📈 Taux de réussite: ${Math.round((testsReussits/testsTotal) * 100)}%`);
    
    const allTestsPassed = testsReussits === testsTotal;
    console.log(allTestsPassed ? 
        '🎉 TOUS LES TESTS ONT RÉUSSI !' : 
        '⚠️ Certains tests ont échoué');
    
    return {
        success: allTestsPassed,
        passed: testsReussits,
        total: testsTotal,
        rate: Math.round((testsReussits/testsTotal) * 100)
    };
}

// ===== FONCTION DE DÉPLOIEMENT =====
function deployFix() {
    console.log('🚀 DÉPLOIEMENT DE LA CORRECTION v2.8 DÉFINITIVE');
    console.log('=' .repeat(60));
    
    try {
        // 1. Vérifier que la nouvelle version est disponible
        if (typeof JobParserAPI === 'undefined') {
            throw new Error('JobParserAPI v2.8 non trouvée');
        }
        
        console.log('✅ 1. JobParserAPI v2.8 détectée');
        
        // 2. Tester la nouvelle version
        console.log('🧪 2. Test de la nouvelle version...');
        const testResults = runComprehensiveTests();
        
        if (!testResults.success) {
            throw new Error(`Tests échoués: ${testResults.passed}/${testResults.total} réussis`);
        }
        
        console.log('✅ 2. Tests de validation réussis');
        
        // 3. Remplacer l'instance globale
        console.log('🔄 3. Remplacement de l\'instance globale...');
        
        // Sauvegarder l'ancienne version
        window.JobParserAPI_OLD = window.JobParserAPI_OLD || window.JobParserAPI;
        
        // Créer nouvelle instance avec configuration correcte
        window.jobParserInstance = new JobParserAPI({
            apiUrl: 'http://localhost:5055/api/parse-job',
            debug: true,
            enablePDFCleaning: true
        });
        
        console.log('✅ 3. Instance globale mise à jour');
        
        // 4. Mettre à jour l'interface utilisateur
        console.log('🎨 4. Mise à jour de l\'interface...');
        updateUI();
        
        console.log('✅ 4. Interface mise à jour');
        
        // 5. Forcer un rafraîchissement du cache
        console.log('🧹 5. Nettoyage du cache...');
        clearParsingCache();
        
        console.log('✅ 5. Cache nettoyé');
        
        // 6. Test en situation réelle
        console.log('🎯 6. Test en situation réelle...');
        const realWorldTest = testRealWorldScenario();
        
        if (!realWorldTest.success) {
            throw new Error('Test en situation réelle échoué');
        }
        
        console.log('✅ 6. Test en situation réelle réussi');
        
        console.log('\n🎉 DÉPLOIEMENT RÉUSSI !');
        console.log('💫 JobParserAPI v2.8 DÉFINITIVE est maintenant actif');
        
        // Afficher un message de succès dans l'interface
        showDeploymentSuccess();
        
        return {
            success: true,
            version: '2.8',
            testsResults: testResults
        };
        
    } catch (error) {
        console.error('❌ ÉCHEC DU DÉPLOIEMENT:', error);
        
        // Restaurer l'ancienne version si possible
        if (window.JobParserAPI_OLD) {
            window.jobParserInstance = new window.JobParserAPI_OLD();
            console.log('🔄 Ancienne version restaurée');
        }
        
        showDeploymentError(error.message);
        
        return {
            success: false,
            error: error.message
        };
    }
}

// ===== FONCTIONS UTILITAIRES =====
function updateUI() {
    // Mettre à jour les messages de l'interface
    const banners = document.querySelectorAll('.urgent-fix-banner');
    banners.forEach(banner => {
        if (banner) {
            banner.innerHTML = `
                <div class="status-info">
                    <div class="fix-icon" style="background-color: #10b981;"></div>
                    <span>🎉 JobParserAPI v2.8 DÉFINITIVE déployée - Extraction titre CORRIGÉE définitivement !</span>
                </div>
                <button class="test-btn" onclick="testDeployedVersion()">
                    Tester v2.8
                </button>
            `;
            banner.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        }
    });
    
    // Mettre à jour les messages de debug
    const debugSection = document.getElementById('debug-section');
    if (debugSection) {
        const debugContent = document.getElementById('debug-content');
        if (debugContent) {
            debugContent.innerHTML = `
                <div style="color: #10b981; font-weight: bold;">
                    ✅ JobParserAPI v2.8 DÉFINITIVE active
                </div>
                <div>📊 Tests de validation: RÉUSSIS</div>
                <div>🎯 Extraction titre: CORRIGÉE</div>
                <div>🔄 Déploiement: TERMINÉ</div>
            `;
        }
        debugSection.style.display = 'block';
    }
}

function clearParsingCache() {
    // Nettoyer le cache du navigateur pour les scripts
    const timestamp = Date.now();
    
    // Forcer le rechargement des événements de parsing
    const analyzeButton = document.getElementById('analyze-job-text');
    if (analyzeButton) {
        // Cloner et remplacer pour supprimer les anciens listeners
        const newButton = analyzeButton.cloneNode(true);
        analyzeButton.parentNode.replaceChild(newButton, analyzeButton);
        
        // Ajouter le nouveau listener avec la version corrigée
        newButton.addEventListener('click', function() {
            const textarea = document.getElementById('job-description-text');
            if (textarea && textarea.value.trim()) {
                testAndParseWithNewVersion(textarea.value.trim());
            }
        });
    }
    
    // Nettoyer le sessionStorage des anciens résultats
    sessionStorage.removeItem('parsedJobData');
    
    console.log('🧹 Cache nettoyé avec timestamp:', timestamp);
}

function testRealWorldScenario() {
    console.log('🎯 Test en situation réelle...');
    
    const realTestText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...";
    
    try {
        const result = window.jobParserInstance.analyzeJobLocally(realTestText);
        
        const success = result.title && 
                       result.title.length <= 25 && 
                       result.title !== realTestText &&
                       result.title.toLowerCase().includes('assistant');
        
        console.log('🎯 Résultat test réel:', result.title);
        console.log('✅ Test réel:', success ? 'RÉUSSI' : 'ÉCHOUÉ');
        
        return { success, result };
        
    } catch (error) {
        console.error('❌ Erreur test réel:', error);
        return { success: false, error };
    }
}

function testAndParseWithNewVersion(text) {
    console.log('🔍 Test et parsing avec v2.8 DÉFINITIVE...');
    
    if (window.jobParserInstance) {
        window.jobParserInstance.parseJobText(text)
            .then(result => {
                console.log('✅ Parsing v2.8 réussi:', result);
                
                // Afficher les résultats dans l'interface
                if (window.JobParsingUI && window.JobParsingUI.showJobResults) {
                    window.JobParsingUI.showJobResults(result);
                }
                
                // Validation finale
                if (result.title && result.title.length <= 25) {
                    console.log('🎉 TITRE CORRECT:', result.title);
                    showNotification('🎉 Extraction titre corrigée ! Titre: ' + result.title, 'success');
                } else {
                    console.warn('⚠️ Titre encore problématique:', result.title);
                    showNotification('⚠️ Problème persiste avec le titre', 'warning');
                }
            })
            .catch(error => {
                console.error('❌ Erreur parsing v2.8:', error);
                showNotification('❌ Erreur lors du parsing', 'error');
            });
    } else {
        console.error('❌ Instance v2.8 non trouvée');
        showNotification('❌ Version v2.8 non initialisée', 'error');
    }
}

function showDeploymentSuccess() {
    showNotification('🎉 JobParserAPI v2.8 DÉFINITIVE déployée avec succès ! Le problème d\'extraction de titre est résolu.', 'success');
}

function showDeploymentError(message) {
    showNotification('❌ Échec du déploiement v2.8: ' + message, 'error');
}

function showNotification(message, type = 'info') {
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // Essayer d'utiliser le système de notifications existant
    if (window.JobParsingUI && window.JobParsingUI.showNotification) {
        window.JobParsingUI.showNotification(message, type);
    } else {
        // Fallback notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            max-width: 400px;
            font-size: 14px;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 5000);
    }
}

// ===== FONCTION DE TEST DE LA VERSION DÉPLOYÉE =====
function testDeployedVersion() {
    console.log('🧪 Test de la version déployée...');
    
    const testText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...";
    
    testAndParseWithNewVersion(testText);
}

// ===== EXPOSER LES FONCTIONS GLOBALEMENT =====
window.runComprehensiveTests = runComprehensiveTests;
window.deployFix = deployFix;
window.testDeployedVersion = testDeployedVersion;
window.testAndParseWithNewVersion = testAndParseWithNewVersion;

console.log('🔧 Script de test et déploiement v2.8 DÉFINITIVE chargé');
console.log('🚀 Tapez deployFix() pour déployer la correction');
console.log('🧪 Tapez runComprehensiveTests() pour tester');