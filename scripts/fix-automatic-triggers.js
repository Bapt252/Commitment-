// Correction automatique des event listeners - Connexion interface → ChatGPT
// Ce script assure que les clics sur l'interface déclenchent automatiquement ChatGPT

console.log('🔗 Correction automatique des event listeners...');

function fixAutomaticChatGPTTriggers() {
    // Attendre que l'instance ChatGPT soit disponible
    if (!window.jobParsingUIGPT || !window.jobParsingUIGPT.gptParser) {
        setTimeout(fixAutomaticChatGPTTriggers, 500);
        return;
    }
    
    console.log('🔧 Correction des triggers automatiques...');
    
    // 1. Corriger le bouton d'analyse de texte
    const analyzeButton = document.getElementById('analyze-job-text');
    if (analyzeButton) {
        // Supprimer tous les event listeners existants
        const newAnalyzeButton = analyzeButton.cloneNode(true);
        analyzeButton.parentNode.replaceChild(newAnalyzeButton, analyzeButton);
        
        // Ajouter le bon event listener
        newAnalyzeButton.addEventListener('click', async () => {
            const textArea = document.getElementById('job-description-text');
            const text = textArea ? textArea.value.trim() : '';
            
            if (!text) {
                console.log('❌ Aucun texte à analyser');
                return;
            }
            
            console.log('🚀 Déclenchement analyse automatique du texte...');
            
            try {
                // Vérifier la clé API
                if (!window.jobParsingUIGPT.gptParser.hasApiKey()) {
                    alert('⚠️ Veuillez configurer votre clé API OpenAI dans la section bleue');
                    return;
                }
                
                // Lancer l'analyse
                await window.jobParsingUIGPT.analyzeJobText(text);
                console.log('✅ Analyse automatique terminée');
                
            } catch (error) {
                console.error('❌ Erreur analyse automatique:', error);
                alert('❌ Erreur : ' + error.message);
            }
        });
        
        console.log('✅ Bouton d\'analyse texte corrigé');
    }
    
    // 2. Corriger l'upload de fichier
    const fileInput = document.getElementById('job-file-input');
    if (fileInput) {
        // Supprimer les event listeners existants
        const newFileInput = fileInput.cloneNode(true);
        fileInput.parentNode.replaceChild(newFileInput, fileInput);
        
        // Ajouter le bon event listener
        newFileInput.addEventListener('change', async (e) => {
            if (e.target.files.length === 0) return;
            
            const file = e.target.files[0];
            console.log('🚀 Déclenchement analyse automatique du fichier:', file.name);
            
            try {
                // Vérifier la clé API
                if (!window.jobParsingUIGPT.gptParser.hasApiKey()) {
                    alert('⚠️ Veuillez configurer votre clé API OpenAI dans la section bleue');
                    return;
                }
                
                // Lancer l'analyse
                await window.jobParsingUIGPT.analyzeFile(file);
                console.log('✅ Analyse automatique fichier terminée');
                
            } catch (error) {
                console.error('❌ Erreur analyse fichier automatique:', error);
                alert('❌ Erreur : ' + error.message);
            }
        });
        
        console.log('✅ Input fichier corrigé');
    }
    
    // 3. Corriger le drag & drop
    const dropZone = document.getElementById('job-drop-zone');
    if (dropZone) {
        // Nettoyer les event listeners existants
        const newDropZone = dropZone.cloneNode(true);
        dropZone.parentNode.replaceChild(newDropZone, dropZone);
        
        // Reconfigurer le drag & drop
        newDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            newDropZone.classList.add('drag-active');
        });
        
        newDropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            newDropZone.classList.remove('drag-active');
        });
        
        newDropZone.addEventListener('drop', async (e) => {
            e.preventDefault();
            newDropZone.classList.remove('drag-active');
            
            const files = e.dataTransfer.files;
            if (files.length === 0) return;
            
            const file = files[0];
            console.log('🚀 Déclenchement analyse automatique drag&drop:', file.name);
            
            try {
                // Vérifier la clé API
                if (!window.jobParsingUIGPT.gptParser.hasApiKey()) {
                    alert('⚠️ Veuillez configurer votre clé API OpenAI dans la section bleue');
                    return;
                }
                
                // Lancer l'analyse
                await window.jobParsingUIGPT.analyzeFile(file);
                console.log('✅ Analyse automatique drag&drop terminée');
                
            } catch (error) {
                console.error('❌ Erreur analyse drag&drop automatique:', error);
                alert('❌ Erreur : ' + error.message);
            }
        });
        
        // Clic pour ouvrir le sélecteur de fichier
        newDropZone.addEventListener('click', () => {
            const fileInput = document.getElementById('job-file-input');
            if (fileInput) {
                fileInput.click();
            }
        });
        
        console.log('✅ Zone drag&drop corrigée');
    }
    
    console.log('🎉 Tous les triggers automatiques sont maintenant opérationnels !');
}

// Lancer la correction
setTimeout(fixAutomaticChatGPTTriggers, 2000);

// Export pour utilisation manuelle si besoin
window.fixAutomaticChatGPTTriggers = fixAutomaticChatGPTTriggers;
