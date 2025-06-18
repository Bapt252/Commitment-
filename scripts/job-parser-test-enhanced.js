// Script de test autonome pour déboguer le Job Parser v2.3
// Usage: Charger cette page dans le navigateur et exécuter les tests

document.addEventListener('DOMContentLoaded', function() {
    console.log('🧪 Script de test Job Parser Enhanced chargé');
    
    // Créer l'interface de test
    createTestInterface();
});

function createTestInterface() {
    // Créer un conteneur pour les tests
    const testContainer = document.createElement('div');
    testContainer.id = 'job-parser-test-container';
    testContainer.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        width: 400px;
        background: white;
        border: 2px solid #7c4dff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-family: Arial, sans-serif;
        font-size: 14px;
        max-height: 80vh;
        overflow-y: auto;
    `;
    
    testContainer.innerHTML = `
        <h3 style="margin-top: 0; color: #7c4dff;">🧪 Job Parser Test v2.3</h3>
        
        <div style="margin-bottom: 10px;">
            <button onclick="testWithSampleFiche()" style="padding: 8px 12px; margin: 5px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Test Fiche Standard
            </button>
            <button onclick="testWithHtmlFiche()" style="padding: 8px 12px; margin: 5px; background: #FF9800; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Test HTML
            </button>
            <button onclick="testFileUpload()" style="padding: 8px 12px; margin: 5px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Test PDF Upload
            </button>
        </div>
        
        <div style="margin-bottom: 10px;">
            <textarea id="test-text-input" placeholder="Collez votre texte de fiche de poste ici..." style="width: 100%; height: 100px; margin-bottom: 10px; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
            <button onclick="testCustomText()" style="padding: 8px 12px; background: #9C27B0; color: white; border: none; border-radius: 4px; cursor: pointer; width: 100%;">
                Analyser ce texte
            </button>
        </div>
        
        <input type="file" id="pdf-file-input" accept=".pdf,.txt,.doc,.docx" style="margin-bottom: 10px;" onchange="handleFileUpload(this)">
        
        <div id="test-results" style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">
            <em>Les résultats apparaîtront ici...</em>
        </div>
        
        <div style="margin-top: 10px; text-align: right;">
            <button onclick="toggleTestContainer()" style="padding: 4px 8px; background: #666; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                Masquer
            </button>
        </div>
    `;
    
    document.body.appendChild(testContainer);
    
    // Créer l'input file caché pour les tests
    const hiddenFileInput = document.createElement('input');
    hiddenFileInput.type = 'file';
    hiddenFileInput.accept = '.pdf,.txt,.doc,.docx';
    hiddenFileInput.style.display = 'none';
    hiddenFileInput.addEventListener('change', handleHiddenFileUpload);
    document.body.appendChild(hiddenFileInput);
    window.hiddenFileInput = hiddenFileInput;
}

// Fonction pour tester avec une fiche standard française
function testWithSampleFiche() {
    const sampleText = `
Fiche de poste : Gestionnaire Paie et ADP

Société : TechCorp Solutions
Lieu de travail : 75014 Paris

Expérience : Minimum 2 ans d'expérience en gestion de paie
Formation : Bac+2/3 en comptabilité ou ressources humaines

Missions principales :
- Gestion de la paie mensuelle pour 150 salariés
- Utilisation du logiciel ADP pour la saisie et les éditions
- Suivi des déclarations sociales (DSN, URSSAF)
- Gestion des congés payés et absences
- Interface avec les organismes sociaux

Compétences requises :
- Maîtrise d'Excel et ADP
- Rigueur et organisation
- Sens du contact et confidentialité
- Autonomie dans le travail

Avantages :
- Télétravail 2 jours par semaine
- Mutuelle entreprise
- Tickets restaurant
- 13e mois
- Formation continue

Type de contrat : CDI - 35h
Rémunération : 35-40K€ selon expérience
    `;
    
    console.log('🧪 Test avec fiche standard française');
    analyzeText(sampleText, 'Fiche Standard');
}

// Fonction pour tester avec du HTML
function testWithHtmlFiche() {
    const htmlText = `
<h1>Responsable Commercial B2B</h1>
<p><strong>Lieu :</strong> <span>69000 Lyon</span></p>
<p><em>Expérience :</em> Minimum 3 ans en commercial B2B</p>

<h2>Missions :</h2>
<ul>
<li>Gestion d'un portefeuille clients</li>
<li>Développement commercial sur la région</li>
<li>Négociation des contrats</li>
</ul>

<h2>Profil :</h2>
<p>Formation Bac+3/5 en commerce<br/>
Maîtrise de Salesforce et Excel<br/>
Véhicule de fonction fourni</p>

<div>Salaire : 45K€ + variable</div>
    `;
    
    console.log('🧪 Test avec HTML à nettoyer');
    analyzeText(htmlText, 'HTML à nettoyer');
}

// Fonction pour analyser du texte personnalisé
function testCustomText() {
    const textarea = document.getElementById('test-text-input');
    if (!textarea.value.trim()) {
        alert('Veuillez entrer du texte à analyser');
        return;
    }
    
    console.log('🧪 Test avec texte personnalisé');
    analyzeText(textarea.value, 'Texte personnalisé');
}

// Fonction principale d'analyse
function analyzeText(text, testName) {
    console.log(`\n🔍 === ANALYSE : ${testName} ===`);
    console.log('📝 Texte original (200 premiers chars):', text.substring(0, 200));
    
    // Vérifier si JobParserAPI est disponible
    if (!window.JobParserAPI) {
        displayError('JobParserAPI non disponible. Assurez-vous que job-parser-api.js est chargé.');
        return;
    }
    
    try {
        // Créer une instance avec debug activé
        const parser = new window.JobParserAPI({ debug: true });
        
        // Analyser le texte
        const result = parser.analyzeJobLocally(text);
        
        // Afficher les résultats
        displayResults(result, testName);
        
        // Tests spécifiques
        runSpecificTests(text, result, testName);
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'analyse:', error);
        displayError(`Erreur: ${error.message}`);
    }
}

// Fonction pour afficher les résultats dans l'interface
function displayResults(result, testName) {
    const resultsDiv = document.getElementById('test-results');
    
    const html = `
        <h4 style="color: #7c4dff; margin-top: 0;">📊 Résultats - ${testName}</h4>
        <div style="display: grid; gap: 8px;">
            <div><strong>Titre:</strong> <span style="color: ${result.title === 'Titre non détecté' ? 'red' : 'green'}">${result.title}</span></div>
            <div><strong>Lieu:</strong> <span style="color: ${result.location ? 'green' : 'orange'}">${result.location || 'Non détecté'}</span></div>
            <div><strong>Expérience:</strong> <span style="color: ${result.experience ? 'green' : 'orange'}">${result.experience || 'Non détecté'}</span></div>
            <div><strong>Formation:</strong> <span style="color: ${result.education ? 'green' : 'orange'}">${result.education || 'Non détecté'}</span></div>
            <div><strong>Salaire:</strong> <span style="color: ${result.salary ? 'green' : 'orange'}">${result.salary || 'Non détecté'}</span></div>
            <div><strong>Compétences:</strong> <span style="color: ${result.skills.length > 0 ? 'green' : 'orange'}">${result.skills.length} trouvée(s)</span></div>
            <div><strong>Responsabilités:</strong> <span style="color: ${result.responsibilities.length > 0 ? 'green' : 'orange'}">${result.responsibilities.length} trouvée(s)</span></div>
            <div><strong>Avantages:</strong> <span style="color: ${result.benefits.length > 0 ? 'green' : 'orange'}">${result.benefits.length} trouvé(s)</span></div>
        </div>
        
        ${result.skills.length > 0 ? `
        <div style="margin-top: 10px;">
            <strong>Compétences détectées:</strong><br>
            <small style="background: #e3f2fd; padding: 4px; border-radius: 4px; display: inline-block; margin-top: 4px;">
                ${result.skills.join(', ')}
            </small>
        </div>
        ` : ''}
        
        <div style="margin-top: 10px; font-size: 12px; color: #666;">
            ⏱️ Test effectué à ${new Date().toLocaleTimeString()}
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    
    // Scroll vers les résultats
    resultsDiv.scrollTop = resultsDiv.scrollHeight;
}

