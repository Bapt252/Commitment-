// Classe pour gérer l'analyse GPT des fiches de poste
class GptParserClient {
    constructor(options = {}) {
        // Configuration par défaut
        this.options = {
            debug: options.debug || false,
            apiUrl: options.apiUrl || 'http://localhost:5055'
        };
        
        // S'assurer que l'URL ne se termine pas par un slash
        this.options.apiUrl = this.options.apiUrl.endsWith('/') 
            ? this.options.apiUrl.slice(0, -1) 
            : this.options.apiUrl;
            
        if (this.options.debug) {
            console.log('GptParserClient initialisé avec', this.options);
        }
    }
    
    // Méthode pour analyser un fichier avec GPT
    async analyzeFile(file) {
        if (this.options.debug) {
            console.log('Envoi du fichier pour analyse GPT:', file.name);
        }
        
        // Créer un FormData pour l'envoi du fichier
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            // Appeler l'API
            const response = await fetch(`${this.options.apiUrl}/api/parse-with-gpt`, {
                method: 'POST',
                body: formData
            });
            
            // Vérifier si la requête a réussi
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erreur lors de l\'analyse du document');
            }
            
            // Récupérer les données
            const result = await response.json();
            
            if (this.options.debug) {
                console.log('Résultat de l\'analyse GPT:', result);
            }
            
            return result;
        } catch (error) {
            console.error('Erreur lors de l\'analyse GPT:', error);
            throw error;
        }
    }
    
    // Méthode pour remplir les champs du formulaire avec les données extraites
    fillFormFields(data) {
        if (this.options.debug) {
            console.log('Remplissage des champs du formulaire avec:', data);
        }
        
        // Mapping entre les champs renvoyés par GPT et les champs du formulaire
        const fieldMapping = {
            'titre_poste': '#job-title-value',
            'entreprise': '#company-name',
            'localisation': '#job-location-value',
            'type_contrat': '#job-contract-value',
            'competences': '#job-skills-value',
            'experience': '#job-experience-value',
            'formation': '#job-education-value',
            'salaire': '#job-salary-value',
            'description': '#job-responsibilities-value'
        };
        
        // Pour chaque champ dans le mapping
        for (const [dataKey, selector] of Object.entries(fieldMapping)) {
            if (data[dataKey]) {
                const field = document.querySelector(selector);
                
                if (field) {
                    // Traitement spécial pour les compétences (tableau)
                    if (dataKey === 'competences' && Array.isArray(data[dataKey])) {
                        field.innerHTML = data[dataKey].map(skill => 
                            `<span class="tag">${skill}</span>`
                        ).join('');
                    } 
                    // Traitement normal pour les autres champs
                    else {
                        field.textContent = data[dataKey];
                    }
                }
            }
        }
        
        // Afficher le conteneur des informations
        const infoContainer = document.getElementById('job-info-container');
        if (infoContainer) {
            infoContainer.style.display = 'block';
        }
        
        // Sauvegarder les données dans sessionStorage pour les récupérer plus tard
        sessionStorage.setItem('parsedJobData', JSON.stringify(data));
    }
}

// Exposer la classe globalement
window.GptParserClient = GptParserClient;
