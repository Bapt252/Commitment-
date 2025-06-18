/**
 * Tests pour le Parser CV Optimisé Commitment
 * Fichier de validation et exemples d'utilisation
 */

// Données de test : CV de Sabine Rivière (Executive Assistant)
const testCVSabine = `
Sabine Rivière
Executive Assistant

E-mail: sabine.riviere04@gmail.com
Téléphone: +33665733921

Expérience

06/2024 - 01/2025
Executive Assistant : Direction Financière Audit / Fiscalité / Trésorerie
Maison Christian Dior Couture : Intérim 8 mois, Paris 08

06/2023 - 05/2024
EXECUTIVE ASSISTANT : Direction Fonds de Fonds COMEX / CODIR / CMG
BPI FRANCE, Paris

08/2019 - 05/2023
EXECUTIVE ASSISTANT/ ASSISTANTE PERSONNELLE de la CEO
Les Secrets de Loly, Paris

Compétences
Tenue d'agendas
Suivi budgétaire
Préparation de rapports
Autonomie
Sens de la communication
Excellente organisation du travail

Informatique
Microsoft
Concur
Coupa
SAP
Pennylane
Google / Outlook

Langues
French - A1
Anglais - A1

Formation
- 01/2006 DIPLÔME D'ÉTUDES SUPÉRIEURES ESVE, Paris
- 01/2014 Business & Economics, BA Birkbeck University, London
`;

// Données de test : CV Développeur
const testCVDeveloper = `
Jean Dupont
Développeur Full Stack Senior

Email: jean.dupont@email.com
Tel: 01 23 45 67 89

EXPERIENCE PROFESSIONNELLE

2022 - Présent
Développeur Full Stack Senior
TechCorp Solutions, Paris
- Développement d'applications React/Node.js
- Architecture microservices avec Docker
- Gestion d'équipe de 5 développeurs

2020 - 2022
Développeur Front-End
WebAgency Digital, Lyon
- Création d'interfaces React et Vue.js
- Intégration APIs REST
- Optimisation performance web

COMPETENCES TECHNIQUES
JavaScript, TypeScript, React, Vue.js, Node.js, Express
Python, Django, Flask
HTML5, CSS3, SASS, Bootstrap
MySQL, PostgreSQL, MongoDB
Git, Docker, Kubernetes, AWS
Agile, Scrum, DevOps

LOGICIELS
Visual Studio Code, WebStorm, Docker Desktop
Figma, Adobe Photoshop, Postman
Jira, Confluence, Slack

LANGUES
Français - Natif
Anglais - Courant (C1)
Espagnol - Intermédiaire (B2)

FORMATION
2019 - Master Informatique, Université Lyon 1
2017 - Licence Informatique, Université Lyon 1
`;

/**
 * Classe de test pour valider le parser optimisé
 */
class CommitmentParserTests {
    constructor() {
        this.tests = [];
        this.results = [];
    }

    /**
     * Lance tous les tests
     */
    async runAllTests() {
        console.log('🧪 Démarrage des tests du parser CV optimisé Commitment...');
        
        // Vérifier que les composants sont chargés
        this.testComponentsLoaded();
        
        // Tests avec CV Executive Assistant
        await this.testSabineCV();
        
        // Tests avec CV Développeur
        await this.testDeveloperCV();
        
        // Tests de performance
        this.testPerformance();
        
        // Tests d'intégration
        this.testIntegration();
        
        // Rapport final
        this.generateReport();
    }

    /**
     * Test de chargement des composants
     */
    testComponentsLoaded() {
        console.log('🔍 Test: Chargement des composants...');
        
        const tests = [
            { name: 'EnhancedCVParser', exists: typeof window.EnhancedCVParser !== 'undefined' },
            { name: 'CommitmentOptimizedPrompt', exists: typeof window.CommitmentOptimizedPrompt !== 'undefined' },
            { name: 'commitmentEnhancedParser', exists: typeof window.commitmentEnhancedParser !== 'undefined' },
            { name: 'testCommitmentParser', exists: typeof window.testCommitmentParser === 'function' },
            { name: 'compareCommitmentParsers', exists: typeof window.compareCommitmentParsers === 'function' }
        ];
        
        tests.forEach(test => {
            if (test.exists) {
                console.log(`✅ ${test.name} chargé`);
                this.addResult('components', test.name, true);
            } else {
                console.log(`❌ ${test.name} manquant`);
                this.addResult('components', test.name, false);
            }
        });
    }