// Fonction pour afficher les erreurs
function displayError(message) {
    const resultsDiv = document.getElementById('test-results');
    resultsDiv.innerHTML = `
        <div style="color: red; font-weight: bold;">❌ ${message}</div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">
            ⏱️ ${new Date().toLocaleTimeString()}
        </div>
    `;
}

// Fonction pour des tests spécifiques
function runSpecificTests(text, result, testName) {
    console.log(`\n🎯 Tests spécifiques pour ${testName}:`);
    
    // Test nettoyage HTML
    if (text.includes('<') && text.includes('>')) {
        console.log('📄 HTML détecté - Test de nettoyage...');
        const parser = new window.JobParserAPI({ debug: false });
        const cleaned = parser.cleanHtmlText(text);
        console.log('✅ Texte nettoyé (200 chars):', cleaned.substring(0, 200));
    }
    
    // Test détection titre
    if (result.title === 'Titre non détecté') {
        console.log('❌ Titre non détecté - Patterns à améliorer');
        debugTitleExtraction(text);
    } else {
        console.log('✅ Titre détecté:', result.title);
    }
    
    // Test détection lieu
    if (!result.location) {
        console.log('❌ Lieu non détecté - Vérification des patterns');
        debugLocationExtraction(text);
    } else {
        console.log('✅ Lieu détecté:', result.location);
    }
}

