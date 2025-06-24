// Fix Event Listeners - S'assurer que l'analyse se déclenche automatiquement
// Ce script corrige le problème des event listeners qui ne se déclenchent pas

console.log('🔧 Fix Event Listeners - Chargement...');

function forceAttachEventListeners() {
    console.log('🔗 Attachement forcé des event listeners...');
    
    // Attendre que l'instance soit disponible
    if (!window.jobParsingUIGPT) {
        console.log('⏳ Attente de jobParsingUIGPT...');
        setTimeout(forceAttachEventListeners, 500);
        return;
    }
    
    const instance = window.jobParsingUIGPT;
    
    // Réattacher les event listeners pour l'upload de fichier
    const fileInput = document.getElementById('job-file-input');
    const dropZone = document.getElementById('job-drop-zone');
    
    if (fileInput && dropZone) {
        // Nettoyer les anciens event listeners
        fileInput.removeEventListener('change', handleFileChange);
        dropZone.removeEventListener('drop', handleFileDrop);
        dropZone.removeEventListener('click', handleDropZoneClick);
        
        // Réattacher avec de nouveaux handlers
        function handleFileChange(e) {
            console.log('📁 Fichier sélectionné via input:', e.target.files[0]?.name);
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                console.log('🚀 Déclenchement analyse automatique fichier...');
                instance.handleFileSelection(file);
            }
        }
        
        function handleFileDrop(e) {
            e.preventDefault();
            dropZone.classList.remove('drag-active');
            console.log('📁 Fichier droppé:', e.dataTransfer.files[0]?.name);
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                console.log('🚀 Déclenchement analyse automatique drop...');
                instance.handleFileSelection(file);
            }
        }
        
        function handleDropZoneClick() {
            console.log('🖱️ Clic sur drop zone');
            fileInput.click();
        }
        
        // Attacher les nouveaux event listeners
        fileInput.addEventListener('change', handleFileChange);
        dropZone.addEventListener('drop', handleFileDrop);
        dropZone.addEventListener('click', handleDropZoneClick);
        
        // Gestion du drag
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-active');
        });
        
        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-active');
        });
        
        console.log('✅ Event listeners fichier réattachés');
    }
    
    // Réattacher l'event listener pour le bouton d'analyse texte
    const analyzeButton = document.getElementById('analyze-job-text');
    const textArea = document.getElementById('job-description-text');
    
    if (analyzeButton && textArea) {
        // Nettoyer l'ancien event listener
        analyzeButton.removeEventListener('click', handleAnalyzeClick);
        
        function handleAnalyzeClick() {
            console.log('🤖 Clic sur bouton analyse');
            const text = textArea.value.trim();
            console.log('📝 Texte à analyser, longueur:', text.length);
            
            if (text) {
                console.log('🚀 Déclenchement analyse automatique texte...');
                instance.analyzeJobText(text);
            } else {
                console.log('❌ Pas de texte à analyser');
                instance.showNotification('error', 'Texte requis', 'Veuillez saisir le texte de la fiche de poste.');
            }
        }
        
        // Attacher le nouveau event listener
        analyzeButton.addEventListener('click', handleAnalyzeClick);
        
        console.log('✅ Event listener bouton analyse réattaché');
    }
    
    // Event listener pour détecter automatiquement quand du texte est collé
    if (textArea) {
        textArea.removeEventListener('input', handleTextInput);
        
        function handleTextInput() {
            const text = textArea.value.trim();
            // Si le texte fait plus de 100 caractères et contient des mots clés de fiche de poste
            if (text.length > 100 && (
                text.toLowerCase().includes('poste') || 
                text.toLowerCase().includes('entreprise') ||
                text.toLowerCase().includes('mission') ||
                text.toLowerCase().includes('compétence') ||
                text.toLowerCase().includes('expérience')
            )) {
                console.log('📝 Texte de fiche de poste détecté automatiquement');
                
                // Attendre un peu que l'utilisateur finisse de coller
                setTimeout(() => {
                    const finalText = textArea.value.trim();
                    if (finalText.length > 100) {
                        console.log('🚀 Déclenchement analyse automatique après détection...');
                        instance.analyzeJobText(finalText);
                    }
                }, 1000);
            }
        }
        
        textArea.addEventListener('input', handleTextInput);
        console.log('✅ Auto-détection texte activée');
    }
    
    // Vérifier que les champs de résultats existent
    const resultFields = [
        'job-title-value',
        'job-contract-value', 
        'job-location-value',
        'job-experience-value',
        'job-education-value',
        'job-salary-value',
        'job-skills-value',
        'job-responsibilities-value',
        'job-benefits-value'
    ];
    
    let missingFields = 0;
    resultFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (!field) {
            console.error(`❌ Champ ${fieldId} manquant`);
            missingFields++;
        }
    });
    
    if (missingFields === 0) {
        console.log('✅ Tous les champs de résultats sont présents');
    } else {
        console.error(`❌ ${missingFields} champs de résultats manquants`);
    }
    
    console.log('🎯 Event listeners automatiques configurés !');
}

// Fonction pour forcer un test automatique
function triggerAutoTest() {
    const textArea = document.getElementById('job-description-text');
    if (textArea && window.jobParsingUIGPT) {
        const testText = `Poste: Développeur Web Frontend
Entreprise: Digital Solutions
Localisation: Lyon, France
Type de contrat: CDI
Expérience: 3 ans minimum en développement web
Formation: Bac+3 en informatique ou équivalent
Compétences techniques: JavaScript, React, HTML/CSS, Git
Missions principales:
- Développement d'interfaces utilisateur modernes
- Intégration avec des APIs REST
- Optimisation des performances frontend
- Collaboration avec l'équipe UX/UI
Rémunération: 42-48k€ selon profil
Avantages:
- Télétravail hybride 3j/semaine
- Mutuelle prise en charge à 100%
- Tickets restaurant
- Formations continues`;
        
        console.log('🧪 Test automatique avec texte prédéfini...');
        textArea.value = testText;
        
        // Déclencher l'analyse
        setTimeout(() => {
            window.jobParsingUIGPT.analyzeJobText(testText);
        }, 500);
    }
}

// Fonction principale d'initialisation
function initAutoEventListeners() {
    // Attendre que le DOM soit prêt et les scripts chargés
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(forceAttachEventListeners, 1000);
        });
    } else {
        setTimeout(forceAttachEventListeners, 1000);
    }
}

// Lancer l'initialisation
initAutoEventListeners();

// Export des fonctions pour debug
window.forceAttachEventListeners = forceAttachEventListeners;
window.triggerAutoTest = triggerAutoTest;

console.log('🔧 Fix Event Listeners chargé !');
console.log('💡 Fonctions disponibles:');
console.log('  - forceAttachEventListeners() : Réattacher tous les event listeners');
console.log('  - triggerAutoTest() : Test automatique avec texte prédéfini');
