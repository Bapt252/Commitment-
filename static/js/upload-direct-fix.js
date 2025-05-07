/**
 * Script de contournement direct pour le problème d'upload de fichier
 * Ce script injecte un bouton visible qui déclenchera directement l'input file
 */
(function() {
    console.log("Upload direct fix initializing...");
    
    // Fonction qui s'exécute quand le contenu est chargé
    function applyFix() {
        console.log("Applying direct upload fix");
        
        // Vérifier si nous sommes dans la page parser
        const isParserPage = document.querySelector('.drop-zone') && document.querySelector('.file-input');
        
        if (isParserPage) {
            console.log("Parser page detected, applying fixes");
            
            // Récupérer les éléments existants
            const dropZone = document.querySelector('.drop-zone');
            const fileInput = document.querySelector('.file-input');
            
            if (!dropZone || !fileInput) {
                console.error("Required elements not found");
                return;
            }
            
            // Créer un bouton visible qui remplacera la fonctionnalité de la zone de dépôt
            const uploadButton = document.createElement('button');
            uploadButton.type = 'button';
            uploadButton.className = 'direct-upload-button';
            uploadButton.innerHTML = '<i class="fas fa-file-upload"></i> Sélectionner un fichier';
            uploadButton.style.cssText = `
                background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                margin: 15px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                font-weight: 500;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            `;
            
            // Ajouter le bouton avant la zone de dépôt
            dropZone.parentNode.insertBefore(uploadButton, dropZone);
            
            // Ajouter un gestionnaire d'événement au bouton pour ouvrir le sélecteur de fichier
            uploadButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("Upload button clicked, triggering file input");
                
                // Réinitialiser l'input file (important pour permettre de sélectionner le même fichier deux fois)
                fileInput.value = '';
                
                // Déclencher le clic sur l'input file
                fileInput.click();
            });
            
            // Améliorer l'affichage du nom de fichier sélectionné
            fileInput.addEventListener('change', function() {
                if (fileInput.files && fileInput.files.length > 0) {
                    const fileName = fileInput.files[0].name;
                    dropZone.querySelector('.drop-text').textContent = `Fichier sélectionné : ${fileName}`;
                    dropZone.style.borderColor = '#7C3AED';
                    dropZone.style.backgroundColor = 'rgba(124, 58, 237, 0.05)';
                    
                    // Mettre à jour le texte du bouton
                    uploadButton.innerHTML = '<i class="fas fa-check"></i> Fichier sélectionné';
                    uploadButton.style.backgroundColor = '#10B981';
                }
            });
            
            console.log("Direct upload fix applied successfully");
        } else {
            console.log("Not on parser page, fix not applied");
        }
    }
    
    // S'exécuter lorsque le DOM est chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyFix);
    } else {
        applyFix();
    }
    
    // S'exécuter également après un délai pour s'assurer que tous les éléments sont chargés
    setTimeout(applyFix, 1000);
})();
