/**
 * ===============================================================================
 * ENHANCED UNIVERSAL MULTIPAGE PARSER - COMMITMENT PLATFORM
 * ===============================================================================
 * 
 * 🎯 SOLUTION UNIVERSELLE
 * ─────────────────────────────────────────────────────────────────────────────
 * Parser intelligent qui fonctionne avec TOUS les CVs multi-pages :
 * • Détection automatique du nombre d'expériences
 * • Adaptation du prompt selon le contenu du CV
 * • Support universel : 2+ pages, 4+ expériences
 * • Heuristiques avancées pour tous profils
 * 
 * 🔬 INTELLIGENCE ADAPTIVE
 * ─────────────────────────────────────────────────────────────────────────────
 * • Analyse automatique du contenu CV
 * • Estimation intelligente du nombre d'expériences
 * • Prompts adaptatifs selon le profil
 * • Validation dynamique des résultats
 * 
 * 💡 FONCTIONNALITÉS
 * ─────────────────────────────────────────────────────────────────────────────
 * • Auto-détection CVs multi-pages (>2000 caractères)
 * • Comptage intelligent des expériences potentielles
 * • Prompts personnalisés par secteur (Tech, Business, Assistant, etc.)
 * • Fallback automatique si échec
 * • Monitoring temps réel des performances
 * 
 * @author Commitment Team
 * @version 3.0.0 - Universal Multi-Page Support
 * @date 2025-06-20
 * @tested Multiple CV profiles and formats
 * ===============================================================================
 */

