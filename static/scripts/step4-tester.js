/**
 * 🧪 NEXTEN - Script de Test Étape 4
 * Test automatisé de la logique conditionnelle et validation
 */

class Step4Tester {
    constructor() {
        this.testResults = [];
        this.init();
    }

    init() {
        console.log('🧪 Initialisation des tests pour l\'étape 4');
        this.createTestButton();
    }

    createTestButton() {
        // Créer un bouton de test visible
        const testButton = document.createElement('button');
        testButton.id = 'test-step4-btn';
        testButton.innerHTML = `
            <i class="fas fa-flask"></i>
            Test Étape 4
        `;
        testButton.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 20px;
            background: linear-gradient(135deg, #8b5cf6, #a855f7);
            color: white;
            padding: 12px 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        `;

        testButton.addEventListener('click', () => {
            this.runAllTests();
        });

        testButton.addEventListener('mouseenter', () => {
            testButton.style.transform = 'translateY(-2px)';
            testButton.style.boxShadow = '0 6px 20px rgba(139, 92, 246, 0.4)';
        });

        testButton.addEventListener('mouseleave', () => {
            testButton.style.transform = 'translateY(0)';
            testButton.style.boxShadow = '0 4px 15px rgba(139, 92, 246, 0.3)';
        });

        document.body.appendChild(testButton);
    }

    async runAllTests() {
        console.log('🚀 Démarrage des tests étape 4...');
        this.showTestModal();
        
        this.testResults = [];

        // Test 1: Navigation vers l'étape 4
        await this.testNavigationToStep4();
        
        // Test 2: Questions obligatoires
        await this.testMandatoryQuestions();
        
        // Test 3: Logique conditionnelle
        await this.testConditionalLogic();
        
        // Test 4: Validation des données
        await this.testDataValidation();
        
        // Test 5: Champs cachés
        await this.testHiddenFields();

        this.displayTestResults();
    }

    async testNavigationToStep4() {
        console.log('📍 Test navigation vers étape 4...');
        
        try {
            // Simuler la navigation vers l'étape 4
            if (window.nextenQuestionnaire) {
                window.nextenQuestionnaire.goToStep(4);
                
                // Vérifier que l'étape 4 est visible
                const step4 = document.getElementById('form-step4');
                const isVisible = step4 && step4.style.display !== 'none' && step4.classList.contains('active');
                
                this.addTestResult('Navigation Étape 4', isVisible, 
                    isVisible ? 'Navigation réussie' : 'Erreur de navigation');
            } else {
                this.addTestResult('Navigation Étape 4', false, 'nextenQuestionnaire non initialisé');
            }
        } catch (error) {
            this.addTestResult('Navigation Étape 4', false, `Erreur: ${error.message}`);
        }
        
        await this.delay(500);
    }

    async testMandatoryQuestions() {
        console.log('❓ Test questions obligatoires...');
        
        const mandatoryQuestions = [
            'timing-options',
            'employment-status-options', 
            'recruitment-status-options'
        ];

        let allQuestionsFound = true;
        let missingQuestions = [];

        mandatoryQuestions.forEach(questionId => {
            const questionElement = document.getElementById(questionId);
            if (!questionElement) {
                allQuestionsFound = false;
                missingQuestions.push(questionId);
            }
        });

        this.addTestResult('Questions Obligatoires', allQuestionsFound, 
            allQuestionsFound ? 'Toutes les questions trouvées' : `Questions manquantes: ${missingQuestions.join(', ')}`);
        
        await this.delay(300);
    }

    async testConditionalLogic() {
        console.log('🔀 Test logique conditionnelle...');
        
        try {
            // Test 1: Sélection "OUI" pour emploi actuel
            const employmentYes = document.querySelector('[data-question="employment-status"][data-value="oui"]');
            if (employmentYes) {
                employmentYes.click();
                
                await this.delay(200);
                
                const yesSection = document.getElementById('employment-yes-section');
                const yesSectionVisible = yesSection && yesSection.classList.contains('active');
                
                this.addTestResult('Logique OUI - Section Emploi', yesSectionVisible, 
                    yesSectionVisible ? 'Section affichée correctement' : 'Section non affichée');
            }

            // Test 2: Sélection "NON" pour emploi actuel
            const employmentNo = document.querySelector('[data-question="employment-status"][data-value="non"]');
            if (employmentNo) {
                employmentNo.click();
                
                await this.delay(200);
                
                const noSection = document.getElementById('employment-no-section');
                const noSectionVisible = noSection && noSection.classList.contains('active');
                
                this.addTestResult('Logique NON - Section Chômage', noSectionVisible, 
                    noSectionVisible ? 'Section affichée correctement' : 'Section non affichée');
            }

        } catch (error) {
            this.addTestResult('Logique Conditionnelle', false, `Erreur: ${error.message}`);
        }
        
        await this.delay(500);
    }

    async testDataValidation() {
        console.log('✅ Test validation des données...');
        
        try {
            // Test validation salaire
            const salaryMin = document.getElementById('current-salary-min');
            const salaryMax = document.getElementById('current-salary-max');
            
            if (salaryMin && salaryMax) {
                salaryMin.value = '50';
                salaryMax.value = '60';
                
                // Simuler l'événement input
                salaryMin.dispatchEvent(new Event('input'));
                salaryMax.dispatchEvent(new Event('input'));
                
                // Vérifier que les valeurs sont sauvegardées
                const hiddenMin = document.getElementById('hidden-current-salary-min');
                const hiddenMax = document.getElementById('hidden-current-salary-max');
                
                const validationWorking = hiddenMin?.value === '50' && hiddenMax?.value === '60';
                
                this.addTestResult('Validation Salaire', validationWorking, 
                    validationWorking ? 'Données sauvegardées correctement' : 'Erreur sauvegarde');
            } else {
                this.addTestResult('Validation Salaire', false, 'Champs salaire non trouvés');
            }

        } catch (error) {
            this.addTestResult('Validation Données', false, `Erreur: ${error.message}`);
        }
        
        await this.delay(300);
    }

    async testHiddenFields() {
        console.log('🔍 Test champs cachés...');
        
        const hiddenFields = [
            'hidden-timing',
            'hidden-employment-status',
            'hidden-recruitment-status',
            'hidden-listening-reasons',
            'hidden-contract-end-reasons'
        ];

        let allFieldsFound = true;
        let missingFields = [];

        hiddenFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!field) {
                allFieldsFound = false;
                missingFields.push(fieldId);
            }
        });

        this.addTestResult('Champs Cachés', allFieldsFound, 
            allFieldsFound ? 'Tous les champs cachés présents' : `Champs manquants: ${missingFields.join(', ')}`);
        
        await this.delay(200);
    }

    addTestResult(testName, success, message) {
        this.testResults.push({
            name: testName,
            success: success,
            message: message,
            timestamp: new Date().toLocaleTimeString()
        });
        
        console.log(`${success ? '✅' : '❌'} ${testName}: ${message}`);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showTestModal() {
        // Supprimer modal existant
        const existingModal = document.getElementById('test-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'test-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 16px;
            padding: 32px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        `;

        modalContent.innerHTML = `
            <div style="text-align: center; margin-bottom: 24px;">
                <h2 style="color: #374151; margin: 0; display: flex; align-items: center; justify-content: center; gap: 12px;">
                    <i class="fas fa-flask" style="color: #8b5cf6;"></i>
                    Tests Étape 4 en cours...
                </h2>
                <div id="test-progress" style="margin-top: 16px;">
                    <div style="width: 100%; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                        <div id="progress-bar" style="width: 0%; height: 100%; background: linear-gradient(135deg, #8b5cf6, #a855f7); transition: width 0.3s ease;"></div>
                    </div>
                    <p id="test-status" style="margin: 12px 0 0 0; color: #6b7280; font-size: 14px;">Initialisation des tests...</p>
                </div>
            </div>
            <div id="test-results-container" style="display: none;">
                <h3 style="color: #374151; margin-bottom: 16px;">Résultats des Tests</h3>
                <div id="test-results-list"></div>
                <div style="text-align: center; margin-top: 24px;">
                    <button id="close-test-modal" style="background: linear-gradient(135deg, #8b5cf6, #a855f7); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        Fermer
                    </button>
                </div>
            </div>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Event listener pour fermer
        document.getElementById('close-test-modal').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    displayTestResults() {
        const progressBar = document.getElementById('progress-bar');
        const testStatus = document.getElementById('test-status');
        const resultsContainer = document.getElementById('test-results-container');
        const resultsList = document.getElementById('test-results-list');

        // Animation de completion
        if (progressBar) {
            progressBar.style.width = '100%';
        }
        
        if (testStatus) {
            testStatus.textContent = 'Tests terminés !';
        }

        setTimeout(() => {
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
            }

            if (resultsList) {
                const successCount = this.testResults.filter(r => r.success).length;
                const totalCount = this.testResults.length;
                
                resultsList.innerHTML = `
                    <div style="margin-bottom: 20px; padding: 16px; background: ${successCount === totalCount ? '#f0fdf4' : '#fef3f2'}; border-radius: 8px; border-left: 4px solid ${successCount === totalCount ? '#10b981' : '#ef4444'};">
                        <div style="font-weight: 600; color: ${successCount === totalCount ? '#065f46' : '#7f1d1d'}; margin-bottom: 8px;">
                            <i class="fas fa-${successCount === totalCount ? 'check-circle' : 'exclamation-triangle'}" style="margin-right: 8px;"></i>
                            Résultat Global: ${successCount}/${totalCount} tests réussis
                        </div>
                        <p style="margin: 0; color: ${successCount === totalCount ? '#047857' : '#991b1b'}; font-size: 14px;">
                            ${successCount === totalCount ? 'Tous les tests sont passés avec succès !' : 'Certains tests ont échoué. Vérifiez les détails ci-dessous.'}
                        </p>
                    </div>
                    ${this.testResults.map(result => `
                        <div style="margin-bottom: 12px; padding: 12px; background: ${result.success ? '#f0fdf4' : '#fef2f2'}; border-radius: 6px; border-left: 3px solid ${result.success ? '#10b981' : '#ef4444'};">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                                <span style="font-weight: 500; color: #374151;">${result.name}</span>
                                <span style="color: ${result.success ? '#10b981' : '#ef4444'}; font-size: 12px;">
                                    <i class="fas fa-${result.success ? 'check' : 'times'}"></i>
                                    ${result.success ? 'RÉUSSI' : 'ÉCHEC'}
                                </span>
                            </div>
                            <div style="font-size: 13px; color: #6b7280;">${result.message}</div>
                            <div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">${result.timestamp}</div>
                        </div>
                    `).join('')}
                `;
            }
        }, 1000);
    }
}

// 🚀 Auto-initialisation du testeur
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.step4Tester = new Step4Tester();
        console.log('🧪 Testeur étape 4 initialisé');
    }, 2000);
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Step4Tester;
}