    /**
     * Test avec le CV de Sabine Rivière
     */
    async testSabineCV() {
        console.log('🧪 Test: CV Executive Assistant (Sabine Rivière)...');
        
        if (typeof window.commitmentEnhancedParser === 'undefined') {
            console.log('❌ Parser non disponible');
            return;
        }
        
        try {
            const result = window.commitmentEnhancedParser.parseCV(testCVSabine);
            
            // Validation des résultats
            const validations = [
                { 
                    name: 'Nom détecté', 
                    test: result.data.personal_info.name === 'Sabine Rivière' 
                },
                { 
                    name: 'Email détecté', 
                    test: result.data.personal_info.email === 'sabine.riviere04@gmail.com' 
                },
                { 
                    name: 'Téléphone détecté', 
                    test: result.data.personal_info.phone === '+33665733921' 
                },
                { 
                    name: 'Poste actuel', 
                    test: result.data.current_position === 'Executive Assistant' 
                },
                { 
                    name: 'Compétences multiples', 
                    test: result.data.skills.length >= 5 
                },
                { 
                    name: 'Logiciels détectés', 
                    test: result.data.software.length >= 5 
                },
                { 
                    name: 'Langues avec niveaux', 
                    test: result.data.languages.length >= 2 && 
                          result.data.languages.every(lang => lang.level !== 'À évaluer')
                },
                { 
                    name: 'Expériences avec dates', 
                    test: result.data.work_experience.length >= 3 &&
                          result.data.work_experience.every(exp => 
                            exp.start_date !== 'À définir' && exp.end_date !== 'À définir')
                },
                { 
                    name: 'Formation détectée', 
                    test: result.data.education && result.data.education.length >= 2
                }
            ];
            
            validations.forEach(validation => {
                if (validation.test) {
                    console.log(`✅ ${validation.name}`);
                    this.addResult('sabine_cv', validation.name, true);
                } else {
                    console.log(`❌ ${validation.name}`);
                    this.addResult('sabine_cv', validation.name, false);
                }
            });
            
            // Log des données extraites pour debug
            console.log('📊 Données extraites Sabine:', {
                skills_count: result.data.skills.length,
                software_count: result.data.software.length,
                languages_count: result.data.languages.length,
                experience_count: result.data.work_experience.length,
                education_count: result.data.education?.length || 0
            });
            
        } catch (error) {
            console.log('❌ Erreur test Sabine CV:', error);
            this.addResult('sabine_cv', 'parsing_error', false, error.message);
        }
    }

    /**
     * Test avec un CV de développeur
     */
    async testDeveloperCV() {
        console.log('🧪 Test: CV Développeur...');
        
        if (typeof window.commitmentEnhancedParser === 'undefined') {
            console.log('❌ Parser non disponible');
            return;
        }
        
        try {
            const result = window.commitmentEnhancedParser.parseCV(testCVDeveloper);
            
            const validations = [
                { 
                    name: 'Nom développeur détecté', 
                    test: result.data.personal_info.name === 'Jean Dupont' 
                },
                { 
                    name: 'Compétences techniques', 
                    test: result.data.skills.some(skill => 
                        skill.toLowerCase().includes('javascript') || 
                        skill.toLowerCase().includes('react') ||
                        skill.toLowerCase().includes('node'))
                },
                { 
                    name: 'Logiciels dev détectés', 
                    test: result.data.software.some(software => 
                        software.toLowerCase().includes('visual studio') ||
                        software.toLowerCase().includes('docker') ||
                        software.toLowerCase().includes('figma'))
                },
                { 
                    name: 'Langues multiples', 
                    test: result.data.languages.length >= 2
                },
                { 
                    name: 'Expériences développeur', 
                    test: result.data.work_experience.some(exp => 
                        exp.title.toLowerCase().includes('développeur'))
                }
            ];
            
            validations.forEach(validation => {
                if (validation.test) {
                    console.log(`✅ ${validation.name}`);
                    this.addResult('developer_cv', validation.name, true);
                } else {
                    console.log(`❌ ${validation.name}`);
                    this.addResult('developer_cv', validation.name, false);
                }
            });
            
        } catch (error) {
            console.log('❌ Erreur test Developer CV:', error);
            this.addResult('developer_cv', 'parsing_error', false, error.message);
        }
    }

    /**
     * Tests de performance
     */
    testPerformance() {
        console.log('🧪 Test: Performance...');
        
        if (typeof window.commitmentEnhancedParser === 'undefined') {
            console.log('❌ Parser non disponible');
            return;
        }
        
        // Test de vitesse
        const startTime = performance.now();
        
        try {
            const result = window.commitmentEnhancedParser.parseCV(testCVSabine);
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            console.log(`⏱️ Temps de parsing: ${duration.toFixed(2)}ms`);
            
            const performanceTests = [
                { 
                    name: 'Parsing rapide (< 100ms)', 
                    test: duration < 100 
                },
                { 
                    name: 'Données cohérentes', 
                    test: result && result.data && result.source 
                },
                { 
                    name: 'Statistiques présentes', 
                    test: result.parsing_stats && result.parsing_stats.content_length > 0
                }
            ];
            
            performanceTests.forEach(test => {
                if (test.test) {
                    console.log(`✅ ${test.name}`);
                    this.addResult('performance', test.name, true);
                } else {
                    console.log(`❌ ${test.name}`);
                    this.addResult('performance', test.name, false);
                }
            });
            
        } catch (error) {
            console.log('❌ Erreur test performance:', error);
            this.addResult('performance', 'performance_error', false, error.message);
        }
    }