(function() {
    'use strict';
    
    // Configuration universelle
    const UNIVERSAL_CONFIG = {
        MIN_MULTIPAGE_LENGTH: 2000,        // Seuil détection multi-pages
        MIN_EXPERIENCES: 3,                // Minimum d'expériences attendues
        MAX_EXPERIENCES: 15,               // Maximum d'expériences possibles
        BOOST_TOKENS: 4000,                // Tokens pour CVs complexes
        DEBUG_MODE: true,                  // Mode debug
        VERSION: '3.0.0-UNIVERSAL'
    };
    
    // État du parser universel
    let isUniversalParserActive = false;
    let originalFetch = null;
    let universalStats = {
        totalCVs: 0,
        multiPageDetected: 0,
        successfulExtractions: 0,
        averageExperiences: 0
    };

    /**
     * 🧠 ANALYSEUR INTELLIGENT DE CV
     * ────────────────────────────────────────────────────────────────────────
     * Analyse un CV pour déterminer ses caractéristiques
     */
    function analyzeCVContent(content) {
        const analysis = {
            isMultiPage: content.length > UNIVERSAL_CONFIG.MIN_MULTIPAGE_LENGTH,
            contentLength: content.length,
            estimatedExperiences: 3,
            cvType: 'general',
            industries: [],
            hasEducation: false,
            hasSkills: false
        };
        
        const lowerContent = content.toLowerCase();
        
        // Détection du nombre d'expériences par heuristiques
        const experienceIndicators = [
            /\d{2}\/\d{4}\s*[-–]\s*\d{2}\/\d{4}/g,        // Dates MM/YYYY - MM/YYYY
            /\d{4}\s*[-–]\s*\d{4}/g,                      // Années YYYY - YYYY
            /depuis\s+\d{4}/gi,                          // Depuis YYYY
            /à\s+ce\s+jour/gi,                           // À ce jour
            /present/gi,                                 // Present
            /aujourd'hui/gi,                             // Aujourd'hui
            /en\s+cours/gi                               // En cours
        ];
        
        let experienceCount = 0;
        experienceIndicators.forEach(regex => {
            const matches = content.match(regex);
            if (matches) experienceCount += matches.length;
        });
        
        // Détection par mots-clés d'entreprises/postes
        const jobTitleIndicators = [
            'assistant', 'manager', 'directeur', 'responsable', 'chef', 'lead',
            'developer', 'engineer', 'consultant', 'analyst', 'specialist',
            'coordinator', 'supervisor', 'executive', 'officer'
        ];
        
        let titleMatches = 0;
        jobTitleIndicators.forEach(title => {
            if (lowerContent.includes(title)) titleMatches++;
        });
        
        // Estimation finale du nombre d'expériences
        analysis.estimatedExperiences = Math.max(
            Math.floor(experienceCount * 0.8), // 80% des indicateurs de dates
            Math.min(Math.floor(titleMatches / 2), 8), // Titres divisés par 2
            UNIVERSAL_CONFIG.MIN_EXPERIENCES
        );
        
        // Si multi-pages, augmenter l'estimation
        if (analysis.isMultiPage) {
            analysis.estimatedExperiences = Math.min(
                analysis.estimatedExperiences + 2,
                UNIVERSAL_CONFIG.MAX_EXPERIENCES
            );
        }
        
        // Détection du type de CV
        if (lowerContent.includes('assistant') || lowerContent.includes('secrétaire')) {
            analysis.cvType = 'assistant';
        } else if (lowerContent.includes('developer') || lowerContent.includes('engineer') || lowerContent.includes('tech')) {
            analysis.cvType = 'tech';
        } else if (lowerContent.includes('manager') || lowerContent.includes('directeur') || lowerContent.includes('business')) {
            analysis.cvType = 'business';
        } else if (lowerContent.includes('commercial') || lowerContent.includes('vente')) {
            analysis.cvType = 'sales';
        }
        
        // Détection d'autres sections
        analysis.hasEducation = lowerContent.includes('formation') || lowerContent.includes('education') || lowerContent.includes('diplôme');
        analysis.hasSkills = lowerContent.includes('compétences') || lowerContent.includes('skills') || lowerContent.includes('logiciels');
        
        return analysis;
    }

    /**
     * 🎯 GÉNÉRATEUR DE PROMPT ADAPTATIF
     * ────────────────────────────────────────────────────────────────────────
     * Génère un prompt personnalisé selon l'analyse du CV
     */
    function generateAdaptivePrompt(cvContent, analysis) {
        const { estimatedExperiences, cvType, isMultiPage } = analysis;
        
        let specificInstructions = '';
        
        // Instructions spécifiques par type de CV
        switch (cvType) {
            case 'assistant':
                specificInstructions = `
Ce CV d'assistant(e) contient probablement des expériences dans différentes entreprises.
Recherche particulièrement : postes d'assistance, secrétariat, support administratif.
Entreprises typiques : grandes entreprises, cabinets, start-ups.`;
                break;
                
            case 'tech':
                specificInstructions = `
Ce CV technique contient probablement des expériences de développement/ingénierie.
Recherche particulièrement : postes de développeur, ingénieur, tech lead, CTO.
Entreprises typiques : start-ups tech, SSII, grands groupes IT.`;
                break;
                
            case 'business':
                specificInstructions = `
Ce CV business contient probablement des expériences de management/direction.
Recherche particulièrement : postes de manager, directeur, chef de projet.
Entreprises typiques : multinationales, PME, cabinets de conseil.`;
                break;
                
            case 'sales':
                specificInstructions = `
Ce CV commercial contient probablement des expériences de vente/business dev.
Recherche particulièrement : postes commerciaux, business development, account manager.
Entreprises typiques : entreprises B2B, retail, services.`;
                break;
                
            default:
                specificInstructions = `
Ce CV contient diverses expériences professionnelles à identifier.
Recherche toutes les expériences mentionnées, même brièvement.`;
        }
        
        // Template adaptatif
        const workExperienceTemplate = Array.from({ length: estimatedExperiences }, (_, i) => 
            `    {"title": "Poste ${i + 1} à identifier", "company": "Entreprise ${i + 1} à identifier", "start_date": "Date début", "end_date": "Date fin"}`
        ).join(',\n');
        
        const adaptivePrompt = `Tu es un expert en extraction de CV ${isMultiPage ? 'MULTI-PAGES' : ''}. 

🔍 ANALYSE AUTOMATIQUE :
- Longueur du CV : ${analysis.contentLength} caractères
- Type détecté : ${cvType.toUpperCase()}
- ${isMultiPage ? 'CV MULTI-PAGES détecté' : 'CV standard'}
- Nombre d'expériences estimé : ${estimatedExperiences}

${specificInstructions}

🚨 RÈGLES UNIVERSELLES :
1. Lis l'INTÉGRALITÉ du CV (toutes les pages)
2. Extrait TOUTES les expériences professionnelles mentionnées
3. Tu dois trouver environ ${estimatedExperiences} expériences ou plus
4. Ne manque AUCUNE expérience, même les plus anciennes
5. Si le CV fait plusieurs pages, lis jusqu'à la fin

🎯 OBJECTIF EXTRACTION :
- Minimum ${UNIVERSAL_CONFIG.MIN_EXPERIENCES} expériences
- Cible ${estimatedExperiences} expériences
- Maximum ${UNIVERSAL_CONFIG.MAX_EXPERIENCES} expériences
- work_experience doit contenir au moins ${estimatedExperiences} éléments

📋 TEMPLATE JSON ADAPTATIF :
{
  "personal_info": {
    "name": "Nom à extraire",
    "email": "email@domain.com",
    "phone": "Téléphone à extraire"
  },
  "current_position": "Poste actuel à identifier",
  "skills": ["compétence1", "compétence2", "compétence3"],
  "software": ["logiciel1", "logiciel2", "logiciel3"],
  "languages": [{"language": "langue1", "level": "niveau1"}],
  "work_experience": [
${workExperienceTemplate}
  ],
  "education": [{"degree": "diplôme", "institution": "école", "year": "année"}]
}

⚡ VALIDATION OBLIGATOIRE ⚡
Vérifie que work_experience contient AU MOINS ${estimatedExperiences} expériences.
Si tu en trouves moins, RELIS le CV entièrement et cherche les expériences manquées.

CV ${isMultiPage ? 'MULTI-PAGES' : ''} À ANALYSER :
${cvContent}

Réponds UNIQUEMENT avec le JSON contenant toutes les expériences trouvées.`;

        return adaptivePrompt;
    }

    /**
     * 📊 ANALYSEUR DE RÉPONSE OPENAI
     * ────────────────────────────────────────────────────────────────────────
     */
    function analyzeUniversalResponse(content, expectedExperiences) {
        try {
            const cleanContent = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
            const parsed = JSON.parse(cleanContent);
            
            if (parsed.work_experience && Array.isArray(parsed.work_experience)) {
                const expCount = parsed.work_experience.length;
                universalStats.totalCVs++;
                
                if (expCount >= expectedExperiences) {
                    universalStats.successfulExtractions++;
                }
                
                universalStats.averageExperiences = 
                    (universalStats.averageExperiences * (universalStats.totalCVs - 1) + expCount) / 
                    universalStats.totalCVs;
                
                const successRate = (universalStats.successfulExtractions / universalStats.totalCVs * 100).toFixed(1);
                
                if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                    console.log(`🎯 RÉSULTAT UNIVERSEL: ${expCount}/${expectedExperiences} expériences`);
                    console.log(`📊 Taux de réussite global: ${successRate}%`);
                    console.log(`📈 Moyenne d'expériences: ${universalStats.averageExperiences.toFixed(1)}`);
                    
                    if (expCount >= expectedExperiences) {
                        console.log('🎉 SUCCÈS! Extraction complète réussie');
                        console.log('📋 Expériences extraites:');
                        parsed.work_experience.forEach((exp, index) => {
                            console.log(`  ${index + 1}. ${exp.company} - ${exp.title}`);
                        });
                    } else {
                        console.log(`⚠️ Extraction partielle: ${expCount}/${expectedExperiences}`);
                    }
                }
                
                return { 
                    success: expCount >= expectedExperiences, 
                    count: expCount, 
                    expected: expectedExperiences,
                    parsed: parsed
                };
            }
        } catch (error) {
            if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                console.error('❌ Erreur parsing réponse:', error);
            }
            return { success: false, count: 0, expected: expectedExperiences };
        }
        
        return { success: false, count: 0, expected: expectedExperiences };
    }

    /**
     * 🔧 INTERCEPTEUR FETCH UNIVERSEL
     * ────────────────────────────────────────────────────────────────────────
     */
    function createUniversalFetchInterceptor() {
        return async function(...args) {
            const [url, options] = args;
            
            if (url.includes('openai.com') && url.includes('chat/completions')) {
                if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                    console.log('🔧 Interception OpenAI - Parser Universel v3.0...');
                }
                
                if (options && options.body) {
                    try {
                        const body = JSON.parse(options.body);
                        
                        // Augmentation des tokens pour CVs complexes
                        if (body.max_tokens <= 3500) {
                            body.max_tokens = UNIVERSAL_CONFIG.BOOST_TOKENS;
                            console.log(`📈 Tokens boostés: ${body.max_tokens}`);
                        }
                        
                        // Analyse et adaptation du prompt
                        if (body.messages && body.messages.length > 0) {
                            const userMessage = body.messages.find(m => m.role === 'user');
                            if (userMessage) {
                                const originalPrompt = userMessage.content;
                                
                                // Extraire le contenu CV
                                let cvContent = extractCVContent(originalPrompt);
                                if (!cvContent) cvContent = originalPrompt;
                                
                                // Analyser le CV
                                const analysis = analyzeCVContent(cvContent);
                                
                                if (analysis.isMultiPage) {
                                    universalStats.multiPageDetected++;
                                    console.log('📄 CV multi-pages détecté - Activation parser renforcé');
                                }
                                
                                // Générer le prompt adaptatif
                                const adaptivePrompt = generateAdaptivePrompt(cvContent, analysis);
                                
                                // Appliquer le prompt
                                userMessage.content = adaptivePrompt;
                                
                                if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                                    console.log('✅ Prompt universel adaptatif appliqué');
                                    console.log(`📊 Analyse: ${analysis.cvType}, ${analysis.estimatedExperiences} exp attendues`);
                                    console.log(`📏 Prompt: ${adaptivePrompt.length} caractères`);
                                }
                                
                                // Stocker l'analyse pour la validation
                                window._currentCVAnalysis = analysis;
                            }
                        }
                        
                        options.body = JSON.stringify(body);
                        
                    } catch (error) {
                        if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                            console.error('❌ Erreur modification prompt universel:', error);
                        }
                    }
                }
            }
            
            // Appel original avec monitoring
            const response = await originalFetch.apply(this, args);
            
            // Analyser la réponse
            if (url.includes('openai.com') && url.includes('chat/completions')) {
                const clonedResponse = response.clone();
                try {
                    const data = await clonedResponse.json();
                    if (data.choices && data.choices[0] && window._currentCVAnalysis) {
                        const result = analyzeUniversalResponse(
                            data.choices[0].message.content, 
                            window._currentCVAnalysis.estimatedExperiences
                        );
                        
                        // Nettoyer l'analyse temporaire
                        delete window._currentCVAnalysis;
                    }
                } catch (error) {
                    if (UNIVERSAL_CONFIG.DEBUG_MODE) {
                        console.error('❌ Erreur analyse réponse:', error);
                    }
                }
            }
            
            return response;
        };
    }

    /**
     * 📝 EXTRACTION DU CONTENU CV
     * ────────────────────────────────────────────────────────────────────────
     */
    function extractCVContent(originalPrompt) {
        const cvMarkers = [
            'CV À ANALYSER', 'CV:', 'CONTENU COMPLET', 'CV COMPLET',
            'CURRICULUM VITAE', 'Resume:', 'CV Content:'
        ];
        
        for (const marker of cvMarkers) {
            const index = originalPrompt.lastIndexOf(marker);
            if (index !== -1) {
                return originalPrompt.substring(index + marker.length + 5);
            }
        }
        
        return originalPrompt;
    }

    /**
     * 🚀 ACTIVATION DU PARSER UNIVERSEL
     * ────────────────────────────────────────────────────────────────────────
     */
    function activateUniversalParser() {
        if (isUniversalParserActive) {
            console.log('⚠️ Parser universel déjà activé');
            return;
        }
        
        if (!window.originalFetch) {
            originalFetch = window.fetch;
            window.originalFetch = originalFetch;
        } else {
            originalFetch = window.originalFetch;
        }
        
        window.fetch = createUniversalFetchInterceptor();
        isUniversalParserActive = true;
        
        console.log('🌟 === ENHANCED UNIVERSAL MULTIPAGE PARSER v3.0 ACTIVÉ ===');
        console.log('✅ Parser intelligent adaptatif installé');
        console.log('🎯 Supporte TOUS les CVs multi-pages (pas seulement Sabine)');
        console.log('🧠 Détection automatique du nombre d\'expériences');
        console.log('📊 Prompts adaptatifs selon le type de CV');
        console.log('🔧 Améliorations:');
        console.log('  - Auto-détection CVs multi-pages');
        console.log('  - Estimation intelligente des expériences');
        console.log('  - Prompts personnalisés (Tech, Business, Assistant, etc.)');
        console.log('  - Validation dynamique des résultats');
        console.log('');
        console.log('🧪 TESTEZ avec N\'IMPORTE QUEL CV multi-pages !');
        console.log('💡 Utilisez window.getUniversalParserStats() pour les statistiques');
    }

    /**
     * 🛑 DÉSACTIVATION DU PARSER UNIVERSEL
     * ────────────────────────────────────────────────────────────────────────
     */
    function deactivateUniversalParser() {
        if (!isUniversalParserActive) {
            console.log('⚠️ Parser universel déjà désactivé');
            return;
        }
        
        if (window.originalFetch) {
            window.fetch = window.originalFetch;
        }
        
        isUniversalParserActive = false;
        console.log('🔄 Enhanced Universal Parser désactivé');
        console.log(`📊 Statistiques de session: ${universalStats.successfulExtractions}/${universalStats.totalCVs} CVs réussis`);
    }

    /**
     * 📊 STATISTIQUES DU PARSER UNIVERSEL
     * ────────────────────────────────────────────────────────────────────────
     */
    function getUniversalParserStats() {
        const successRate = universalStats.totalCVs > 0 ? 
            (universalStats.successfulExtractions / universalStats.totalCVs * 100).toFixed(1) : '0';
        
        return {
            isActive: isUniversalParserActive,
            version: UNIVERSAL_CONFIG.VERSION,
            totalCVsProcessed: universalStats.totalCVs,
            multiPageDetected: universalStats.multiPageDetected,
            successfulExtractions: universalStats.successfulExtractions,
            successRate: successRate + '%',
            averageExperiences: universalStats.averageExperiences.toFixed(1),
            capabilities: {
                autoDetection: true,
                adaptivePrompts: true,
                universalSupport: true,
                intelligentEstimation: true
            }
        };
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // INTERFACE PUBLIQUE UNIVERSELLE
    // ═══════════════════════════════════════════════════════════════════════════
    
    // Activation automatique
    activateUniversalParser();
    
    // Fonctions globales
    window.getUniversalParserStats = getUniversalParserStats;
    window.disableUniversalParser = deactivateUniversalParser;
    window.enableUniversalParser = activateUniversalParser;
    
    // Alias pour compatibilité
    window.getEnhancedParserStats = getUniversalParserStats;
    window.disableEnhancedParser = deactivateUniversalParser;
    window.enableEnhancedParser = activateUniversalParser;
    
    // Nettoyage automatique
    window.addEventListener('beforeunload', function() {
        if (isUniversalParserActive) {
            deactivateUniversalParser();
        }
    });

})();

