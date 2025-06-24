// JobParserGPT - Version ChatGPT pour analyse intelligente de fiches de poste
// Remplace les algorithmes locaux par une vraie analyse IA

class JobParserGPT {
    constructor(options = {}) {
        this.apiKey = options.apiKey || this.getStoredApiKey();
        this.debug = options.debug || false;
        this.version = '1.0-GPT-' + Date.now();
        
        // Configuration ChatGPT
        this.gptModel = 'gpt-4o-mini';
        this.maxTokens = 2000;
        
        if (this.debug) {
            console.log('🤖 JobParserGPT v1.0 initialisé');
            console.log('🔑 API Key:', this.apiKey ? 'Configurée' : 'Non configurée');
        }
    }
    
    // ===== GESTION DE LA CLÉ API =====
    
    setApiKey(apiKey) {
        this.apiKey = apiKey;
        this.storeApiKey(apiKey);
        console.log('✅ Clé API ChatGPT configurée');
    }
    
    getStoredApiKey() {
        try {
            return localStorage.getItem('openai_api_key_jobparser');
        } catch (e) {
            return null;
        }
    }
    
    storeApiKey(apiKey) {
        try {
            localStorage.setItem('openai_api_key_jobparser', apiKey);
        } catch (e) {
            console.warn('Impossible de sauvegarder la clé API');
        }
    }
    
    hasApiKey() {
        return this.apiKey && this.apiKey.trim().length > 0;
    }
    
    // ===== PROMPT OPTIMISÉ POUR L'EXTRACTION =====
    
    getJobAnalysisPrompt(jobText) {
        return `Tu es un expert en analyse de fiches de poste. Analyse ce texte et extrais exactement ces 10 informations sous format JSON :

TEXTE À ANALYSER :
${jobText}

INSTRUCTIONS :
- Extrais uniquement les informations présentes dans le texte
- Si une information n'est pas trouvée, utilise une chaîne vide ""
- Sois précis et concis
- Pour les compétences, retourne un tableau de maximum 8 éléments
- Pour les responsabilités, retourne un texte descriptif en français

FORMAT DE RÉPONSE OBLIGATOIRE (JSON valide uniquement) :
{
  "title": "titre exact du poste",
  "company": "nom de l'entreprise",
  "location": "ville/région",
  "contract_type": "type de contrat (CDI/CDD/Stage/etc)",
  "experience": "expérience requise",
  "education": "formation demandée", 
  "salary": "rémunération mentionnée",
  "skills": ["compétence1", "compétence2", "compétence3"],
  "responsibilities": "description des missions et responsabilités",
  "benefits": "avantages proposés"
}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.`;
    }
    
    // ===== EXTRACTION DES FICHIERS =====
    
    async extractTextFromFile(file) {
        const fileType = file.type;
        
        if (fileType === 'text/plain') {
            return await this.readTextFile(file);
        } else if (fileType === 'application/pdf') {
            return await this.extractTextFromPDF(file);
        } else if (fileType.includes('word') || fileType.includes('document')) {
            return await this.extractTextFromWord(file);
        } else {
            throw new Error('Type de fichier non supporté: ' + fileType);
        }
    }
    
