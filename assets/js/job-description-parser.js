/**
 * Module de parsing de fiche de poste
 * Permet d'extraire les informations d'une fiche de poste et de remplir automatiquement le formulaire
 */

document.addEventListener('DOMContentLoaded', function() {
    // Référence aux éléments DOM
    const parseButton = document.getElementById('parse-job-description');
    const importModal = new bootstrap.Modal(document.getElementById('importJobDescriptionModal'));
    const parseConfirmButton = document.getElementById('parse-confirm');
    const fileInput = document.getElementById('job-description-file');
    const textInput = document.getElementById('job-description-text');

    // Ouvrir la modal lorsqu'on clique sur le bouton d'import
    if (parseButton) {
        parseButton.addEventListener('click', function() {
            importModal.show();
        });
    }

    // Analyser la fiche de poste lorsqu'on clique sur le bouton de confirmation
    if (parseConfirmButton) {
        parseConfirmButton.addEventListener('click', async function() {
            let content = null;

            // Récupérer le contenu à partir du fichier ou du texte collé
            if (fileInput.files.length > 0) {
                content = await readFileContent(fileInput.files[0]);
            } else if (textInput.value.trim()) {
                content = textInput.value.trim();
            }

            if (content) {
                // Analyser le contenu pour extraire les informations pertinentes
                const extractedInfo = parseJobDescription(content);
                
                // Remplir le formulaire avec les informations extraites
                fillFormWithParsedData(extractedInfo);
                
                // Fermer la modal
                importModal.hide();
                
                // Réinitialiser les champs de la modal
                fileInput.value = '';
                textInput.value = '';
                
                // Afficher un message de succès
                showNotification('Informations importées avec succès !', 'success');
            } else {
                showNotification('Veuillez fournir une fiche de poste à analyser.', 'warning');
            }
        });
    }

    /**
     * Lit le contenu d'un fichier
     * @param {File} file - Le fichier à lire
     * @returns {Promise<string>} - Le contenu du fichier
     */
    async function readFileContent(file) {
        // Pour l'instant, cette fonction ne gère que les fichiers texte
        // Dans une implémentation réelle, il faudrait utiliser des bibliothèques
        // comme pdf.js ou mammoth.js pour lire des fichiers PDF ou DOCX
        return new Promise((resolve, reject) => {
            if (file.type === 'text/plain') {
                const reader = new FileReader();
                reader.onload = function(e) {
                    resolve(e.target.result);
                };
                reader.onerror = function(e) {
                    reject(new Error('Erreur lors de la lecture du fichier'));
                };
                reader.readAsText(file);
            } else {
                // Simuler une extraction pour les fichiers PDF et DOCX
                // Dans une implémentation réelle, vous utiliseriez des bibliothèques dédiées
                setTimeout(() => {
                    resolve(`Contenu extrait du fichier ${file.name}\n\nCeci est une simulation de contenu extrait.\n\nTitre du poste: ${file.name.replace(/\.\w+$/, '')}\n\nDescription: Ce poste requiert une expérience de 3-5 ans dans le domaine.\n\nResponsabilités principales:\n- Développement de fonctionnalités\n- Maintenance de code existant\n- Collaboration avec l'équipe\n\nCompétences requises:\n- JavaScript\n- HTML/CSS\n- Expérience avec les frameworks modernes`);
                }, 1000);
            }
        });
    }

    /**
     * Analyse une fiche de poste pour en extraire les informations
     * @param {string} content - Le contenu de la fiche de poste
     * @returns {Object} - Les informations extraites
     */
    function parseJobDescription(content) {
        // Objet pour stocker les informations extraites
        const result = {
            title: null,
            description: content, // Par défaut, on garde tout le contenu
            experience: null,
            sector: null
        };

        // Extraction du titre
        const titleMatch = content.match(/(?:poste|titre|intitulé)\s*(?:du poste)?\s*[:\-]\s*([^\n.]+)/i) ||
                        content.match(/([^\n.]+(?:développeur|ingénieur|chef de projet|directeur|manager|consultant|technicien|analyste)[^\n.]*)/i);
        if (titleMatch) {
            result.title = titleMatch[1].trim();
        }

        // Extraction de l'expérience requise
        const expMatch = content.match(/(?:expérience|exp)\s*(?:requise|demandée|souhaitée)?\s*[:\-]?\s*(\d+)[- ](\d+)\s*ans/i) ||
                        content.match(/(\d+)[- ](\d+)\s*ans d'expérience/i);
        if (expMatch) {
            const minExp = parseInt(expMatch[1]);
            const maxExp = parseInt(expMatch[2]);

            // Conversion en catégorie d'expérience
            if (minExp < 2) {
                result.experience = '0-2';
            } else if (minExp < 5 || maxExp <= 5) {
                result.experience = '2-5';
            } else if (minExp < 10 || maxExp <= 10) {
                result.experience = '5-10';
            } else {
                result.experience = '10+';
            }
        }

        // Extraction du secteur d'activité
        const sectorMatches = {
            'tech': /(?:technologie|informatique|IT|digital|web|software|logiciel)/i,
            'finance': /(?:finance|banque|assurance|comptabilité|audit)/i,
            'health': /(?:santé|médical|pharma|hôpital|clinique)/i,
            'retail': /(?:commerce|retail|distribution|vente|magasin)/i,
            'education': /(?:éducation|enseignement|formation|école|université)/i,
            'manufacturing': /(?:industrie|production|fabrication|manufacture|usine)/i,
            'services': /(?:service|conseil|consulting|prestataire)/i
        };

        for (const [sector, regex] of Object.entries(sectorMatches)) {
            if (regex.test(content)) {
                result.sector = sector;
                break;
            }
        }

        // Extraction de la description (si possible, on isole les parties pertinentes)
        const descriptionMatch = content.match(/(?:description|descriptif|missions|responsabilités)\s*(?:du poste)?\s*[:\-]\s*([\s\S]+?)(?:\n\n|\n\r\n|$)/i);
        if (descriptionMatch) {
            result.description = descriptionMatch[1].trim();
        }

        return result;
    }

    /**
     * Remplit le formulaire avec les données extraites
     * @param {Object} data - Les données extraites de la fiche de poste
     */
    function fillFormWithParsedData(data) {
        // Remplir le titre du poste
        if (data.title) {
            const jobTitleInput = document.getElementById('job-title');
            if (jobTitleInput) jobTitleInput.value = data.title;
        }

        // Remplir la description
        if (data.description) {
            const jobDescriptionInput = document.getElementById('job-description');
            if (jobDescriptionInput) jobDescriptionInput.value = data.description;
        }

        // Sélectionner l'expérience requise
        if (data.experience) {
            const experienceSelect = document.getElementById('experience-required');
            if (experienceSelect) experienceSelect.value = data.experience;
        }

        // Définir le secteur d'activité si extrait
        if (data.sector) {
            // Activer l'option "Obligatoire" pour la connaissance du secteur
            const secteurOui = document.getElementById('secteur-oui');
            if (secteurOui) {
                secteurOui.checked = true;
                // Simuler l'événement de changement pour afficher le sélecteur de secteur
                const event = new Event('change');
                secteurOui.dispatchEvent(event);
            }

            // Sélectionner le secteur
            const sectorSelect = document.getElementById('activity-sector');
            if (sectorSelect) sectorSelect.value = data.sector;
        }
    }

    /**
     * Affiche une notification à l'utilisateur
     * @param {string} message - Le message à afficher
     * @param {string} type - Le type de notification (success, warning, error, info)
     */
    function showNotification(message, type = 'info') {
        // Créer l'élément de notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '300px';
        notification.innerHTML = message;

        // Ajouter la notification au document
        document.body.appendChild(notification);

        // Supprimer la notification après 3 secondes
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
});
