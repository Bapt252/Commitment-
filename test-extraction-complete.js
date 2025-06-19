const fs = require('fs');
const pdf = require('pdf-parse');
const path = require('path');

// Chemin vers ton PDF de test
const PDF_PATH = path.join(require('os').homedir(), 'Desktop', 'testfp.pdf');

console.log('🔍 TEST EXTRACTION COMPLÈTE - JobParserAPI v2.12');
console.log('================================================');
console.log(`📁 PDF Test: ${PDF_PATH}`);

// 1. TITRE DU POSTE (déjà optimisé)
function extractTitle(text) {
    console.log('\n📋 1. EXTRACTION TITRE');
    console.log('----------------------');
    
    const patterns = [
        /Assistant(?:\(e\))?\s+juridique/i,
        /Juriste(?:\s+[a-zA-ZÀ-ÿ]+)?/i,
        /Responsable\s+[a-zA-ZÀ-ÿ]+/i,
        /Chef\s+de\s+[a-zA-ZÀ-ÿ]+/i
    ];
    
    for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
            let title = match[0].trim().replace(/\([hf\/\s]*\)/gi, '');
            if (title.length <= 25) {
                console.log(`✅ Titre détecté: "${title}"`);
                return title;
            }
        }
    }
    return 'Poste à pourvoir';
}

// 2. TYPE DE CONTRAT
function extractContractType(text) {
    console.log('\n📋 2. EXTRACTION TYPE DE CONTRAT');
    console.log('---------------------------------');
    
    const contractPatterns = [
        { pattern: /\bCDI\b/i, type: 'CDI' },
        { pattern: /\bCDD\b/i, type: 'CDD' },
        { pattern: /\bStage\b/i, type: 'Stage' },
        { pattern: /\bINTERIM\b|\bINTÉRIM\b/i, type: 'Intérim' },
        { pattern: /\bFreelance\b/i, type: 'Freelance' },
        { pattern: /temps\s+partiel/i, type: 'Temps partiel' },
        { pattern: /temps\s+plein/i, type: 'Temps plein' },
        { pattern: /contrat\s+permanent/i, type: 'CDI' },
        { pattern: /contrat\s+temporaire/i, type: 'CDD' }
    ];
    
    console.log('🔍 Recherche patterns de contrat:');
    for (const { pattern, type } of contractPatterns) {
        if (pattern.test(text)) {
            console.log(`✅ Type de contrat trouvé: "${type}"`);
            return type;
        }
        console.log(`❌ "${type}" non trouvé`);
    }
    
    console.log('❌ Aucun type de contrat détecté');
    return '';
}

// 3. LIEU
function extractLocation(text) {
    console.log('\n📋 3. EXTRACTION LIEU');
    console.log('---------------------');
    
    const locationPatterns = [
        { pattern: /(\d{5})\s+([A-Z][a-zA-ZÀ-ÿ\s\-]{3,20})/g, name: 'Code postal + ville' },
        { pattern: /(Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux|Nice|Nantes|Strasbourg|Montpellier|Rennes|Corsica|Corse)/gi, name: 'Villes principales' },
        { pattern: /(Panchéraccía|Porticcio|Ajaccio|Bastia)/gi, name: 'Villes Corse' },
        { pattern: /lieu\s*:\s*([^\n\r,]{3,30})/i, name: 'Lieu explicite' },
        { pattern: /situé[e]?\s+(?:à|en)\s+([A-Z][a-zA-ZÀ-ÿ\s\-]{3,20})/i, name: 'Situé à/en' },
        { pattern: /\b(France|Corse)\b/gi, name: 'Pays/région' }
    ];
    
    console.log('🔍 Recherche patterns de lieu:');
    for (const { pattern, name } of locationPatterns) {
        const match = text.match(pattern);
        if (match) {
            let location = match[1] && match[2] ? `${match[1]} ${match[2]}` : match[1] || match[0];
            location = location.trim();
            if (location.length >= 3 && location.length <= 50) {
                console.log(`✅ ${name}: "${location}"`);
                return location;
            }
        }
        console.log(`❌ ${name}: Non trouvé`);
    }
    
    console.log('❌ Aucun lieu détecté');
    return '';
}

