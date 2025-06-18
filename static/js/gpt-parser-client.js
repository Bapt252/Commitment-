/**
 * GPT Parser Client - Interface de parsing CV avec OpenAI
 * Ce module gère l'intégration avec l'API OpenAI pour le parsing de CV
 * Compatible avec le déploiement GitHub Pages
 */

class GPTParserClient {
    constructor(options = {}) {
        this.apiKey = options.apiKey || localStorage.getItem('openai_api_key');
        this.baseURL = options.baseURL || 'https://api.openai.com/v1';
        this.model = options.model || 'gpt-3.5-turbo';
        this.fallbackMode = options.fallbackMode || false;
        this.onProgress = options.onProgress || (() => {});
        this.onError = options.onError || (() => {});
        this.onSuccess = options.onSuccess || (() => {});
    }

    /**
     * Parse un CV en utilisant l'API OpenAI
     * @param {File} file - Le fichier CV à analyser
     * @returns {Promise<Object>} - Les données extraites du CV
     */
    async parseCV(file) {
        try {
            this.onProgress('Lecture du fichier...');
            
            // Lire le contenu du fichier
            const content = await this.readFileContent(file);
            
            if (!content || content.trim().length < 50) {
                throw new Error('Le contenu du fichier est trop court ou vide');
            }

            this.onProgress('Analyse avec l\'IA...');

            // Si pas de clé API, utiliser le mode fallback
            if (!this.apiKey) {
                console.warn('Aucune clé API OpenAI détectée, utilisation du mode fallback');
                return this.fallbackParsing(content);
            }

            // Analyse avec OpenAI
            const result = await this.analyzeWithOpenAI(content);
            
            this.onSuccess('Analyse terminée avec succès');
            return result;

        } catch (error) {
            console.error('Erreur lors du parsing:', error);
            
            // En cas d'erreur avec OpenAI, essayer le fallback
            if (this.apiKey && !this.fallbackMode) {
                console.warn('Erreur OpenAI, basculement vers le mode fallback');
                try {
                    const content = await this.readFileContent(file);
                    return this.fallbackParsing(content);
                } catch (fallbackError) {
                    this.onError(fallbackError);
                    throw fallbackError;
                }
            } else {
                this.onError(error);
                throw error;
            }
        }
    }

