/**
 * Job Parser Integration Fix
 * Script d'intégration robuste pour faire fonctionner le job parsing 
 * dans le questionnaire client Commitment
 */

// Variables globales pour l'état du parsing
let jobParserInstance = null;
let parsingInProgress = false;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initialisation du Job Parser Integration Fix...');
    
    // Attendre que tous les scripts soient chargés
    setTimeout(initializeJobParsing, 500);
});

/**
 * Initialise le système de job parsing
 */
function initializeJobParsing() {
    console.log('🚀 Démarrage de l\'initialisation du job parsing...');
    
    // 1. Créer l'instance JobParserAPI
    createJobParserInstance();
    
    // 2. Configurer l'affichage conditionnel
    setupConditionalDisplay();
    
    // 3. Configurer les événements de fichiers
    setupFileHandling();
    
    // 4. Configurer les boutons d'analyse
    setupAnalysisButtons();
    
    // 5. Test de fonctionnement
    testJobParserSetup();
    
    console.log('✅ Job parsing complètement initialisé !');
}

/**
 * Crée l'instance JobParserAPI
 */
function createJobParserInstance() {
    try {
        if (window.JobParserAPI) {
            jobParserInstance = new window.JobParserAPI({
                debug: true,
                enablePDFCleaning: true
            });
            
            // Créer aussi l'instance globale pour compatibilité
            window.jobParserAPI = jobParserInstance;
            
            console.log('✅ JobParserAPI instance créée avec succès');
        } else {
            console.error('❌ JobParserAPI class non trouvée. Vérifiez que job-parser-api.js est chargé.');
        }
    } catch (error) {
        console.error('❌ Erreur lors de la création de l\'instance JobParserAPI:', error);
    }
}

/**
 * Configure l'affichage conditionnel de la section parsing
 */
function setupConditionalDisplay() {
    const recruitmentYes = document.getElementById('recruitment-yes');
    const recruitmentNo = document.getElementById('recruitment-no');
    const jobParsingSection = document.getElementById('job-parsing-section');
    
    if (recruitmentYes && recruitmentNo && jobParsingSection) {
        // Événement pour "Oui"
        recruitmentYes.addEventListener('change', function() {
            if (this.checked) {
                jobParsingSection.classList.add('active');
                sessionStorage.setItem('recruitmentNeeded', 'yes');
                showNotification('Section de parsing de fiche de poste activée !', 'info');
                console.log('✅ Section job parsing activée');
            }
        });
        
        // Événement pour "Non" 
        recruitmentNo.addEventListener('change', function() {
            if (this.checked) {
                jobParsingSection.classList.remove('active');
                sessionStorage.setItem('recruitmentNeeded', 'no');
                console.log('Section job parsing désactivée');
            }
        });
        
        // Restaurer l'état sauvegardé
        const savedChoice = sessionStorage.getItem('recruitmentNeeded');
        if (savedChoice === 'yes') {
            recruitmentYes.checked = true;
            jobParsingSection.classList.add('active');
        }
    }
}

/**
 * Configure la gestion des fichiers (drag & drop + sélection)
 */
function setupFileHandling() {
    const dropZone = document.getElementById('job-drop-zone');
    const fileInput = document.getElementById('job-file-input');
    const fileBadge = document.getElementById('file-badge');
    const fileName = document.getElementById('file-name');
    const removeFile = document.getElementById('remove-file');
    
    if (!dropZone || !fileInput) return;
    
    // Prévenir les comportements par défaut
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    // Effets visuels drag & drop
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-active');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-active');
        });
    });
    
    // Gestion du drop de fichier
    dropZone.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    // Clic sur la zone pour ouvrir le sélecteur
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Sélection de fichier classique
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFileSelection(this.files[0]);
        }
    });
    
    // Supprimer le fichier sélectionné
    if (removeFile) {
        removeFile.addEventListener('click', function(e) {
            e.stopPropagation();
            fileInput.value = '';
            if (fileBadge) fileBadge.style.display = 'none';
        });
    }
    
    /**
     * Gère la sélection d'un fichier
     */
    function handleFileSelection(file) {
        console.log('📁 Fichier sélectionné:', file.name, file.type);
        
        // Vérifier le type de fichier
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'text/plain'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            showNotification('Type de fichier non supporté. Utilisez PDF, DOCX ou TXT.', 'error');
            return;
        }
        
        // Afficher le badge du fichier
        if (fileBadge && fileName) {
            fileName.textContent = file.name;
            fileBadge.style.display = 'flex';
        }
        
        // Proposer l'analyse automatique
        if (confirm(`Voulez-vous analyser le fichier "${file.name}" maintenant ?`)) {
            analyzeJobFile(file);
        }
    }
}

/**
 * Configure les boutons d'analyse
 */
function setupAnalysisButtons() {
    const analyzeTextBtn = document.getElementById('analyze-job-text');
    const jobTextarea = document.getElementById('job-description-text');
    
    if (analyzeTextBtn && jobTextarea) {
        analyzeTextBtn.addEventListener('click', function() {
            const text = jobTextarea.value.trim();
            
            if (!text) {
                showNotification('Veuillez entrer le texte de la fiche de poste à analyser.', 'warning');
                return;
            }
            
            analyzeJobText(text);
        });
        
        console.log('✅ Bouton d\'analyse de texte configuré');
    }
}

