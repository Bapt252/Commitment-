const fs = require('fs');
const pdf = require('pdf-parse');
const path = require('path');

// Chemin vers ton PDF de test
const PDF_PATH = path.join(require('os').homedir(), 'Desktop', 'Bcom HR Opportunité de poste Assistant Juridique.pdf');

console.log('🔍 TEST EXTRACTION TITRE - JobParserAPI');
console.log('=====================================');
console.log(`📁 PDF Test: ${PDF_PATH}`);

// Stratégie 1: Pattern exact pour "Assistant juridique"
function extractTitleByPattern(text) {
    console.log('\n📋 STRATÉGIE 1: Pattern exact');
    console.log('------------------------------');
    
    const patterns = [
        /Assistant(?:\(e\))?\s+juridique/i,
        /Assistant(?:e)?\s+juridique/i,
        /Juriste/i,
        /Conseiller(?:\(ère\))?\s+juridique/i
    ];
    
    for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
            const title = match[0].trim();
            console.log(`✅ Pattern trouvé: "${title}"`);
            console.log(`📏 Longueur: ${title.length} caractères`);
            return title.length <= 25 ? title : title.substring(0, 25);
        }
    }
    
    console.log('❌ Aucun pattern trouvé');
    return 'Poste à pourvoir';
}

// Stratégie 2: Première ligne intelligente
function extractTitleByFirstLine(text) {
    console.log('\n📋 STRATÉGIE 2: Première ligne intelligente');
    console.log('------------------------------------------');
    
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    for (let i = 0; i < Math.min(5, lines.length); i++) {
        const line = lines[i];
        console.log(`Ligne ${i + 1}: "${line.substring(0, 50)}${line.length > 50 ? '...' : ''}"`);
        
        // Ignorer les lignes trop courtes ou avec des mots-clés non pertinents
        if (line.length < 5 || 
            /^(qui sommes|nous|offre|poste|opportunité|recrutement)/i.test(line)) {
            console.log(`  ⏭️ Ignorée (${line.length < 5 ? 'trop courte' : 'mot-clé non pertinent'})`);
            continue;
        }
        
        // Nettoyer la ligne
        let cleanTitle = line
            .replace(/^[^a-zA-ZÀ-ÿ]*/, '') // Supprimer caractères non alphabétiques au début
            .replace(/[^\w\sÀ-ÿ\(\)]+.*$/, '') // Supprimer tout après caractères spéciaux
            .trim();
        
        if (cleanTitle.length >= 5 && cleanTitle.length <= 50) {
            const finalTitle = cleanTitle.length <= 25 ? cleanTitle : cleanTitle.substring(0, 25);
            console.log(`✅ Titre extrait: "${finalTitle}"`);
            console.log(`📏 Longueur: ${finalTitle.length} caractères`);
            return finalTitle;
        }
    }
    
    console.log('❌ Aucune première ligne valide trouvée');
    return 'Poste à pourvoir';
}

// Stratégie 3: Détection par mots-clés professionnels
function extractTitleByKeywords(text) {
    console.log('\n📋 STRATÉGIE 3: Mots-clés professionnels');
    console.log('---------------------------------------');
    
    const jobKeywords = {
        'Assistant juridique': ['assistant juridique', 'assistante juridique', 'assistant(e) juridique'],
        'Juriste': ['juriste', 'juriste d\'entreprise', 'juriste contrats'],
        'Conseiller juridique': ['conseiller juridique', 'conseillère juridique', 'conseiller(ère) juridique'],
        'Responsable juridique': ['responsable juridique', 'responsable affaires juridiques'],
        'Secrétaire juridique': ['secrétaire juridique']
    };
    
    // Normaliser le texte pour la recherche
    const normalizedText = text.toLowerCase().replace(/[àáâãäå]/g, 'a').replace(/[èéêë]/g, 'e');
    
    for (const [jobTitle, keywords] of Object.entries(jobKeywords)) {
        for (const keyword of keywords) {
            if (normalizedText.includes(keyword.toLowerCase())) {
                console.log(`✅ Mot-clé trouvé: "${keyword}" → "${jobTitle}"`);
                console.log(`📏 Longueur: ${jobTitle.length} caractères`);
                return jobTitle;
            }
        }
    }
    
    // Recherche générique de mots professionnels
    const genericPatterns = [
        /\b(assistant|assistante|secrétaire|conseiller|conseillère|responsable|chef|manager|directeur|directrice)\s+\w+/gi
    ];
    
    for (const pattern of genericPatterns) {
        const matches = text.match(pattern);
        if (matches && matches.length > 0) {
            const title = matches[0].trim();
            const finalTitle = title.length <= 25 ? title : title.substring(0, 25);
            console.log(`✅ Pattern générique trouvé: "${finalTitle}"`);
            console.log(`📏 Longueur: ${finalTitle.length} caractères`);
            return finalTitle;
        }
    }
    
    console.log('❌ Aucun mot-clé professionnel trouvé');
    return 'Poste à pourvoir';
}

