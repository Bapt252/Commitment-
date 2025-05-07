/**
 * Script de correction pour le problème d'upload de fichier
 * Ce script s'assure que le clic sur l'icône du nuage fonctionne correctement
 */
(function() {
    console.log("Upload fix initializing...");
    
    // Fonction qui s'exécute quand le contenu est chargé
    function applyFix() {
        console.log("Applying upload fix");
        
        // Vérifier si nous sommes dans la page parser
        const isParserPage = document.querySelector('.drop-zone') && document.querySelector('.file-input');
        
        if (isParserPage) {
            console.log("Parser page detected, applying fixes");
            
            // Récupérer les éléments existants
            const dropZone = document.querySelector('.drop-zone');
            const fileInput = document.querySelector('.file-input');
            const cloudIcon = document.querySelector('.drop-icon');
            
            if (!dropZone || !fileInput) {
                console.error("Required elements not found");
                return;
            }
            
            // S'assurer que le clic sur la zone de dépôt ouvre le sélecteur de fichier
            dropZone.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("Drop zone clicked, triggering file input");
                fileInput.click();
            });
            
            // S'assurer spécifiquement que le clic sur l'icône du nuage fonctionne aussi
            if (cloudIcon) {
                cloudIcon.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log("Cloud icon clicked, triggering file input");
                    fileInput.click();
                });
            }
            
            // Améliorer l'affichage du nom de fichier sélectionné
            fileInput.addEventListener('change', function() {
                if (fileInput.files && fileInput.files.length > 0) {
                    const fileName = fileInput.files[0].name;
                    const dropText = dropZone.querySelector('.drop-text');
                    if (dropText) {
                        dropText.textContent = `Fichier sélectionné : ${fileName}`;
                        dropZone.style.borderColor = '#7C3AED';
                        dropZone.style.backgroundColor = 'rgba(124, 58, 237, 0.05)';
                    }
                }
            });
            
            console.log("Upload fix applied successfully");
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