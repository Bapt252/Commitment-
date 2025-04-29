/**
 * Script d'initialisation pour l'intégration du service de parsing CV
 * Ce script doit être inclus après cv-parser-integration.js
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le service de parsing CV
    const cvParser = new CVParserIntegration({
        apiUrl: 'http://localhost:5051/api/v1', // URL du service de parsing GPT
        useAsync: false, // Mode synchrone par défaut
        
        // Callbacks pour suivre le processus
        onParsingStart: (file) => {
            console.log('Début de l\'analyse du CV:', file.name);
            
            // Afficher l'indicateur de chargement s'il existe
            const loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'flex';
            }
            
            // Mettre à jour la barre de progression si elle existe
            const stepperProgress = document.querySelector('.stepper-progress');
            if (stepperProgress) {
                stepperProgress.style.width = '33.33%';
            }
        },
        
        onParsingComplete: (data) => {
            console.log('Analyse du CV terminée:', data);
            
            // Cacher l'indicateur de chargement
            const loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Mise à jour de l'interface avec les données extraites
            updateUI(data);
            
            // Afficher un message de succès
            const successMessage = document.getElementById('successMessage');
            if (successMessage) {
                successMessage.style.display = 'block';
                setTimeout(() => {
                    successMessage.style.display = 'none';
                }, 3000);
            }
        },
        
        onParsingError: (error) => {
            console.error('Erreur lors de l\'analyse du CV:', error);
            
            // Cacher l'indicateur de chargement
            const loadingIndicator = document.getElementById('loadingIndicator');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
            // Afficher l'erreur
            const errorText = document.getElementById('errorText');
            const errorMessage = document.getElementById('errorMessage');
            if (errorText && errorMessage) {
                errorText.textContent = `Erreur lors de l'analyse: ${error.message}`;
                errorMessage.style.display = 'block';
                
                // Masquer le message d'erreur après un délai
                setTimeout(() => {
                    errorMessage.style.display = 'none';
                }, 5000);
            }
        }
    });
    
    // Initialiser le service
    cvParser.init();
    
    // Intercepter l'événement de changement de fichier
    const fileInput = document.getElementById('cvFile');
    if (fileInput) {
        // Sauvegarder le gestionnaire d'événements original s'il existe
        const originalChangeHandler = fileInput.onchange;
        
        // Remplacer par notre gestionnaire qui utilisera le service de parsing
        fileInput.onchange = async function(event) {
            if (this.files && this.files.length > 0) {
                const file = this.files[0];
                
                try {
                    // Vérifier le type de fichier
                    if (!isValidFileType(file)) {
                        showError('Type de fichier non pris en charge. Veuillez charger un fichier PDF, DOC, DOCX, JPG ou PNG.');
                        return;
                    }
                    
                    // Vérifier la taille du fichier
                    if (file.size > 10 * 1024 * 1024) { // 10MB max
                        showError('La taille du fichier dépasse la limite de 10MB.');
                        return;
                    }
                    
                    // Afficher les informations du fichier
                    displayFileInfo(file);
                    
                    // Utiliser notre service de parsing CV
                    await window.parseCV(file);
                    
                } catch (error) {
                    console.error('Erreur lors du traitement du fichier:', error);
                    showError('Une erreur est survenue lors du traitement du fichier.');
                }
            }
            
            // Appeler le gestionnaire original si nécessaire
            if (originalChangeHandler) {
                originalChangeHandler.call(this, event);
            }
        };
    }
    
    // Intercepter l'événement de drop de fichier
    const uploadContainer = document.getElementById('uploadContainer');
    if (uploadContainer) {
        // Sauvegarder le gestionnaire d'événements original s'il existe
        const originalDropHandler = uploadContainer.ondrop;
        
        // Remplacer par notre gestionnaire
        uploadContainer.ondrop = async function(event) {
            event.preventDefault();
            
            if (event.dataTransfer.files.length > 0) {
                const file = event.dataTransfer.files[0];
                
                try {
                    // Vérifier le type de fichier
                    if (!isValidFileType(file)) {
                        showError('Type de fichier non pris en charge. Veuillez charger un fichier PDF, DOC, DOCX, JPG ou PNG.');
                        return;
                    }
                    
                    // Vérifier la taille du fichier
                    if (file.size > 10 * 1024 * 1024) { // 10MB max
                        showError('La taille du fichier dépasse la limite de 10MB.');
                        return;
                    }
                    
                    // Afficher les informations du fichier
                    displayFileInfo(file);
                    
                    // Utiliser notre service de parsing CV
                    await window.parseCV(file);
                    
                } catch (error) {
                    console.error('Erreur lors du traitement du fichier:', error);
                    showError('Une erreur est survenue lors du traitement du fichier.');
                }
            }
            
            // Revenir à l'apparence normale
            this.style.borderColor = '#ddd';
            this.style.backgroundColor = 'transparent';
            
            // Appeler le gestionnaire original si nécessaire
            if (originalDropHandler) {
                originalDropHandler.call(this, event);
            }
        };
    }
    
    /**
     * Vérifie si le type de fichier est valide
     * @param {File} file - Fichier à vérifier
     * @returns {boolean} - true si le fichier est d'un type valide
     */
    function isValidFileType(file) {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png',
            'text/plain'
        ];
        
        const fileExtension = file.name.split('.').pop().toLowerCase();
        const allowedExtensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'];
        
        return allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);
    }
    
    /**
     * Affiche les informations du fichier dans l'interface
     * @param {File} file - Fichier à afficher
     */
    function displayFileInfo(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileInfo = document.getElementById('fileInfo');
        
        if (fileName && fileSize && fileInfo) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'flex';
        }
    }
    
    /**
     * Formate la taille d'un fichier en unités lisibles
     * @param {number} bytes - Taille en octets
     * @returns {string} - Taille formatée
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Affiche un message d'erreur
     * @param {string} message - Message d'erreur à afficher
     */
    function showError(message) {
        const errorText = document.getElementById('errorText');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorText && errorMessage) {
            errorText.textContent = message;
            errorMessage.style.display = 'block';
            
            // Masquer le message après 5 secondes
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }
    }
    
    /**
     * Met à jour l'interface avec les données extraites du CV
     * @param {Object} data - Données extraites
     */
    function updateUI(data) {
        // Récupérer les données importantes
        const personalInfo = data.personal_info || {};
        const skills = data.skills || [];
        const workExperience = data.work_experience || [];
        
        // Mettre à jour les éléments de l'interface si existants
        if (document.getElementById('parsedName')) {
            document.getElementById('parsedName').textContent = personalInfo.name || 'Non détecté';
        }
        
        if (document.getElementById('parsedEmail')) {
            document.getElementById('parsedEmail').textContent = personalInfo.email || 'Non détecté';
        }
        
        if (document.getElementById('parsedPhone')) {
            document.getElementById('parsedPhone').textContent = personalInfo.phone || 'Non détecté';
        }
        
        // Poste actuel (dernier emploi)
        if (document.getElementById('parsedJobTitle')) {
            const latestJob = workExperience.length > 0 ? workExperience[0] : null;
            document.getElementById('parsedJobTitle').textContent = latestJob?.title || 'Non détecté';
        }
        
        // Compétences
        if (document.getElementById('parsedSkills')) {
            const skillsText = Array.isArray(skills) ? skills.join(', ') : 'Non détecté';
            document.getElementById('parsedSkills').textContent = skillsText;
        }
        
        // Expérience (calculée à partir des emplois)
        if (document.getElementById('parsedExperience')) {
            let totalYears = 0;
            if (workExperience.length > 0) {
                workExperience.forEach(job => {
                    const startDate = job.start_date ? new Date(job.start_date) : null;
                    const endDate = job.end_date ? new Date(job.end_date) : new Date();
                    
                    if (startDate) {
                        const years = (endDate.getFullYear() - startDate.getFullYear()) + 
                                     (endDate.getMonth() - startDate.getMonth()) / 12;
                        totalYears += years;
                    }
                });
            }
            
            document.getElementById('parsedExperience').textContent = 
                totalYears > 0 ? `${Math.round(totalYears)} ans` : 'Non détecté';
        }
        
        // Afficher la section de résultats
        const parsedData = document.getElementById('parsedData');
        if (parsedData) {
            parsedData.style.display = 'block';
        }
        
        // Stocker les données pour le chat si la variable existe
        if (window.documentData !== undefined) {
            window.documentData = data;
        }
    }
});