// 4. EXPÉRIENCE REQUISE
function extractExperience(text) {
    console.log('\n📋 4. EXTRACTION EXPÉRIENCE');
    console.log('---------------------------');
    
    const experiencePatterns = [
        { pattern: /(\d+)\s*(?:à\s*(\d+))?\s*an[s]?\s*(?:d['']?expérience)?/i, name: 'X ans d\'expérience' },
        { pattern: /(débutant[e]?)\s*accepté[e]?/i, name: 'Débutant accepté' },
        { pattern: /(première\s+expérience)/i, name: 'Première expérience' },
        { pattern: /(junior|confirmé[e]?|senior)/i, name: 'Niveau expérience' },
        { pattern: /(sans\s+expérience)/i, name: 'Sans expérience' },
        { pattern: /expérience\s+(souhaitée|requise|exigée|nécessaire)/i, name: 'Expérience requise' },
        { pattern: /minimum\s*(\d+)\s*an[s]?/i, name: 'Minimum X ans' },
        { pattern: /(?:au\s+moins|minimum)\s*(\d+)\s*(?:années?|ans?)/i, name: 'Au moins X ans' }
    ];
    
    console.log('🔍 Recherche patterns d\'expérience:');
    for (const { pattern, name } of experiencePatterns) {
        const match = text.match(pattern);
        if (match) {
            let experience = match[1];
            if (match[2]) experience += ` à ${match[2]} ans`;
            console.log(`✅ ${name}: "${experience}"`);
            return experience;
        }
        console.log(`❌ ${name}: Non trouvé`);
    }
    
    console.log('❌ Aucune expérience spécifiée');
    return '';
}

// 5. FORMATION
function extractEducation(text) {
    console.log('\n📋 5. EXTRACTION FORMATION');
    console.log('--------------------------');
    
    const educationPatterns = [
        { pattern: /(Master\s*[12]?(?:\s+[a-zA-ZÀ-ÿ\s]{3,30})?)/i, name: 'Master' },
        { pattern: /(Licence(?:\s+[a-zA-ZÀ-ÿ\s]{3,30})?)/i, name: 'Licence' },
        { pattern: /(BTS\s+[a-zA-ZÀ-ÿ\s]{3,30})/i, name: 'BTS' },
        { pattern: /(DUT\s+[a-zA-ZÀ-ÿ\s]{3,30})/i, name: 'DUT' },
        { pattern: /(Bac\s*\+\s*[2-5])/i, name: 'Bac+X' },
        { pattern: /(Baccalauréat|Bac(?:\s+[a-zA-ZÀ-ÿ\s]{3,20})?)/i, name: 'Baccalauréat' },
        { pattern: /(CAP\s+[a-zA-ZÀ-ÿ\s]{3,30})/i, name: 'CAP' },
        { pattern: /(formation\s+(?:juridique|commerciale|administrative|technique)[^\n.,]{0,40})/i, name: 'Formation spécialisée' },
        { pattern: /(école\s+(?:de\s+)?(?:commerce|ingénieur|droit)[^\n.,]{0,30})/i, name: 'École spécialisée' },
        { pattern: /(niveau\s+(?:bac|licence|master|bts|dut))/i, name: 'Niveau requis' }
    ];
    
    console.log('🔍 Recherche patterns de formation:');
    for (const { pattern, name } of educationPatterns) {
        const match = text.match(pattern);
        if (match) {
            const education = match[1].trim();
            console.log(`✅ ${name}: "${education}"`);
            return education;
        }
        console.log(`❌ ${name}: Non trouvé`);
    }
    
    console.log('❌ Aucune formation spécifiée');
    return '';
}