// Stratégie 4: Multi-patterns avec fallback
function extractTitleMultiPatterns(text) {
    console.log('\n📋 STRATÉGIE 4: Multi-patterns avec fallback');
    console.log('--------------------------------------------');
    
    // Étape 1: Patterns spécifiques haute priorité
    const highPriorityPatterns = [
        { regex: /Assistant(?:\(e\))?\s+juridique/i, name: 'Assistant juridique spécifique' },
        { regex: /Juriste(?:\s+[a-zA-ZÀ-ÿ]+)?/i, name: 'Juriste général' },
        { regex: /Conseiller(?:\(ère\))?\s+juridique/i, name: 'Conseiller juridique' }
    ];
    
    console.log('🎯 Test patterns haute priorité:');
    for (const { regex, name } of highPriorityPatterns) {
        const match = text.match(regex);
        if (match) {
            const title = match[0].trim();
            const finalTitle = title.length <= 25 ? title : title.substring(0, 25);
            console.log(`  ✅ ${name}: "${finalTitle}" (${finalTitle.length} caractères)`);
            return finalTitle;
        }
        console.log(`  ❌ ${name}: Non trouvé`);
    }
    
    // Étape 2: Analyse des premières lignes significatives
    console.log('\n🔍 Analyse premières lignes:');
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    for (let i = 0; i < Math.min(3, lines.length); i++) {
        const line = lines[i];
        
        // Ignorer les lignes avec des mots-clés d'exclusion
        if (/^(qui sommes|nous|offre|entreprise|société|groupe)/i.test(line)) {
            console.log(`  ⏭️ Ligne ${i + 1} ignorée: "${line.substring(0, 30)}..."`);
            continue;
        }
        
        // Extraire le début de la ligne comme titre potentiel
        let candidateTitle = line
            .replace(/[^\w\sÀ-ÿ\(\)\-]/g, ' ') // Garder seulement lettres, espaces, parenthèses, tirets
            .replace(/\s+/g, ' ') // Normaliser les espaces
            .trim();
        
        if (candidateTitle.length >= 5 && candidateTitle.length <= 50) {
            const finalTitle = candidateTitle.length <= 25 ? candidateTitle : candidateTitle.substring(0, 25);
            console.log(`  ✅ Ligne ${i + 1} candidate: "${finalTitle}" (${finalTitle.length} caractères)`);
            return finalTitle;
        }
        
        console.log(`  ❌ Ligne ${i + 1} rejetée: "${line.substring(0, 30)}..." (longueur: ${candidateTitle.length})`);
    }
    
    // Étape 3: Fallback garanti
    console.log('\n⚠️ Fallback activé');
    return 'Poste à pourvoir';
}

// Fonction principale de test
async function testPDFParsing() {
    try {
        // Vérifier si le fichier existe
        if (!fs.existsSync(PDF_PATH)) {
            console.log(`❌ Fichier non trouvé: ${PDF_PATH}`);
            console.log('\n💡 Solutions possibles:');
            console.log('1. Vérifiez le nom exact du fichier sur votre bureau');
            console.log('2. Modifiez le chemin PDF_PATH dans le script');
            console.log('3. Déplacez le PDF sur votre bureau avec le nom exact');
            return;
        }
        
        console.log('✅ Fichier PDF trouvé, lecture en cours...\n');
        
        // Lire et parser le PDF
        const dataBuffer = fs.readFileSync(PDF_PATH);
        const data = await pdf(dataBuffer);
        
        console.log(`📄 PDF lu avec succès:`);
        console.log(`   - Pages: ${data.numpages}`);
        console.log(`   - Caractères: ${data.text.length}`);
        console.log(`   - Première ligne: "${data.text.split('\n')[0].substring(0, 100)}..."`);
        
        console.log('\n' + '='.repeat(50));
        console.log('🧪 TEST DES 4 STRATÉGIES');
        console.log('='.repeat(50));
        
        // Tester les 4 stratégies
        const results = {
            pattern: extractTitleByPattern(data.text),
            firstLine: extractTitleByFirstLine(data.text),
            keywords: extractTitleByKeywords(data.text),
            multiPatterns: extractTitleMultiPatterns(data.text)
        };
        
        console.log('\n' + '='.repeat(50));
        console.log('📊 RÉSULTATS FINAUX');
        console.log('='.repeat(50));
        
        Object.entries(results).forEach(([strategy, result], index) => {
            const strategyNames = {
                pattern: 'Pattern exact',
                firstLine: 'Première ligne',
                keywords: 'Mots-clés',
                multiPatterns: 'Multi-patterns'
            };
            
            console.log(`${index + 1}. ${strategyNames[strategy]}: "${result}" (${result.length} caractères)`);
        });
        
        console.log('\n🎯 RECOMMANDATION:');
        
        // Analyser les résultats pour donner une recommandation
        const uniqueResults = [...new Set(Object.values(results))];
        
        if (uniqueResults.length === 1 && uniqueResults[0] === 'Poste à pourvoir') {
            console.log('⚠️ Aucune stratégie n\'a réussi à extraire un titre spécifique');
            console.log('💡 Il faut revoir l\'algorithme ou le contenu du PDF');
        } else {
            const nonFallbackResults = Object.entries(results).filter(([_, result]) => result !== 'Poste à pourvoir');
            
            if (nonFallbackResults.length > 0) {
                const bestStrategy = nonFallbackResults[0];
                console.log(`✅ Meilleure stratégie: ${bestStrategy[0]} → "${bestStrategy[1]}"`);
                console.log('💡 Cette stratégie devrait être intégrée dans JobParserAPI');
            }
        }
        
    } catch (error) {
        console.error('❌ Erreur lors du test:', error.message);
        
        if (error.message.includes('pdf-parse')) {
            console.log('\n💡 Solution: Installez pdf-parse avec: npm install pdf-parse');
        }
    }
}

// Lancer le test
testPDFParsing();