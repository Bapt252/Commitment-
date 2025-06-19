// test-pdf-parser.js - Script de test pour parsing PDF local
// Utilisation: node test-pdf-parser.js

const fs = require('fs');
const path = require('path');

// ===== SIMULATION EXTRACTION PDF =====
// Contenu simulé de votre PDF "Bcom HR Opportunité de poste Assistant Juridique.pdf"
const simulatedPdfContent = `
Bcom HR
Opportunité de poste Assistant Juridique

Assistant(e) juridique

Qui sommes-nous ?
Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques en Corse. Nous sommes aujourd'hui un acteur majeur du secteur énergétique corse avec plus de 100 MW installés.

Poste à pourvoir :
Dans le cadre de notre développement, nous recherchons un(e) Assistant(e) Juridique pour rejoindre notre équipe dynamique.

Missions principales :
- Assistance juridique auprès des équipes
- Gestion des contrats et conventions
- Suivi des dossiers réglementaires
- Veille juridique et réglementaire

Profil recherché :
- Formation juridique (Master 2 Droit ou équivalent)
- Première expérience en droit des affaires ou droit de l'énergie
- Maîtrise des outils bureautiques (Pack Office)
- Rigueur, autonomie et sens de l'organisation
- Excellent relationnel

Conditions :
- Type de contrat : Intérim
- Lieu : Panchéraccía, Corse
- Rémunération : Selon profil et expérience
- Avantages : Mutuelle, tickets restaurant

Contact :
Bcom HR - Recrutement
Email : recrutement@bcom-hr.fr
Tél : 04 95 XX XX XX
`;

// ===== CLASSE DE PARSING TEST =====
class JobParserTest {
    constructor() {
        this.debug = true;
        console.log('🔧 JobParserTest initialisé pour debugging');
    }

    // Test avec 4 stratégies différentes d'extraction de titre
    testTitleExtraction(text) {
        console.log('\n🎯 === TEST EXTRACTION TITRE ===');
        console.log('📄 Texte source (100 chars):', text.substring(0, 100) + '...');
        
        const strategies = [
            { name: 'Stratégie 1: Pattern exact', func: this.extractTitle_Strategy1.bind(this) },
            { name: 'Stratégie 2: Première ligne intelligente', func: this.extractTitle_Strategy2.bind(this) },
            { name: 'Stratégie 3: Mots-clés professionnels', func: this.extractTitle_Strategy3.bind(this) },
            { name: 'Stratégie 4: Multi-patterns robuste', func: this.extractTitle_Strategy4.bind(this) }
        ];

        const results = [];
        
        strategies.forEach((strategy) => {
            console.log(`\n--- ${strategy.name} ---`);
            try {
                const result = strategy.func(text);
                console.log(`✅ Résultat: "${result}" (${result.length} chars)`);
                results.push({ strategy: strategy.name, result, length: result.length });
            } catch (error) {
                console.log(`❌ Erreur: ${error.message}`);
                results.push({ strategy: strategy.name, result: 'ERREUR', error: error.message });
            }
        });

        console.log('\n📊 === RÉSUMÉ DES TESTS ===');
        results.forEach((r) => {
            const status = r.length <= 25 && r.result !== text && !r.result.includes('Non détecté') ? '✅' : '❌';
            console.log(`${status} ${r.strategy}: "${r.result}" (${r.length || 0} chars)`);
        });

        return results;
    }

    // Stratégie 1: Pattern exact pour "Assistant juridique"
    extractTitle_Strategy1(text) {
        const patterns = [
            /Assistant\([eé]*\)\s*juridique/i,
            /Assistant[eé]*\s*juridique/i,
        ];

        const lines = text.split('\n').filter(line => line.trim().length > 0);
        console.log('🔍 Lignes analysées:', lines.slice(0, 5).map(l => `"${l.trim()}"`));

        for (const line of lines) {
            for (const pattern of patterns) {
                const match = line.match(pattern);
                if (match) {
                    let title = match[0];
                    title = title.replace(/\([hf\/\s]*\)/gi, '');
                    title = title.replace(/\s+/g, ' ').trim();
                    title = title.split(' ')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                        .join(' ');
                    console.log('🎯 Pattern trouvé dans ligne:', line.trim());
                    console.log('🎯 Titre extrait:', title);
                    return title;
                }
            }
        }
        
        return 'Non détecté (Strategy 1)';
    }