// 6. RÉMUNÉRATION
function extractSalary(text) {
    console.log('\n📋 6. EXTRACTION RÉMUNÉRATION');
    console.log('-----------------------------');
    
    const salaryPatterns = [
        { pattern: /(\d{1,3}(?:\s?\d{3})*)\s*€\s*(?:brut|net)?\s*(?:\/\s*(?:mois|an|année))?/i, name: 'Montant exact €' },
        { pattern: /(\d+)\s*k\s*€?\s*(?:brut|net)?\s*(?:\/\s*an)?/i, name: 'Montant en K€' },
        { pattern: /(\d+\s*(?:k€?)?)\s*(?:à|-)?\s*(\d+\s*k?€?)\s*(?:brut|net)?/i, name: 'Fourchette salaire' },
        { pattern: /(selon\s+(?:profil|expérience|convention|grille))/i, name: 'Selon profil' },
        { pattern: /(à\s+négocier|négociable)/i, name: 'À négocier' },
        { pattern: /(salaire\s+(?:attractif|motivant|compétitif|intéressant))/i, name: 'Salaire attractif' },
        { pattern: /(SMIC|salaire\s+minimum)/i, name: 'SMIC' },
        { pattern: /rémunération\s*:\s*([^\n\r]{10,50})/i, name: 'Rémunération explicite' },
        { pattern: /package\s+(?:global\s+)?(?:de\s+)?(\d+(?:\s*k)?€?)/i, name: 'Package global' }
    ];
    
    console.log('🔍 Recherche patterns de rémunération:');
    for (const { pattern, name } of salaryPatterns) {
        const match = text.match(pattern);
        if (match) {
            let salary = match[1];
            if (match[2]) salary += ` à ${match[2]}`;
            console.log(`✅ ${name}: "${salary}"`);
            return salary;
        }
        console.log(`❌ ${name}: Non trouvé`);
    }
    
    console.log('❌ Aucune rémunération spécifiée');
    return '';
}

// 7. COMPÉTENCES REQUISES
function extractSkills(text) {
    console.log('\n📋 7. EXTRACTION COMPÉTENCES');
    console.log('----------------------------');
    
    const skillCategories = {
        'Techniques': [
            'Excel', 'Word', 'PowerPoint', 'Outlook', 'Pack Office', 'Office 365',
            'SAP', 'ERP', 'CRM', 'Salesforce', 'Adobe', 'Photoshop', 'InDesign',
            'JavaScript', 'Python', 'Java', 'HTML', 'CSS', 'SQL', 'MongoDB'
        ],
        'Juridiques': [
            'Droit des contrats', 'Droit commercial', 'Droit du travail', 'Droit public',
            'Veille juridique', 'Rédaction actes', 'Contentieux', 'Compliance'
        ],
        'Commerciales': [
            'Prospection', 'Négociation', 'Vente', 'Marketing', 'Relation client',
            'Développement commercial', 'Fidélisation', 'Cross-selling'
        ],
        'Soft Skills': [
            'Organisation', 'Autonomie', 'Communication', 'Relationnel', 'Rigueur',
            'Polyvalence', 'Dynamisme', 'Adaptabilité', 'Esprit d\'équipe', 'Leadership',
            'Gestion du stress', 'Créativité', 'Initiative', 'Ponctualité'
        ],
        'Langues': [
            'Anglais', 'Espagnol', 'Italien', 'Allemand', 'Chinois', 'Arabe',
            'Bilingue', 'Trilingue', 'Niveau B2', 'Niveau C1', 'TOEIC', 'TOEFL'
        ]
    };
    
    const detectedSkills = {};
    
    console.log('🔍 Recherche compétences par catégorie:');
    
    for (const [category, skills] of Object.entries(skillCategories)) {
        console.log(`\n🎯 ${category}:`);
        detectedSkills[category] = [];
        
        for (const skill of skills) {
            const regex = new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
            if (regex.test(text)) {
                detectedSkills[category].push(skill);
                console.log(`  ✅ ${skill}`);
            } else {
                console.log(`  ❌ ${skill}`);
            }
        }
        
        if (detectedSkills[category].length === 0) {
            console.log(`  ⚠️ Aucune compétence ${category.toLowerCase()} détectée`);
        }
    }
    
    // Retourner un résumé
    const allSkills = Object.values(detectedSkills).flat();
    console.log(`\n📊 Total compétences détectées: ${allSkills.length}`);
    return detectedSkills;
}

