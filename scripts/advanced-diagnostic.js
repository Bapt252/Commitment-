/**
 * Diagnostic avancé JobParserAPI - Détection de problèmes v2.5
 * Ce script fait un diagnostic complet pour identifier pourquoi l'extraction ne fonctionne pas
 */

(function() {
    'use strict';
    
    // Diagnostic au chargement
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(runAdvancedDiagnostic, 2000); // Laisser le temps aux scripts de charger
    });
    
    function runAdvancedDiagnostic() {
        console.log('🔍 === DIAGNOSTIC AVANCÉ JOBPARSERAPI ===');
        
        const diagnosticResults = {
            apiAvailable: false,
            version: 'unknown',
            methods: {},
            testResults: {}
        };
        
        // 1. Vérifier la disponibilité de l'API
        if (typeof window.JobParserAPI === 'function') {
            diagnosticResults.apiAvailable = true;
            console.log('✅ JobParserAPI trouvée');
            
            try {
                // 2. Créer une instance de test
                const testInstance = new window.JobParserAPI({ debug: true });
                console.log('✅ Instance créée avec succès');
                
                // 3. Vérifier les méthodes disponibles
                const methods = Object.getOwnPropertyNames(window.JobParserAPI.prototype);
                diagnosticResults.methods = methods;
                console.log('📋 Méthodes disponibles:', methods);
                
                // 4. Vérifier la version via le code source
                if (testInstance.extractJobTitle) {
                    const extractTitleCode = testInstance.extractJobTitle.toString();
                    
                    if (extractTitleCode.includes('Ultra-enhanced title extraction v2.5')) {
                        diagnosticResults.version = 'v2.5';
                        console.log('✅ Version v2.5 confirmée');
                    } else if (extractTitleCode.includes('Enhanced title extraction v2.4')) {
                        diagnosticResults.version = 'v2.4';
                        console.log('⚠️ Version v2.4 détectée (ancienne)');
                    } else {
                        diagnosticResults.version = 'v2.3 ou antérieure';
                        console.log('❌ Version ancienne détectée');
                    }
                    
                    // 5. Test d'extraction sur un cas simple
                    const testText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques";
                    
                    console.log('🧪 Test d\'extraction avec le texte:', testText.substring(0, 50) + '...');
                    
                    try {
                        const result = testInstance.analyzeJobLocally(testText);
                        diagnosticResults.testResults = result;
                        
                        console.log('📊 Résultat du test d\'extraction:');
                        console.log('- Titre:', result.title);
                        console.log('- Entreprise:', result.company);
                        console.log('- Lieu:', result.location);
                        console.log('- Compétences:', result.skills);
                        
                        // Analyser le problème
                        if (result.title && result.title.length > 100) {
                            console.log('❌ PROBLÈME DÉTECTÉ: Le titre est trop long');
                            console.log('   Longueur du titre:', result.title.length);
                            console.log('   Le titre capte probablement tout le texte');
                        } else if (result.title && result.title.length < 50) {
                            console.log('✅ Titre de longueur acceptable');
                        }
                        
                    } catch (error) {
                        console.error('❌ Erreur lors du test d\'extraction:', error);
                        diagnosticResults.testResults.error = error.message;
                    }
                    
                } else {
                    console.log('❌ Méthode extractJobTitle non trouvée');
                }
                
            } catch (error) {
                console.error('❌ Erreur lors de la création de l\'instance:', error);
            }
            
        } else {
            diagnosticResults.apiAvailable = false;
            console.log('❌ JobParserAPI non trouvée');
        }
        
        // 6. Vérifier l'UI
        console.log('🔍 Vérification de l\'interface utilisateur...');
        const jobParsingUI = window.JobParsingUI;
        if (jobParsingUI) {
            console.log('✅ JobParsingUI trouvée');
            const apiInstance = jobParsingUI.jobParserInstance();
            console.log('📋 Instance API de l\'UI:', apiInstance ? 'Disponible' : 'Non disponible');
        } else {
            console.log('❌ JobParsingUI non trouvée');
        }
        
        // 7. Afficher le diagnostic dans l'interface
        displayDiagnosticResults(diagnosticResults);
        
        console.log('🔍 === FIN DU DIAGNOSTIC ===');
        
        return diagnosticResults;
    }
    
    function displayDiagnosticResults(results) {
        const debugSection = document.getElementById('debug-section');
        const debugContent = document.getElementById('debug-content');
        
        if (debugSection && debugContent) {
            debugContent.innerHTML = `
                <h4>🔍 Diagnostic JobParserAPI</h4>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>API disponible:</strong> ${results.apiAvailable ? '✅ Oui' : '❌ Non'}</p>
                    <p><strong>Version détectée:</strong> ${results.version}</p>
                    <p><strong>Méthodes disponibles:</strong> ${results.methods.length || 0}</p>
                    
                    ${results.testResults.title ? `
                        <div style="margin-top: 15px; padding: 10px; background: ${results.testResults.title.length > 100 ? '#ffebee' : '#e8f5e8'}; border-radius: 6px;">
                            <p><strong>Test d'extraction:</strong></p>
                            <p><strong>Titre extrait:</strong> "${results.testResults.title.substring(0, 100)}${results.testResults.title.length > 100 ? '...' : ''}"</p>
                            <p><strong>Longueur:</strong> ${results.testResults.title.length} caractères</p>
                            <p><strong>Status:</strong> ${results.testResults.title.length > 100 ? '❌ Problématique' : '✅ OK'}</p>
                        </div>
                    ` : ''}
                    
                    <button onclick="window.AdvancedDiagnostic.runManualTest()" style="margin-top: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🧪 Lancer test manuel
                    </button>
                    
                    <button onclick="window.AdvancedDiagnostic.forceReload()" style="margin-top: 10px; margin-left: 10px; padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🔄 Rechargement forcé
                    </button>
                </div>
            `;
            
            debugSection.style.display = 'block';
        }
    }
    
    function runManualTest() {
        console.log('🧪 Test manuel déclenché...');
        
        const testText = document.getElementById('job-description-text')?.value || 
            "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009";
            
        if (window.JobParserAPI) {
            try {
                const testInstance = new window.JobParserAPI({ debug: true });
                const result = testInstance.analyzeJobLocally(testText);
                
                console.log('📊 Résultat du test manuel:', result);
                alert(`Test terminé!\nTitre: "${result.title}"\nLongueur: ${result.title.length} caractères\n\nVoir la console pour plus de détails.`);
                
            } catch (error) {
                console.error('❌ Erreur lors du test manuel:', error);
                alert('Erreur lors du test: ' + error.message);
            }
        } else {
            alert('JobParserAPI non disponible');
        }
    }
    
    function forceReload() {
        console.log('🔄 Rechargement forcé...');
        // Nettoyer complètement le cache
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => {
                    caches.delete(name);
                });
            });
        }
        
        // Supprimer tous les storage
        localStorage.clear();
        sessionStorage.clear();
        
        // Recharger avec timestamp
        const url = new URL(window.location);
        url.searchParams.set('v', Date.now());
        window.location.href = url.toString();
    }
    
    // Exposer les fonctions
    window.AdvancedDiagnostic = {
        runAdvancedDiagnostic,
        runManualTest,
        forceReload
    };
    
    console.log('✅ Diagnostic avancé JobParserAPI chargé');
    
})();