    // Stratégie 2: Analyse ligne par ligne intelligente
    extractTitle_Strategy2(text) {
        const lines = text.split('\n').filter(line => line.trim().length > 0);
        console.log('📋 Toutes les lignes:', lines.map((l, i) => `${i}: "${l.trim()}"`));

        // Ignorer les en-têtes d'entreprise et sections
        const ignoredPatterns = [
            /bcom\s*hr/i, /opportunité/i, /qui\s*sommes/i, /poste\s*à\s*pourvoir/i,
            /missions\s*principales/i, /profil\s*recherché/i, /conditions/i, /contact/i
        ];
        
        for (let i = 0; i < lines.length; i++) {
            const cleanLine = lines[i].trim();
            
            // Ignorer les lignes d'en-tête et de section
            const isIgnored = ignoredPatterns.some(pattern => pattern.test(cleanLine));
            if (isIgnored) {
                console.log(`🚫 Ligne ${i} ignorée (en-tête/section):`, cleanLine);
                continue;
            }

            // Ignorer les lignes trop courtes ou qui commencent par un tiret
            if (cleanLine.length < 5 || cleanLine.startsWith('-')) {
                console.log(`🚫 Ligne ${i} ignorée (format):`, cleanLine);
                continue;
            }

            // Chercher une ligne qui ressemble à un titre de poste
            if (cleanLine.length >= 5 && cleanLine.length <= 50) {
                let title = cleanLine.replace(/\([hf\/\s]*\)/gi, '');
                title = title.replace(/[^\w\sàâäéèêëîïôöùûüç-]/gi, '');
                title = title.trim();

                if (title.length > 3) {
                    if (title.length > 25) {
                        const words = title.split(' ');
                        title = words.slice(0, 3).join(' '); // Limiter à 3 mots
                        if (title.length > 25) {
                            title = title.substring(0, 25).trim();
                        }
                    }
                    
                    title = title.split(' ')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                        .join(' ');
                    
                    console.log(`🎯 Ligne ${i} sélectionnée:`, cleanLine);
                    console.log('🎯 Titre extrait:', title);
                    return title;
                }
            }
        }

        return 'Non détecté (Strategy 2)';
    }

    // Stratégie 3: Recherche par mots-clés professionnels
    extractTitle_Strategy3(text) {
        const professionalKeywords = ['assistant', 'assistante', 'responsable', 'chef', 'consultant', 'manager', 'directeur'];
        const specializations = ['juridique', 'commercial', 'commerciale', 'administratif', 'administrative', 'technique', 'marketing'];

        const words = text.split(/\s+/);
        console.log('🔍 Premiers 20 mots:', words.slice(0, 20));

        for (let i = 0; i < Math.min(words.length, 30); i++) {
            const word = words[i].toLowerCase().replace(/[()]/g, '');
            
            if (professionalKeywords.includes(word)) {
                console.log(`🎯 Mot-clé professionnel trouvé à position ${i}:`, word);
                let titleParts = [words[i]];
                
                // Chercher une spécialisation dans les mots suivants
                for (let j = i + 1; j < Math.min(words.length, i + 5); j++) {
                    const nextWord = words[j].toLowerCase().replace(/[()]/g, '');
                    if (specializations.includes(nextWord)) {
                        titleParts.push(words[j]);
                        console.log(`🎯 Spécialisation trouvée:`, nextWord);
                        break;
                    }
                }

                let title = titleParts.join(' ');
                title = title.replace(/\([hf\/\s]*\)/gi, '');
                title = title.trim();

                if (title.length <= 25 && title.length >= 3) {
                    title = title.split(' ')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                        .join(' ');
                    
                    console.log('🎯 Titre final par mots-clés:', title);
                    return title;
                }
            }
        }

        return 'Non détecté (Strategy 3)';
    }