/**
 * Analyse un texte de fiche de poste
 */
async function analyzeJobText(text) {
    if (parsingInProgress) {
        showNotification('Une analyse est déjà en cours...', 'info');
        return;
    }
    
    console.log('🔍 Démarrage de l\'analyse de texte...');
    parsingInProgress = true;
    
    // Afficher le loader
    showLoader(true);
    
    try {
        let result;
        
        if (jobParserInstance) {
            // Utiliser l'API locale avancée
            result = jobParserInstance.analyzeJobLocally(text);
            console.log('✅ Analyse locale réussie:', result);
        } else {
            // Fallback simple si l'API n'est pas disponible
            result = createFallbackAnalysis(text);
            console.log('⚠️ Utilisation du fallback simple');
        }
        
        // Sauvegarder et afficher les résultats
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        displayJobResults(result);
        
        showNotification('✅ Analyse réussie ! Informations extraites automatiquement.', 'success');
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'analyse:', error);
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
    } finally {
        parsingInProgress = false;
        showLoader(false);
    }
}

/**
 * Analyse un fichier de fiche de poste
 */
async function analyzeJobFile(file) {
    if (parsingInProgress) {
        showNotification('Une analyse est déjà en cours...', 'info');
        return;
    }
    
    console.log('📄 Démarrage de l\'analyse de fichier:', file.name);
    parsingInProgress = true;
    
    // Afficher le loader
    showLoader(true);
    
    try {
        let text = '';
        
        // Lire le contenu du fichier
        if (file.type === 'text/plain') {
            text = await readTextFile(file);
        } else if (file.type === 'application/pdf') {
            text = await readPDFFile(file);
        } else if (file.type.includes('word')) {
            text = await readWordFile(file);
        }
        
        if (!text) {
            throw new Error('Impossible de lire le contenu du fichier');
        }
        
        console.log('📝 Texte extrait du fichier (', text.length, 'caractères)');
        
        // Analyser le texte extrait
        let result;
        
        if (jobParserInstance) {
            result = jobParserInstance.analyzeJobLocally(text);
            console.log('✅ Analyse locale réussie:', result);
        } else {
            result = createFallbackAnalysis(text);
            console.log('⚠️ Utilisation du fallback simple');
        }
        
        // Sauvegarder et afficher les résultats
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        displayJobResults(result);
        
        showNotification(`✅ Fichier "${file.name}" analysé avec succès !`, 'success');
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'analyse du fichier:', error);
        showNotification('Erreur lors de l\'analyse du fichier: ' + error.message, 'error');
    } finally {
        parsingInProgress = false;
        showLoader(false);
    }
}

/**
 * Lit un fichier texte
 */
function readTextFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = () => reject(new Error('Erreur lecture fichier texte'));
        reader.readAsText(file);
    });
}

/**
 * Lit un fichier PDF (basique)
 */
async function readPDFFile(file) {
    try {
        // Utiliser une lecture basique comme texte en attendant une meilleure implémentation
        const text = await readTextFile(file);
        return text;
    } catch (error) {
        throw new Error('Impossible de lire le fichier PDF. Essayez de copier-coller le texte.');
    }
}

/**
 * Lit un fichier Word (basique)
 */
async function readWordFile(file) {
    try {
        // Utiliser une lecture basique comme texte en attendant une meilleure implémentation
        const text = await readTextFile(file);
        return text;
    } catch (error) {
        throw new Error('Impossible de lire le fichier Word. Essayez de copier-coller le texte.');
    }
}

/**
 * Crée une analyse fallback simple si l'API n'est pas disponible
 */
function createFallbackAnalysis(text) {
    console.log('🔄 Création d\'une analyse fallback...');
    
    // Extraction basique avec regex simples
    const title = extractSimpleTitle(text);
    const location = extractSimpleLocation(text);
    const contract = extractSimpleContract(text);
    const experience = extractSimpleExperience(text);
    const skills = extractSimpleSkills(text);
    
    return {
        title: title || 'Titre non détecté',
        company: '',
        location: location || '',
        contract_type: contract || '',
        skills: skills,
        experience: experience || '',
        education: '',
        salary: '',
        responsibilities: [],
        benefits: []
    };
}

// Fonctions d'extraction simple pour le fallback
function extractSimpleTitle(text) {
    const lines = text.split('\n').slice(0, 5);
    for (const line of lines) {
        const cleanLine = line.trim();
        if (cleanLine.length > 5 && cleanLine.length < 80) {
            const jobWords = ['développeur', 'assistant', 'responsable', 'chef', 'directeur', 'commercial', 'comptable'];
            if (jobWords.some(word => cleanLine.toLowerCase().includes(word))) {
                return cleanLine;
            }
        }
    }
    return null;
}

function extractSimpleLocation(text) {
    const match = text.match(/(?:paris|lyon|marseille|toulouse|lille|bordeaux|nantes)/i);
    return match ? match[0] : null;
}