// 8. RESPONSABILITÉS/MISSIONS
function extractResponsibilities(text) {
    console.log('\n📋 8. EXTRACTION RESPONSABILITÉS');
    console.log('--------------------------------');
    
    const responsibilityKeywords = [
        'gérer', 'assurer', 'participer', 'contribuer', 'développer', 'organiser',
        'coordonner', 'suivre', 'analyser', 'optimiser', 'superviser', 'piloter',
        'mettre en place', 'être en charge', 'responsable de', 'mission principale',
        'vous aurez pour mission', 'vos responsabilités', 'vos missions'
    ];
    
    const responsibilities = [];
    
    // Chercher des phrases avec des verbes d'action
    const sentences = text.split(/[.!?\n]/).filter(s => s.trim().length > 15);
    
    console.log('🔍 Analyse des responsabilités:');
    
    sentences.forEach((sentence, index) => {
        const cleanSentence = sentence.trim();
        const lowerSentence = cleanSentence.toLowerCase();
        
        // Vérifier si la phrase contient des mots-clés de responsabilité
        const hasKeyword = responsibilityKeywords.some(keyword => 
            lowerSentence.includes(keyword.toLowerCase())
        );
        
        if (hasKeyword && cleanSentence.length > 20 && cleanSentence.length < 200) {
            responsibilities.push(cleanSentence);
            console.log(`✅ Mission ${responsibilities.length}: "${cleanSentence.substring(0, 80)}..."`);
        }
    });
    
    console.log(`\n📊 Total responsabilités détectées: ${responsibilities.length}`);
    return responsibilities.slice(0, 8); // Max 8 responsabilités
}

// 9. AVANTAGES
function extractBenefits(text) {
    console.log('\n📋 9. EXTRACTION AVANTAGES');
    console.log('--------------------------');
    
    const benefitPatterns = [
        { pattern: /télétravail|remote|travail\s+à\s+distance/i, benefit: 'Télétravail' },
        { pattern: /tickets?\s+restaurant|tr\b/i, benefit: 'Tickets restaurant' },
        { pattern: /mutuelle|assurance\s+santé/i, benefit: 'Mutuelle santé' },
        { pattern: /formation[s]?|développement\s+professionnel/i, benefit: 'Formation' },
        { pattern: /évolution|carrière|promotion/i, benefit: 'Évolution de carrière' },
        { pattern: /prime[s]?|bonus/i, benefit: 'Primes/Bonus' },
        { pattern: /véhicule\s+de\s+(?:fonction|service)|voiture/i, benefit: 'Véhicule de fonction' },
        { pattern: /parking|place\s+de\s+parking/i, benefit: 'Parking' },
        { pattern: /comité\s+d\'entreprise|ce\b/i, benefit: 'Comité d\'entreprise' },
        { pattern: /rtt|repos\s+compensateur/i, benefit: 'RTT' },
        { pattern: /13[eè]me?\s+mois|treizième\s+mois/i, benefit: '13ème mois' },
        { pattern: /participation|intéressement/i, benefit: 'Participation/Intéressement' },
        { pattern: /restaurant\s+d\'entreprise|cantine/i, benefit: 'Restaurant d\'entreprise' },
        { pattern: /flexibilité?\s+horaire|horaires?\s+flexibles?/i, benefit: 'Horaires flexibles' },
        { pattern: /congés?\s+supplémentaires?/i, benefit: 'Congés supplémentaires' }
    ];
    
    const detectedBenefits = [];
    
    console.log('🔍 Recherche avantages:');
    
    for (const { pattern, benefit } of benefitPatterns) {
        if (pattern.test(text)) {
            detectedBenefits.push(benefit);
            console.log(`✅ ${benefit}`);
        } else {
            console.log(`❌ ${benefit}`);
        }
    }
    
    console.log(`\n📊 Total avantages détectés: ${detectedBenefits.length}`);
    return detectedBenefits;
}