    async readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur lecture fichier texte'));
            reader.readAsText(file, 'utf-8');
        });
    }
    
    async extractTextFromPDF(file) {
        try {
            // Vérifier que PDF.js est chargé
            if (typeof pdfjsLib === 'undefined') {
                throw new Error('PDF.js non disponible');
            }
            
            const arrayBuffer = await this.fileToArrayBuffer(file);
            const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
            
            let fullText = '';
            
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                const page = await pdf.getPage(pageNum);
                const textContent = await page.getTextContent();
                
                const pageText = textContent.items
                    .map(item => item.str)
                    .join(' ');
                
                fullText += pageText + '\n';
            }
            
            return this.cleanExtractedText(fullText);
            
        } catch (error) {
            console.error('Erreur extraction PDF:', error);
            throw new Error('Impossible d\'extraire le texte du PDF: ' + error.message);
        }
    }
    
    async extractTextFromWord(file) {
        // Pour les fichiers Word, on utilise une approche simplifiée
        // En production, vous pourriez utiliser une bibliothèque comme mammoth.js
        try {
            const text = await this.readTextFile(file);
            return this.cleanExtractedText(text);
        } catch (error) {
            throw new Error('Extraction de fichier Word non implémentée complètement');
        }
    }
    
    fileToArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = e => reject(new Error('Erreur lecture fichier'));
            reader.readAsArrayBuffer(file);
        });
    }
    
    cleanExtractedText(text) {
        return text
            .replace(/\s+/g, ' ')  // Normaliser les espaces
            .replace(/\n+/g, '\n') // Normaliser les retours à la ligne
            .trim();
    }
    
    // ===== ANALYSE AVEC CHATGPT =====
    
    async analyzeJobWithGPT(text) {
        if (!this.hasApiKey()) {
            throw new Error('Clé API ChatGPT non configurée');
        }
        
        if (!text || text.trim().length < 50) {
            throw new Error('Texte trop court pour analyse');
        }
        
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    model: this.gptModel,
                    messages: [
                        {
                            role: 'system',
                            content: 'Tu es un expert en analyse de fiches de poste. Tu dois extraire des informations précises et retourner uniquement du JSON valide.'
                        },
                        {
                            role: 'user',
                            content: this.getJobAnalysisPrompt(text)
                        }
                    ],
                    max_tokens: this.maxTokens,
                    temperature: 0.1,
                    response_format: { type: "json_object" }
                })
            });
            
            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`Erreur API OpenAI (${response.status}): ${errorData}`);
            }
            
            const data = await response.json();
            
            if (!data.choices || !data.choices[0] || !data.choices[0].message) {
                throw new Error('Réponse API invalide');
            }
            
            const result = JSON.parse(data.choices[0].message.content);
            
            return this.validateAndCleanResult(result);
            
        } catch (error) {
            console.error('Erreur analyse GPT:', error);
            throw error;
        }
    }
    
    validateAndCleanResult(result) {
        // Valider et nettoyer le résultat
        const validatedResult = {
            title: (result.title || '').substring(0, 100),
            company: (result.company || '').substring(0, 100),
            location: (result.location || '').substring(0, 100),
            contract_type: (result.contract_type || '').substring(0, 50),
            experience: (result.experience || '').substring(0, 200),
            education: (result.education || '').substring(0, 200),
            salary: (result.salary || '').substring(0, 100),
            skills: Array.isArray(result.skills) ? result.skills.slice(0, 8) : [],
            responsibilities: (result.responsibilities || '').substring(0, 1000),
            benefits: (result.benefits || '').substring(0, 500)
        };
        
        return validatedResult;
    }
    
    // ===== MÉTHODES PRINCIPALES =====
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Analyse fichier avec ChatGPT:', file.name);
        }
        
        try {
            // Étape 1: Extraire le texte
            const text = await this.extractTextFromFile(file);
            
            if (this.debug) {
                console.log('✅ Texte extrait, longueur:', text.length);
                console.log('📝 Aperçu:', text.substring(0, 200) + '...');
            }
            
            // Étape 2: Analyser avec GPT
            return await this.analyzeJobWithGPT(text);
            
        } catch (error) {
            console.error('Erreur parsing fichier:', error);
            throw error;
        }
    }
    
    async parseJobText(text) {
        if (this.debug) {
            console.log('📝 Analyse texte avec ChatGPT, longueur:', text.length);
        }
        
        try {
            return await this.analyzeJobWithGPT(text);
        } catch (error) {
            console.error('Erreur parsing texte:', error);
            throw error;
        }
    }
    
    // ===== MÉTHODES UTILITAIRES =====
    
    async testConnection() {
        if (!this.hasApiKey()) {
            throw new Error('Clé API non configurée');
        }
        
        try {
            const testText = `Intitulé du poste : Développeur Web
Entreprise : TechCorp
Localisation : Paris
Type de contrat : CDI
Expérience : 3 ans minimum
Formation : Bac+3 en informatique
Compétences : JavaScript, React, Node.js
Missions : Développement d'applications web
Salaire : 45k€
Avantages : Télétravail, mutuelle`;
            
            const result = await this.analyzeJobWithGPT(testText);
            
            if (this.debug) {
                console.log('✅ Test de connexion réussi:', result);
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ Test de connexion échoué:', error);
            throw error;
        }
    }
}

// ===== INTÉGRATION GLOBALE =====

// Remplacer l'ancienne instance si elle existe
if (typeof window !== 'undefined') {
    window.JobParserGPT = JobParserGPT;
    
    // Créer une instance globale
    window.jobParserGPTInstance = new JobParserGPT({ debug: true });
    
    console.log('🤖 JobParserGPT chargé et prêt !');
    console.log('📋 Fonctionnalités:');
    console.log('  - Analyse fichiers PDF/DOCX/TXT');
    console.log('  - Extraction texte + ChatGPT');
    console.log('  - 10 champs extraits automatiquement');
    console.log('  - Configuration clé API');
}

// Export pour modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JobParserGPT;
}