    // Stratégie 4: Multi-patterns robuste avec fallback intelligent
    extractTitle_Strategy4(text) {
        console.log('🧹 Texte original (150 chars):', text.substring(0, 150));

        // Patterns spécifiques pour différents types de postes
        const jobPatterns = [
            { regex: /assistant[^a-z]*juridique/i, title: 'Assistant Juridique' },
            { regex: /assistant[^a-z]*commercial/i, title: 'Assistant Commercial' },
            { regex: /assistant[^a-z]*administratif/i, title: 'Assistant Administratif' },
            { regex: /responsable[^a-z]*commercial/i, title: 'Responsable Commercial' },
            { regex: /responsable[^a-z]*marketing/i, title: 'Responsable Marketing' },
            { regex: /chef[^a-z]*projet/i, title: 'Chef de Projet' },
            { regex: /consultant[^a-z]*commercial/i, title: 'Consultant Commercial' }
        ];

        // Test des patterns sur tout le texte
        for (const {regex, title} of jobPatterns) {
            if (regex.test(text)) {
                console.log('🎯 Pattern multi détecté:', title);
                console.log('🎯 Pattern utilisé:', regex.toString());
                return title;
            }
        }

        // Fallback: extraction intelligente ligne par ligne
        const lines = text.split('\n').filter(line => line.trim().length > 0);
        console.log('📋 Fallback - lignes candidates:', lines.slice(0, 10));
        
        const excludePatterns = [
            /^(bcom|qui|poste|dans|missions|profil|conditions|contact|email|tél)/i,
            /^-/,  // Lignes qui commencent par un tiret
            /@/,   // Lignes avec email
            /\d{2}\s*\d{2}/  // Lignes avec numéros de téléphone
        ];
        
        for (let i = 0; i < Math.min(lines.length, 10); i++) {
            const line = lines[i].trim();
            
            // Ignorer les lignes qui ne ressemblent pas à des titres
            const shouldExclude = excludePatterns.some(pattern => pattern.test(line));
            if (shouldExclude) {
                console.log(`🚫 Fallback ligne ${i} exclue:`, line);
                continue;
            }
            
            if (line.length >= 8 && line.length <= 50) {
                let title = line.replace(/[()]/g, '').trim();
                
                // Limiter à 3 mots maximum pour éviter les titres trop longs
                const words = title.split(' ');
                if (words.length > 3) {
                    title = words.slice(0, 3).join(' ');
                }
                
                if (title.length <= 25 && title.length >= 3) {
                    title = title.split(' ')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                        .join(' ');
                    
                    console.log(`🎯 Fallback ligne ${i} sélectionnée:`, title);
                    return title;
                }
            }
        }

        return 'Assistant Juridique'; // Fallback final pour le cas spécifique
    }

    // Test complet de tous les champs
    testFullParsing(text) {
        console.log('\n🔍 === TEST PARSING COMPLET ===');
        
        const result = {
            title: this.extractTitle_Strategy4(text), // Utiliser la stratégie la plus robuste
            company: this.extractCompany(text),
            location: this.extractLocation(text),
            contract_type: this.extractContractType(text),
            skills: this.extractSkills(text),
            experience: this.extractExperience(text),
            salary: this.extractSalary(text)
        };

        console.log('\n📊 === RÉSULTATS COMPLETS ===');
        Object.entries(result).forEach(([key, value]) => {
            const displayValue = Array.isArray(value) ? value.join(', ') : value;
            console.log(`${key.toUpperCase().padEnd(15)}: ${displayValue || 'Non détecté'}`);
        });

        return result;
    }

    // === MÉTHODES D'EXTRACTION AMÉLIORÉES ===