// FONCTION PRINCIPALE DE TEST
async function testCompleteExtraction() {
    try {
        // Vérifier si le fichier existe
        if (!fs.existsSync(PDF_PATH)) {
            console.log(`❌ Fichier non trouvé: ${PDF_PATH}`);
            console.log('\n💡 Assurez-vous que testfp.pdf est sur votre bureau');
            return;
        }
        
        console.log('✅ Fichier PDF trouvé, lecture en cours...\n');
        
        // Lire et parser le PDF
        const dataBuffer = fs.readFileSync(PDF_PATH);
        const data = await pdf(dataBuffer);
        
        console.log(`📄 PDF lu avec succès:`);
        console.log(`   - Pages: ${data.numpages}`);
        console.log(`   - Caractères: ${data.text.length}`);
        
        console.log('\n' + '='.repeat(60));
        console.log('🧪 TEST EXTRACTION COMPLÈTE - 9 ÉLÉMENTS');
        console.log('='.repeat(60));
        
        // Tester toutes les extractions
        const results = {
            title: extractTitle(data.text),
            contractType: extractContractType(data.text),
            location: extractLocation(data.text),
            experience: extractExperience(data.text),
            education: extractEducation(data.text),
            salary: extractSalary(data.text),
            skills: extractSkills(data.text),
            responsibilities: extractResponsibilities(data.text),
            benefits: extractBenefits(data.text)
        };
        
        console.log('\n' + '='.repeat(60));
        console.log('📊 RÉSULTATS FINAUX EXTRACTION COMPLÈTE');
        console.log('='.repeat(60));
        
        console.log(`1. 📋 Titre: "${results.title}"`);
        console.log(`2. 📄 Contrat: "${results.contractType}"`);
        console.log(`3. 📍 Lieu: "${results.location}"`);
        console.log(`4. 💼 Expérience: "${results.experience}"`);
        console.log(`5. 🎓 Formation: "${results.education}"`);
        console.log(`6. 💰 Salaire: "${results.salary}"`);
        console.log(`7. 🎯 Compétences: ${Object.values(results.skills).flat().length} détectées`);
        console.log(`8. 📋 Responsabilités: ${results.responsibilities.length} missions`);
        console.log(`9. 🎁 Avantages: ${results.benefits.length} bénéfices`);
        
        console.log('\n🎯 DÉTAIL COMPÉTENCES:');
        for (const [category, skills] of Object.entries(results.skills)) {
            if (skills.length > 0) {
                console.log(`   ${category}: ${skills.join(', ')}`);
            }
        }
        
        console.log('\n📋 RESPONSABILITÉS:');
        results.responsibilities.forEach((resp, i) => {
            console.log(`   ${i + 1}. ${resp.substring(0, 100)}...`);
        });
        
        console.log('\n🎁 AVANTAGES:');
        console.log(`   ${results.benefits.join(', ')}`);
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ TEST TERMINÉ - Prêt pour intégration v2.12');
        console.log('='.repeat(60));
        
        return results;
        
    } catch (error) {
        console.error('❌ Erreur lors du test:', error.message);
        
        if (error.message.includes('pdf-parse')) {
            console.log('\n💡 Solution: Installez pdf-parse avec: npm install pdf-parse');
        }
    }
}

// Lancer le test
testCompleteExtraction();