    /**
     * Lit le contenu d'un fichier selon son type
     * @param {File} file - Le fichier à lire
     * @returns {Promise<string>} - Le contenu textuel du fichier
     */
    async readFileContent(file) {
        const fileType = file.type.toLowerCase();
        const fileName = file.name.toLowerCase();

        if (fileType === 'text/plain' || fileName.endsWith('.txt')) {
            return this.readTextFile(file);
        } else if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
            return this.readPDFFile(file);
        } else if (fileType.includes('word') || fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
            return this.readWordFile(file);
        } else {
            // Essayer de lire comme un fichier texte
            return this.readTextFile(file);
        }
    }

    /**
     * Lit un fichier texte
     */
    async readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Erreur lors de la lecture du fichier'));
            reader.readAsText(file);
        });
    }

    /**
     * Lit un fichier PDF (méthode simplifiée pour GitHub Pages)
     */
    async readPDFFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    const textDecoder = new TextDecoder();
                    const str = textDecoder.decode(new Uint8Array(content));
                    
                    // Extraction basique de texte depuis un PDF
                    let text = '';
                    const lines = str.split('\n');
                    
                    for (const line of lines) {
                        // Rechercher des lignes contenant du texte lisible
                        if (line.match(/[a-zA-Z0-9]{3,}/)) {
                            const cleanLine = line.replace(/[^\w\s@.-]/g, ' ').trim();
                            if (cleanLine.length > 2) {
                                text += cleanLine + '\n';
                            }
                        }
                    }
                    
                    resolve(text || 'Contenu PDF extrait avec limitations');
                } catch (error) {
                    reject(new Error('Erreur lors de la lecture du PDF'));
                }
            };
            reader.onerror = () => reject(new Error('Erreur lors de la lecture du fichier PDF'));
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Lit un fichier Word (traitement simplifié)
     */
    async readWordFile(file) {
        // Pour les fichiers Word, on va essayer de lire comme du texte
        // En production, utiliser une bibliothèque comme mammoth.js
        return this.readTextFile(file);
    }

    /**
     * Analyse le CV avec l'API OpenAI
     */
    async analyzeWithOpenAI(content) {
        const prompt = this.buildPrompt(content);
        
        try {
            const response = await fetch(`${this.baseURL}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    model: this.model,
                    messages: [
                        {
                            role: 'system',
                            content: 'Tu es un expert en analyse de CV. Extrait les informations de manière précise et structure-les en JSON.'
                        },
                        {
                            role: 'user',
                            content: prompt
                        }
                    ],
                    temperature: 0.1,
                    max_tokens: 1500
                })
            });

            if (!response.ok) {
                throw new Error(`Erreur API OpenAI: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            const aiResponse = data.choices[0].message.content;
            
            // Parser la réponse JSON de l'IA
            return this.parseAIResponse(aiResponse);

        } catch (error) {
            console.error('Erreur OpenAI:', error);
            throw new Error(`Erreur d'analyse IA: ${error.message}`);
        }
    }

    /**
     * Construit le prompt pour l'analyse OpenAI
     */
    buildPrompt(content) {
        return `Analyse ce CV et extrait les informations suivantes au format JSON strict :

{
  "personal_info": {
    "name": "nom complet",
    "email": "adresse email",
    "phone": "numéro de téléphone"
  },
  "current_position": "titre du poste actuel ou dernier poste",
  "skills": ["compétence1", "compétence2", "..."],
  "software": ["logiciel1", "logiciel2", "..."],
  "languages": [
    {"language": "Français", "level": "Natif"},
    {"language": "Anglais", "level": "Courant"}
  ],
  "work_experience": [
    {
      "title": "titre du poste",
      "company": "nom de l'entreprise",
      "start_date": "MM/YYYY",
      "end_date": "MM/YYYY ou Present"
    }
  ]
}

Contenu du CV à analyser :
${content}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.`;
    }

    /**
     * Parse la réponse de l'IA
     */
    parseAIResponse(response) {
        try {
            // Nettoyer la réponse pour extraire le JSON
            let cleanResponse = response.trim();
            
            // Supprimer les balises markdown si présentes
            cleanResponse = cleanResponse.replace(/```json\n?/g, '').replace(/```\n?/g, '');
            
            // Parser le JSON
            const parsed = JSON.parse(cleanResponse);
            
            return {
                data: parsed,
                source: 'openai',
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('Erreur parsing réponse IA:', error);
            console.log('Réponse brute:', response);
            
            // En cas d'erreur de parsing, retourner un format standardisé
            return this.createMockData();
        }
    }

    /**
     * Mode fallback : analyse locale sans IA
     */
    fallbackParsing(content) {
        this.onProgress('Mode local activé...');
        
        const data = {
            personal_info: this.extractPersonalInfo(content),
            current_position: this.extractCurrentPosition(content),
            skills: this.extractSkills(content),
            software: this.extractSoftware(content),
            languages: this.extractLanguages(content),
            work_experience: this.extractWorkExperience(content)
        };

        return {
            data: data,
            source: 'fallback',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Extraction d'informations personnelles (mode fallback)
     */
    extractPersonalInfo(content) {
        const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
        const phoneRegex = /(\+33|0)[1-9](\d{8}|\s\d{2}\s\d{2}\s\d{2}\s\d{2})/;
        
        const email = content.match(emailRegex)?.[0] || '';
        const phone = content.match(phoneRegex)?.[0] || '';
        
        // Extraction basique du nom (première ligne non vide)
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        const name = lines[0]?.trim() || '';

        return { name, email, phone };
    }

    /**
     * Extraction du poste actuel (mode fallback)
     */
    extractCurrentPosition(content) {
        const positionKeywords = ['développeur', 'ingénieur', 'chef', 'manager', 'analyst', 'consultant'];
        const lines = content.toLowerCase().split('\n');
        
        for (const line of lines.slice(0, 10)) {
            if (positionKeywords.some(keyword => line.includes(keyword))) {
                return line.trim();
            }
        }
        
        return 'Position non détectée';
    }

    /**
     * Extraction des compétences (mode fallback)
     */
    extractSkills(content) {
        const techKeywords = [
            'JavaScript', 'Python', 'Java', 'React', 'Angular', 'Vue',
            'Node.js', 'PHP', 'C#', 'C++', 'HTML', 'CSS', 'SQL'
        ];
        
        const foundSkills = [];
        const lowerContent = content.toLowerCase();
        
        for (const skill of techKeywords) {
            if (lowerContent.includes(skill.toLowerCase())) {
                foundSkills.push(skill);
            }
        }
        
        return foundSkills.length > 0 ? foundSkills : ['Compétences à spécifier'];
    }

    /**
     * Extraction des logiciels (mode fallback)
     */
    extractSoftware(content) {
        const softwareKeywords = [
            'Excel', 'Word', 'PowerPoint', 'Photoshop', 'Illustrator',
            'Figma', 'Sketch', 'InDesign', 'AutoCAD', 'SolidWorks'
        ];
        
        const foundSoftware = [];
        const lowerContent = content.toLowerCase();
        
        for (const software of softwareKeywords) {
            if (lowerContent.includes(software.toLowerCase())) {
                foundSoftware.push(software);
            }
        }
        
        return foundSoftware.length > 0 ? foundSoftware : ['Logiciels à spécifier'];
    }

    /**
     * Extraction des langues (mode fallback)
     */
    extractLanguages(content) {
        const languages = [
            { language: 'Français', level: 'Natif' },
            { language: 'Anglais', level: 'À évaluer' }
        ];
        
        if (content.toLowerCase().includes('english') || content.toLowerCase().includes('anglais')) {
            languages[1].level = 'Courant';
        }
        
        return languages;
    }

    /**
     * Extraction de l'expérience (mode fallback)
     */
    extractWorkExperience(content) {
        return [
            {
                title: 'Expérience à compléter',
                company: 'Entreprise à spécifier',
                start_date: 'À définir',
                end_date: 'À définir'
            }
        ];
    }

    /**
     * Crée des données d'exemple en cas d'erreur
     */
    createMockData() {
        return {
            data: {
                personal_info: {
                    name: 'À compléter',
                    email: 'À compléter',
                    phone: 'À compléter'
                },
                current_position: 'À compléter',
                skills: ['Compétences à spécifier'],
                software: ['Logiciels à spécifier'],
                languages: [
                    { language: 'Français', level: 'Natif' },
                    { language: 'Anglais', level: 'À évaluer' }
                ],
                work_experience: [
                    {
                        title: 'Poste à compléter',
                        company: 'Entreprise à spécifier',
                        start_date: 'À définir',
                        end_date: 'À définir'
                    }
                ]
            },
            source: 'mock',
            timestamp: new Date().toISOString()
        };
    }
}

// Exposer la classe globalement
window.GPTParserClient = GPTParserClient;

// Service d'intégration pour compatibilité avec l'interface existante
class CVParserIntegration {
    constructor(options = {}) {
        this.client = new GPTParserClient(options);
        this.onParsingStart = options.onParsingStart || (() => {});
        this.onParsingComplete = options.onParsingComplete || (() => {});
        this.onParsingError = options.onParsingError || (() => {});
    }

    async parseCV(file) {
        this.onParsingStart();
        
        try {
            const result = await this.client.parseCV(file);
            this.onParsingComplete(result);
            return result;
        } catch (error) {
            this.onParsingError(error);
            throw error;
        }
    }
}

// Exposer le service d'intégration
window.CVParserIntegration = CVParserIntegration;

console.log('GPT Parser Client chargé avec succès');
