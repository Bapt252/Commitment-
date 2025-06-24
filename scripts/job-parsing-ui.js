// Job Parsing UI Script
// Gère l'interface utilisateur pour l'analyse des fiches de poste

class JobParsingUI {
    constructor() {
        this.fileInput = document.getElementById('job-file-input');
        this.dropZone = document.getElementById('job-drop-zone');
        this.textArea = document.getElementById('job-description-text');
        this.analyzeButton = document.getElementById('analyze-job-text');
        this.loader = document.getElementById('analysis-loader');
        this.resultsContainer = document.getElementById('job-info-container');
        this.fileBadge = document.getElementById('file-badge');
        this.fileName = document.getElementById('file-name');
        this.removeFileBtn = document.getElementById('remove-file');
        
        this.init();
    }
    
    init() {
        if (!this.dropZone) return;
        
        this.setupFileUpload();
        this.setupTextAnalysis();
        this.setupFileRemoval();
        
        console.log('✅ Job Parsing UI initialisé');
    }
    
    setupFileUpload() {
        // Gestion du drag & drop
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('drag-active');
        });
        
        this.dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-active');
        });
        
        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-active');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        });
        
        // Clic sur la zone de drop
        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });
        
        // Sélection de fichier
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelection(e.target.files[0]);
                }
            });
        }
    }
    
    setupTextAnalysis() {
        if (this.analyzeButton) {
            this.analyzeButton.addEventListener('click', () => {
                const text = this.textArea.value.trim();
                if (text) {
                    this.analyzeJobText(text);
                } else {
                    this.showNotification('error', 'Texte requis', 'Veuillez saisir le texte de la fiche de poste.');
                }
            });
        }
    }
    
    setupFileRemoval() {
        if (this.removeFileBtn) {
            this.removeFileBtn.addEventListener('click', () => {
                this.clearFile();
            });
        }
    }
    
    handleFileSelection(file) {
        // Vérifier le type de fichier
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showNotification('error', 'Type de fichier non supporté', 'Veuillez sélectionner un fichier PDF, DOCX ou TXT.');
            return;
        }
        
        // Vérifier la taille (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('error', 'Fichier trop volumineux', 'La taille du fichier ne doit pas dépasser 5MB.');
            return;
        }
        
        // Afficher le fichier sélectionné
        this.showSelectedFile(file);
        
        // Analyser le fichier
        this.analyzeFile(file);
    }
    
    showSelectedFile(file) {
        if (this.fileName && this.fileBadge) {
            this.fileName.textContent = file.name;
            this.fileBadge.style.display = 'flex';
            
            // Cacher le texte de drop zone
            const dropText = this.dropZone.querySelector('.drop-zone-text');
            if (dropText) {
                dropText.style.display = 'none';
            }
        }
    }
    
    clearFile() {
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        
        if (this.fileBadge) {
            this.fileBadge.style.display = 'none';
        }
        
        // Réafficher le texte de drop zone
        const dropText = this.dropZone.querySelector('.drop-zone-text');
        if (dropText) {
            dropText.style.display = 'block';
        }
        
        // Cacher les résultats
        this.hideResults();
    }
    
    analyzeFile(file) {
        this.showLoader();
        
        // Simuler l'analyse (à remplacer par votre API)
        setTimeout(() => {
            const mockResults = this.generateMockResults();
            this.displayResults(mockResults);
            this.hideLoader();
        }, 2000);
    }
    
    analyzeJobText(text) {
        this.showLoader();
        
        // Simuler l'analyse du texte
        setTimeout(() => {
            const mockResults = this.generateMockResults(text);
            this.displayResults(mockResults);
            this.hideLoader();
        }, 1500);
    }
    
    generateMockResults(text = '') {
        // Analyse basique du texte pour extraire des informations
        const results = {
            title: 'Non spécifié',
            contract: 'Non spécifié',
            location: 'Non spécifié',
            experience: 'Non spécifié',
            education: 'Non spécifié',
            salary: 'Non spécifié',
            skills: [],
            responsibilities: 'Non spécifié',
            benefits: 'Non spécifié'
        };
        
        if (text) {
            // Extraction basique du titre
            const lines = text.split('\n');
            if (lines.length > 0) {
                results.title = lines[0].trim() || 'Poste à définir';
            }
            
            // Recherche de mots-clés pour les compétences
            const skillKeywords = [
                'JavaScript', 'Python', 'Java', 'React', 'Vue', 'Angular', 'Node.js',
                'HTML', 'CSS', 'SQL', 'Git', 'Docker', 'AWS', 'Azure', 'MongoDB'
            ];
            
            skillKeywords.forEach(skill => {
                if (text.toLowerCase().includes(skill.toLowerCase())) {
                    results.skills.push(skill);
                }
            });
            
            // Recherche de type de contrat
            if (text.toLowerCase().includes('cdi')) {
                results.contract = 'CDI';
            } else if (text.toLowerCase().includes('cdd')) {
                results.contract = 'CDD';
            } else if (text.toLowerCase().includes('stage')) {
                results.contract = 'Stage';
            }
            
            // Recherche de localisation
            const locationPatterns = ['paris', 'lyon', 'marseille', 'toulouse', 'bordeaux', 'lille', 'nantes', 'strasbourg'];
            locationPatterns.forEach(city => {
                if (text.toLowerCase().includes(city)) {
                    results.location = city.charAt(0).toUpperCase() + city.slice(1);
                }
            });
        }
        
        return results;
    }
    
    displayResults(results) {
        if (!this.resultsContainer) return;
        
        // Afficher le conteneur de résultats
        this.resultsContainer.style.display = 'block';
        
        // Remplir les champs
        this.setFieldValue('job-title-value', results.title);
        this.setFieldValue('job-contract-value', results.contract);
        this.setFieldValue('job-location-value', results.location);
        this.setFieldValue('job-experience-value', results.experience);
        this.setFieldValue('job-education-value', results.education);
        this.setFieldValue('job-salary-value', results.salary);
        this.setFieldValue('job-responsibilities-value', results.responsibilities);
        this.setFieldValue('job-benefits-value', results.benefits);
        
        // Afficher les compétences
        this.displaySkills(results.skills);
        
        // Scroll vers les résultats
        this.resultsContainer.scrollIntoView({ behavior: 'smooth' });
        
        this.showNotification('success', 'Analyse terminée', 'Les informations ont été extraites avec succès.');
    }
    
    setFieldValue(fieldId, value) {
        const field = document.getElementById(fieldId);
        if (field) {
            field.textContent = value || 'Non spécifié';
        }
    }
    
    displaySkills(skills) {
        const skillsContainer = document.getElementById('job-skills-value');
        if (!skillsContainer) return;
        
        if (skills && skills.length > 0) {
            skillsContainer.innerHTML = '';
            skills.forEach(skill => {
                const tag = document.createElement('span');
                tag.className = 'tag';
                tag.textContent = skill;
                skillsContainer.appendChild(tag);
            });
        } else {
            skillsContainer.textContent = 'Non spécifié';
        }
    }
    
    showLoader() {
        if (this.loader) {
            this.loader.style.display = 'flex';
        }
    }
    
    hideLoader() {
        if (this.loader) {
            this.loader.style.display = 'none';
        }
    }
    
    hideResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'none';
        }
    }
    
    showNotification(type, title, message) {
        // Utilise la fonction de notification du script principal
        if (window.questionnaireNav) {
            window.questionnaireNav.showNotification(type, title, message);
        } else {
            console.log(`${type.toUpperCase()}: ${title} - ${message}`);
        }
    }
}

// Initialiser l'UI de parsing quand le DOM est prêt
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        window.jobParsingUI = new JobParsingUI();
    }, 200);
});

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParsingUI;
}