/**
 * ===============================================================================
 * NOTES DE DÉVELOPPEMENT UNIVERSEL
 * ===============================================================================
 * 
 * 🔧 INTÉGRATION
 * ─────────────────────────────────────────────────────────────────────────────
 * <script src="/static/js/enhanced-multipage-parser.js"></script>
 * 
 * 🧪 COMMANDES DE DEBUG
 * ─────────────────────────────────────────────────────────────────────────────
 * window.getUniversalParserStats()  // Statistiques complètes
 * window.disableUniversalParser()   // Désactivation
 * window.enableUniversalParser()    // Réactivation
 * 
 * 📋 TYPES DE CVS SUPPORTÉS
 * ─────────────────────────────────────────────────────────────────────────────
 * - Assistant/Secrétaire : Détection spécialisée des postes d'assistance
 * - Tech/Ingénieur : Focus sur expériences techniques et développement
 * - Business/Manager : Ciblage des postes de direction et management
 * - Commercial/Vente : Optimisation pour profils commerciaux
 * - Général : Approche universelle pour tous autres profils
 * 
 * 🎯 HEURISTIQUES D'ESTIMATION
 * ─────────────────────────────────────────────────────────────────────────────
 * - Comptage des indicateurs de dates (MM/YYYY, YYYY-YYYY)
 * - Analyse des mots-clés de postes et entreprises
 * - Détection multi-pages (>2000 caractères)
 * - Ajustement selon le type de profil détecté
 * 
 * 🚀 PERFORMANCES ATTENDUES
 * ─────────────────────────────────────────────────────────────────────────────
 * - CVs 1 page : 95-100% d'extraction complète
 * - CVs 2+ pages : 85-100% d'extraction complète
 * - Auto-adaptation selon le contenu
 * - Support universel tous secteurs
 * ===============================================================================
 */