function extractSimpleContract(text) {
    const match = text.match(/\b(CDI|CDD|STAGE|INTERIM)\b/i);
    return match ? match[0].toUpperCase() : null;
}

function extractSimpleExperience(text) {
    const match = text.match(/(\d+\s*(?:ans?|années?)\s*(?:d'expérience|expérience))/i);
    return match ? match[0] : null;
}

function extractSimpleSkills(text) {
    const skills = ['JavaScript', 'Excel', 'Word', 'PowerPoint', 'SAP', 'Autonomie', 'Rigueur', 'Communication'];
    return skills.filter(skill => text.toLowerCase().includes(skill.toLowerCase()));
}

/**
 * Affiche les résultats d'analyse dans l'interface
 */
function displayJobResults(data) {
    console.log('📊 Affichage des résultats:', data);
    
    // Afficher le conteneur des résultats
    const container = document.getElementById('job-info-container');
    if (container) {
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Remplir tous les champs
    updateResultField('job-title-value', data.title);
    updateResultField('job-contract-value', data.contract_type);
    updateResultField('job-location-value', data.location);
    updateResultField('job-experience-value', data.experience);
    updateResultField('job-education-value', data.education);
    updateResultField('job-salary-value', data.salary);
    
    // Compétences avec tags
    updateSkillsField('job-skills-value', data.skills);
    
    // Responsabilités
    updateListField('job-responsibilities-value', data.responsibilities);
    
    // Avantages
    updateListField('job-benefits-value', data.benefits);
}

/**
 * Met à jour un champ de résultat
 */
function updateResultField(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value || 'Non spécifié';
    }
}

/**
 * Met à jour le champ des compétences avec des tags
 */
function updateSkillsField(id, skills) {
    const element = document.getElementById(id);
    if (!element) return;
    
    if (Array.isArray(skills) && skills.length > 0) {
        element.innerHTML = '';
        skills.forEach(skill => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = skill;
            element.appendChild(tag);
        });
    } else {
        element.textContent = 'Non spécifié';
    }
}

/**
 * Met à jour un champ de liste
 */
function updateListField(id, items) {
    const element = document.getElementById(id);
    if (!element) return;
    
    if (Array.isArray(items) && items.length > 0) {
        element.innerHTML = '';
        const ul = document.createElement('ul');
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            ul.appendChild(li);
        });
        element.appendChild(ul);
    } else {
        element.textContent = 'Non spécifié';
    }
}

/**
 * Affiche/cache le loader
 */
function showLoader(show) {
    const loader = document.getElementById('analysis-loader');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}

/**
 * Affiche une notification
 */
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);
    
    // Essayer d'utiliser la fonction globale si disponible
    if (window.QuestionnaireNavigation && window.QuestionnaireNavigation.showNotification) {
        window.QuestionnaireNavigation.showNotification(message, type);
        return;
    }
    
    // Créer une notification personnalisée
    createCustomNotification(message, type);
}

/**
 * Crée une notification personnalisée
 */
function createCustomNotification(message, type) {
    // Supprimer les notifications existantes
    const existingNotifications = document.querySelectorAll('.custom-notification');
    existingNotifications.forEach(notif => notif.remove());
    
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `custom-notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        padding: 15px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        max-width: 350px;
        border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        animation: slideIn 0.3s ease;
    `;
    
    // Ajouter l'icône et le message
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">${icon}</span>
            <span>${message}</span>
        </div>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Supprimer après 5 secondes
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Test le setup du job parser
 */
function testJobParserSetup() {
    console.log('🧪 Test du setup job parser...');
    
    const results = {
        jobParserAPI: !!window.JobParserAPI,
        jobParserInstance: !!jobParserInstance,
        recruitmentRadios: !!document.getElementById('recruitment-yes'),
        jobParsingSection: !!document.getElementById('job-parsing-section'),
        analyzeButton: !!document.getElementById('analyze-job-text'),
        dropZone: !!document.getElementById('job-drop-zone'),
        fileInput: !!document.getElementById('job-file-input'),
        jobTextarea: !!document.getElementById('job-description-text'),
        resultsContainer: !!document.getElementById('job-info-container')
    };
    
    console.log('📋 Résultats du test:', results);
    
    const allGood = Object.values(results).every(Boolean);
    
    if (allGood) {
        console.log('✅ Tous les composants sont en place !');
        showNotification('🎉 Job Parser complètement opérationnel !', 'success');
    } else {
        console.warn('⚠️ Certains composants manquent:', 
            Object.entries(results).filter(([_, value]) => !value).map(([key]) => key)
        );
    }
}

// Ajouter les styles CSS pour les animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .drag-active {
        border-color: var(--primary, #7c3aed) !important;
        background-color: rgba(124, 58, 237, 0.05) !important;
    }
`;
document.head.appendChild(style);

// Exposer les fonctions utiles globalement
window.JobParserIntegrationFix = {
    analyzeJobText,
    analyzeJobFile,
    displayJobResults,
    showNotification,
    testJobParserSetup
};

console.log('✅ Job Parser Integration Fix chargé avec succès !');