// Debug spécifique pour le titre
function debugTitleExtraction(text) {
    console.log('🔍 Debug extraction titre:');
    
    const patterns = [
        { name: 'Fiche de poste', regex: /fiche\s+de\s+poste\s*[:\-]?\s*(.+?)(?:\n|$)/i },
        { name: 'Poste :', regex: /poste\s*[:\-]\s*([^\n.]+)/i },
        { name: 'Titre :', regex: /titre\s*[:\-]\s*([^\n.]+)/i },
        { name: 'Gestionnaire', regex: /(gestionnaire\s+[^\n]+)/i },
        { name: 'Responsable', regex: /(responsable\s+[^\n]+)/i }
    ];
    
    patterns.forEach(pattern => {
        const match = text.match(pattern.regex);
        if (match) {
            console.log(`  ✅ ${pattern.name}:`, match[1] || match[0]);
        } else {
            console.log(`  ❌ ${pattern.name}: non trouvé`);
        }
    });
}

// Debug spécifique pour le lieu
function debugLocationExtraction(text) {
    console.log('🔍 Debug extraction lieu:');
    
    const patterns = [
        { name: 'Lieu de travail', regex: /lieu\s+de\s+travail\s*[:\-]?\s*([^\n.]+)/i },
        { name: 'Code postal', regex: /(\d{5})\s+([A-Z][a-z]+)/i },
        { name: 'Paris', regex: /(paris\s*\d*)/i },
        { name: 'Lyon', regex: /(lyon\s*\d*)/i }
    ];
    
    patterns.forEach(pattern => {
        const match = text.match(pattern.regex);
        if (match) {
            console.log(`  ✅ ${pattern.name}:`, match[1] || match[0]);
        } else {
            console.log(`  ❌ ${pattern.name}: non trouvé`);
        }
    });
}

// Gestion upload de fichier visible
function handleFileUpload(input) {
    if (input.files.length > 0) {
        const file = input.files[0];
        console.log('📁 Fichier sélectionné:', file.name);
        
        if (file.type === 'application/pdf') {
            analyzePDFFile(file);
        } else {
            analyzeTextFile(file);
        }
    }
}

// Gestion upload de fichier caché
function handleHiddenFileUpload(event) {
    handleFileUpload(event.target);
}

// Fonction pour déclencher le sélecteur de fichier
function testFileUpload() {
    window.hiddenFileInput.click();
}

// Analyse d'un fichier PDF
function analyzePDFFile(file) {
    console.log('📄 Analyse du fichier PDF:', file.name);
    
    if (!window.pdfjsLib) {
        displayError('PDF.js non disponible. Impossible d\'analyser les fichiers PDF.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const typedarray = new Uint8Array(e.target.result);
            const pdf = await pdfjsLib.getDocument({data: typedarray}).promise;
            
            let fullText = '';
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const textContent = await page.getTextContent();
                const pageText = textContent.items.map(item => item.str).join(' ');
                fullText += pageText + '\n';
            }
            
            console.log('📝 Texte extrait du PDF (500 premiers chars):', fullText.substring(0, 500));
            analyzeText(fullText, `PDF: ${file.name}`);
            
        } catch (error) {
            console.error('❌ Erreur lecture PDF:', error);
            displayError(`Erreur lecture PDF: ${error.message}`);
        }
    };
    
    reader.readAsArrayBuffer(file);
}

// Analyse d'un fichier texte
function analyzeTextFile(file) {
    console.log('📄 Analyse du fichier texte:', file.name);
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        analyzeText(text, `Fichier: ${file.name}`);
    };
    
    reader.readAsText(file);
}

// Fonction pour masquer/afficher le conteneur de test
function toggleTestContainer() {
    const container = document.getElementById('job-parser-test-container');
    if (container.style.display === 'none') {
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

// Exposer les fonctions pour usage en console
window.jobParserDebug = {
    testSample: testWithSampleFiche,
    testHtml: testWithHtmlFiche,
    testText: testCustomText,
    analyzeText: analyzeText,
    show: () => {
        const container = document.getElementById('job-parser-test-container');
        if (container) container.style.display = 'block';
        else createTestInterface();
    }
};

console.log('🚀 Script de test chargé !');
console.log('📖 Fonctions disponibles:');
console.log('  - jobParserDebug.testSample() : Test avec fiche standard');
console.log('  - jobParserDebug.testHtml() : Test avec HTML');
console.log('  - jobParserDebug.analyzeText("texte") : Analyser du texte');
console.log('  - jobParserDebug.show() : Afficher l\'interface de test');