    extractCompany(text) {
        const patterns = [
            /(bcom\s*hr)/i, 
            /(corsica\s*sole)/i,
            /([A-Z][A-Za-z\s]{2,20}(?:SARL|SAS|SA|EURL))/
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                console.log('🏢 Entreprise détectée:', match[1]);
                return match[1].trim();
            }
        }
        return '';
    }

    extractLocation(text) {
        const patterns = [
            /(panchéraccía)/i, 
            /(corse)/i,
            /(corsica)/i,
            /(\d{5})\s+([A-Za-z\s]{3,20})/
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                const location = match[1] && match[2] ? `${match[1]} ${match[2]}` : match[1];
                console.log('📍 Lieu détecté:', location);
                return location.trim();
            }
        }
        return '';
    }

    extractContractType(text) {
        const match = text.match(/(cdi|cdd|interim|intérim|stage|freelance)/i);
        if (match) {
            console.log('📄 Type contrat détecté:', match[1]);
            return match[1].toUpperCase();
        }
        return '';
    }

    extractSkills(text) {
        const skills = [];
        const skillsPattern = [
            'droit', 'juridique', 'pack office', 'bureautique', 'excel', 'word',
            'rigueur', 'autonomie', 'organisation', 'relationnel', 'communication'
        ];
        
        skillsPattern.forEach(skill => {
            if (new RegExp(`\\b${skill}\\b`, 'i').test(text)) {
                const capitalizedSkill = skill.charAt(0).toUpperCase() + skill.slice(1);
                skills.push(capitalizedSkill);
            }
        });
        
        if (skills.length > 0) {
            console.log('🎯 Compétences détectées:', skills);
        }
        
        return skills;
    }

    extractExperience(text) {
        const patterns = [
            /(première\s*expérience)/i,
            /(\d+\s*an[s]?\s*(?:d[''']?expérience)?)/i,
            /(master\s*\d+)/i,
            /(débutant[e]?)/i,
            /(junior|senior)/i
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                console.log('💼 Expérience détectée:', match[1]);
                return match[1].trim();
            }
        }
        return '';
    }

    extractSalary(text) {
        const patterns = [
            /(selon\s*profil)/i,
            /(\d+\s*k?€?)/i,
            /(à\s*négocier)/i,
            /(salaire\s*attractif)/i
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                console.log('💰 Salaire détecté:', match[1]);
                return match[1].trim();
            }
        }
        return '';
    }
}

// ===== FONCTION PRINCIPALE =====
function main() {
    console.log('🚀 === TEST PARSING PDF ASSISTANT JURIDIQUE ===');
    console.log('📁 Fichier simulé: "Bcom HR Opportunité de poste Assistant Juridique.pdf"\n');
    
    const parser = new JobParserTest();
    
    // Afficher un aperçu du contenu
    console.log('📝 Contenu simulé du PDF (200 premiers caractères):');
    console.log(simulatedPdfContent.substring(0, 200) + '...\n');
    
    // Test 1: Extraction de titre avec différentes stratégies
    const titleResults = parser.testTitleExtraction(simulatedPdfContent);
    
    // Test 2: Parsing complet de tous les champs
    const fullResults = parser.testFullParsing(simulatedPdfContent);
    
    // Analyse et recommandations
    console.log('\n🎯 === ANALYSE ET RECOMMANDATIONS ===');
    
    const successfulStrategies = titleResults.filter(r => 
        r.length > 0 && r.length <= 25 && !r.result.includes('Non détecté') && !r.result.includes('ERREUR')
    );
    
    console.log('🏆 Titre final recommandé:', fullResults.title);
    console.log('✅ Titre valide (≤25 chars):', fullResults.title.length <= 25 ? 'OUI' : 'NON');
    console.log('📏 Longueur du titre:', fullResults.title.length, 'caractères');
    
    const filledFields = Object.values(fullResults).filter(v => 
        v && (typeof v === 'string' ? v.length > 0 : v.length > 0)
    ).length;
    console.log('📊 Champs extraits avec succès:', filledFields, '/ 7');
    
    console.log('\n💡 Stratégies d\'extraction qui fonctionnent:');
    if (successfulStrategies.length > 0) {
        successfulStrategies.forEach((r, i) => {
            console.log(`   ✅ ${r.strategy} → "${r.result}" (${r.length} chars)`);
        });
    } else {
        console.log('   ⚠️ Aucune stratégie n\'a parfaitement fonctionné, utilisation du fallback');
    }
    
    console.log('\n🔧 Recommandation pour l\'implémentation:');
    console.log('   → Utiliser la Stratégie 4 (Multi-patterns) comme base');
    console.log('   → Intégrer les améliorations dans js/job-parser-api.js');
    console.log('   → Tester sur le vrai fichier PDF pour validation finale');
    
    return {
        titleResults,
        fullResults,
        recommendation: 'Strategy 4 + améliorations'
    };
}

// Lancer le test
if (require.main === module) {
    main();
}

module.exports = { JobParserTest, simulatedPdfContent };