/**
 * CV Parser Integration - Force Multi-pages Parser
 * Remplace complètement l'ancien système par le parser multi-pages corrigé
 */

(function() {
    'use strict';

    console.log('🔧 Intégration CV Parser Multi-pages - FORÇAGE ACTIF');

    // Configuration forcée
    const FORCE_MULTIPAGE = true;
    const DEBUG_MODE = true;

    /**
     * Classe CVParserIntegration compatible mais utilisant le parser multi-pages
     */
    class CVParserIntegration {
        constructor(options = {}) {
            this.options = {
                useEnhancedParsing: true,
                multiPageSupport: true,
                ...options
            };
            
            // Forcer l'utilisation du parser multi-pages
            if (typeof window.EnhancedCVParserMultipage !== 'undefined') {
                this.parser = new window.EnhancedCVParserMultipage();
                console.log('✅ Parser multi-pages forcé dans CVParserIntegration');
            } else {
                console.error('❌ Parser multi-pages non disponible');
                throw new Error('Parser multi-pages requis');
            }

            // Callbacks
            this.onParsingStart = options.onParsingStart || (() => {});
            this.onParsingComplete = options.onParsingComplete || (() => {});
            this.onParsingError = options.onParsingError || (() => {});
        }

        /**
         * Parse un CV en utilisant FORCÉMENT le parser multi-pages
         */
        async parseCV(file) {
            console.log(`🔍 Parsing multi-pages FORCÉ pour: ${file.name}`);
            
            this.onParsingStart();

            try {
                // Utiliser directement le parser multi-pages corrigé
                const result = await this.parser.parseCV(file);
                
                console.log('📊 Résultat parsing multi-pages:', result);
                
                // Vérifier si on a des données de la page 2
                if (result.data.work_experience && result.data.work_experience.length > 3) {
                    console.log('✅ SUCCÈS: Données multi-pages détectées !');
                } else {
                    console.log('⚠️ Attention: Peu d\'expériences détectées, vérifier le contenu');
                }

                this.onParsingComplete(result);
                return result;
                
            } catch (error) {
                console.error('❌ Erreur parsing multi-pages:', error);
                this.onParsingError(error);
                throw error;
            }
        }
    }

    /**
     * Fonction de création du parser (compatible avec l'ancien système)
     */
    function createEnhancedParser() {
        return new CVParserIntegration({
            useEnhancedParsing: true,
            multiPageSupport: true
        });
    }

    /**
     * Test avec le CV complet de Sabine (incluant page 2)
     */
    function testSabineMultipageCV() {
        console.log('🧪 Test CV Sabine Rivière complet (2 pages)...');
        
        // CV Sabine avec TOUTES les données (pages 1 + 2)
        const sabineFullCV = `
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

--- PAGE 2 ---

04/2019 - 08/2019
EXECUTIVE ASSISTANT du CEO (CDD : CONGÉ MATERNITÉ)
Socavim-Vallat, Paris / Annecy

10/2017 - 03/2019
ASSISTANTE PERSONNELLE
Famille Française, Paris / Monaco

06/2017 - 10/2017
EXECUTIVE ASSISTANTE du CEO
Start-Up Oyst E-Corps Adtech Services, Paris

02/2012 - 07/2015
ASSISTANTE PERSONNELLE
Oligarque Russe, Moscou / Londres / Paris / Vienne

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
French - Natif
Anglais - Courant

Formation
- 01/2006 DIPLÔME D'ÉTUDES SUPÉRIEURES ESVE, Paris
- 01/2014 Business & Economics, BA Birkbeck University, London
        `;

        try {
            const parser = new window.EnhancedCVParserMultipage();
            const result = parser.parseCV(sabineFullCV);
            
            console.log('📊 Résultats test Sabine complet:', result);
            
            // Vérifications spécifiques multi-pages
            const experiences = result.data.work_experience || [];
            const education = result.data.education || [];
            
            console.log('🎯 Vérifications multi-pages:');
            console.log(`- Expériences détectées: ${experiences.length} (attendu: ≥6)`);
            console.log(`- Formations détectées: ${education.length} (attendu: ≥2)`);
            
            // Vérifier les expériences spécifiques de la page 2
            const hasSocavim = experiences.some(exp => 
                exp.company && exp.company.toLowerCase().includes('socavim')
            );
            const hasOyst = experiences.some(exp => 
                exp.company && exp.company.toLowerCase().includes('oyst')
            );
            const hasOligarque = experiences.some(exp => 
                exp.company && exp.company.toLowerCase().includes('oligarque') ||
                exp.title && exp.title.toLowerCase().includes('oligarque')
            );
            
            console.log(`- Socavim-Vallat détecté: ${hasSocavim ? '✅' : '❌'}`);
            console.log(`- Start-Up Oyst détecté: ${hasOyst ? '✅' : '❌'}`);
            console.log(`- Oligarque Russe détecté: ${hasOligarque ? '✅' : '❌'}`);
            
            // Vérifier les formations
            const hasESVE = education.some(edu => 
                edu.institution && edu.institution.toLowerCase().includes('esve') ||
                edu.degree && edu.degree.toLowerCase().includes('esve')
            );
            const hasBirkbeck = education.some(edu => 
                edu.institution && edu.institution.toLowerCase().includes('birkbeck')
            );
            
            console.log(`- Formation ESVE détectée: ${hasESVE ? '✅' : '❌'}`);
            console.log(`- Formation Birkbeck détectée: ${hasBirkbeck ? '✅' : '❌'}`);
            
            // Score final
            const score = [
                experiences.length >= 6,
                hasSocavim,
                hasOyst,
                hasOligarque,
                hasESVE,
                hasBirkbeck
            ].filter(Boolean).length;
            
            console.log(`🏆 Score multi-pages: ${score}/6 (${Math.round(score/6*100)}%)`);
            
            if (score >= 5) {
                console.log('✅ TEST MULTI-PAGES RÉUSSI - Toutes les pages traitées !');
            } else {
                console.log('❌ TEST MULTI-PAGES ÉCHOUÉ - Vérifier l\'intégration');
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ Erreur test Sabine:', error);
            return null;
        }
    }

    /**
     * Test de lecture PDF réelle (pour fichiers uploadés)
     */
    async function testRealPDFParsing(file) {
        if (!file) {
            console.log('📄 Utilisez: testRealPDFParsing(votrefichier.pdf)');
            return;
        }

        console.log(`🔍 Test parsing PDF réel: ${file.name}`);
        
        try {
            const parser = new window.EnhancedCVParserMultipage();
            const result = await parser.parseCV(file);
            
            console.log('📊 Résultat parsing PDF:', result);
            console.log(`📄 Pages traitées: ${result.parsing_stats?.pdf_support ? 'Toutes' : 'Limitées'}`);
            console.log(`📈 Contenu extrait: ${result.parsing_stats?.content_length} caractères`);
            
            return result;
            
        } catch (error) {
            console.error('❌ Erreur parsing PDF:', error);
            return null;
        }
    }

    /**
     * Installation et export des fonctions
     */
    function installMultipageParser() {
        // Exporter les classes et fonctions globalement
        window.CVParserIntegration = CVParserIntegration;
        window.createEnhancedParser = createEnhancedParser;
        window.testSabineMultipageCV = testSabineMultipageCV;
        window.testRealPDFParsing = testRealPDFParsing;
        
        // Instance globale pour compatibilité
        if (typeof window.EnhancedCVParserMultipage !== 'undefined') {
            window.commitmentMultipageParser = new window.EnhancedCVParserMultipage();
        }
        
        console.log('✅ Parser multi-pages intégré et forcé');
        console.log('🧪 Tests disponibles:');
        console.log('  - testSabineMultipageCV()');
        console.log('  - testRealPDFParsing(file)');
    }

    // Installation automatique
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installMultipageParser);
    } else {
        installMultipageParser();
    }

    // Installation différée pour s'assurer que tout est chargé
    setTimeout(() => {
        if (typeof window.EnhancedCVParserMultipage !== 'undefined') {
            installMultipageParser();
            console.log('🎯 Parser multi-pages FORCÉ et opérationnel !');
        } else {
            console.error('❌ Parser multi-pages non trouvé après délai');
        }
    }, 1000);

})();