    /**
     * Tests d'intégration
     */
    testIntegration() {
        console.log('🧪 Test: Intégration...');
        
        const integrationTests = [
            { 
                name: 'Instance globale disponible', 
                test: typeof window.commitmentEnhancedParser === 'object' 
            },
            { 
                name: 'Fonctions de test disponibles', 
                test: typeof window.testCommitmentParser === 'function' &&
                      typeof window.compareCommitmentParsers === 'function'
            },
            { 
                name: 'Auto-installation réussie', 
                test: typeof window.autoInstallCommitmentParser === 'function'
            },
            { 
                name: 'Prompts optimisés chargés', 
                test: typeof window.CommitmentOptimizedPrompt !== 'undefined'
            }
        ];
        
        integrationTests.forEach(test => {
            if (test.test) {
                console.log(`✅ ${test.name}`);
                this.addResult('integration', test.name, true);
            } else {
                console.log(`❌ ${test.name}`);
                this.addResult('integration', test.name, false);
            }
        });
    }

    /**
     * Ajoute un résultat de test
     */
    addResult(category, testName, passed, error = null) {
        this.results.push({
            category,
            testName,
            passed,
            error,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Génère le rapport final
     */
    generateReport() {
        console.log('\n📊 RAPPORT DE TESTS - Parser CV Optimisé Commitment\n');
        
        const categories = [...new Set(this.results.map(r => r.category))];
        let totalPassed = 0;
        let totalTests = 0;
        
        categories.forEach(category => {
            const categoryResults = this.results.filter(r => r.category === category);
            const passed = categoryResults.filter(r => r.passed).length;
            const total = categoryResults.length;
            
            console.log(`📁 ${category.toUpperCase()}: ${passed}/${total} tests réussis`);
            
            categoryResults.forEach(result => {
                const icon = result.passed ? '✅' : '❌';
                console.log(`  ${icon} ${result.testName}`);
                if (result.error) {
                    console.log(`    Erreur: ${result.error}`);
                }
            });
            
            console.log('');
            totalPassed += passed;
            totalTests += total;
        });
        
        const successRate = ((totalPassed / totalTests) * 100).toFixed(1);
        
        console.log(`🎯 RÉSULTAT GLOBAL: ${totalPassed}/${totalTests} (${successRate}%)`);
        
        if (successRate >= 90) {
            console.log('🎉 EXCELLENT! Le parser optimisé fonctionne parfaitement.');
        } else if (successRate >= 75) {
            console.log('✅ BON! Le parser optimisé fonctionne bien avec quelques améliorations possibles.');
        } else {
            console.log('⚠️ ATTENTION! Le parser optimisé nécessite des corrections.');
        }
        
        // Stockage des résultats pour analyse
        window.commitmentTestResults = {
            totalTests,
            totalPassed,
            successRate: parseFloat(successRate),
            details: this.results,
            timestamp: new Date().toISOString()
        };
        
        console.log('\n💾 Résultats stockés dans window.commitmentTestResults');
    }
}

/**
 * Fonction de test rapide pour la console
 */
function runCommitmentParserTests() {
    const tester = new CommitmentParserTests();
    return tester.runAllTests();
}

/**
 * Test spécifique pour un CV custom
 */
function testCustomCV(cvContent) {
    if (typeof window.commitmentEnhancedParser === 'undefined') {
        console.log('❌ Parser optimisé non disponible');
        return null;
    }
    
    try {
        console.log('🧪 Test CV personnalisé...');
        const result = window.commitmentEnhancedParser.parseCV(cvContent);
        
        console.log('📊 Résultats:', {
            nom: result.data.personal_info.name,
            email: result.data.personal_info.email,
            téléphone: result.data.personal_info.phone,
            poste: result.data.current_position,
            compétences: result.data.skills.length,
            logiciels: result.data.software.length,
            langues: result.data.languages.length,
            expériences: result.data.work_experience.length,
            formations: result.data.education?.length || 0
        });
        
        return result;
    } catch (error) {
        console.log('❌ Erreur test CV personnalisé:', error);
        return null;
    }
}

// Export pour utilisation
if (typeof window !== 'undefined') {
    window.runCommitmentParserTests = runCommitmentParserTests;
    window.testCustomCV = testCustomCV;
    window.CommitmentParserTests = CommitmentParserTests;
}

console.log('🧪 Fichier de tests Commitment chargé!');
console.log('📞 Utilisation: runCommitmentParserTests() ou testCustomCV(cvContent)');
