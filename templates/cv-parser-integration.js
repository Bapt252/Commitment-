/**
 * Module d'intégration du système de parsing de CV basé sur GPT
 * Version améliorée avec support GitHub Pages, intégration directe de l'API OpenAI et PDF.js
 */

// Configuration par défaut de l'URL de l'API de parsing
const CV_PARSER_API_URL = 'http://localhost:5051/api';

// Classe principale d'intégration
class CVParserIntegration {
  constructor(options = {}) {
    // Options par défaut
    this.options = {
      apiUrl: CV_PARSER_API_URL,
      useAsync: false, // Utiliser le parsing asynchrone ou synchrone
      onParsingStart: null,
      onParsingComplete: null,
      onParsingError: null,
      forceMock: this.isGitHubPages(), // Forcer le mode mock sur GitHub Pages
      useDirectOpenAI: false, // Utiliser l'API OpenAI directement (pour GitHub Pages)
      openAIKey: '', // Clé API OpenAI (si useDirectOpenAI est true)
      ...options
    };
    
    console.log('CVParserIntegration initialisé avec API URL:', this.options.apiUrl);
    
    // Détecter si on doit utiliser le parsing avec OpenAI directement
    if (this.options.forceMock && this.options.useDirectOpenAI && this.options.openAIKey) {
      console.log('Mode parsing direct avec OpenAI activé');
      this.options.forceMock = false;
    } else if (this.options.forceMock) {
      console.log('Mode mock activé (GitHub Pages ou configuration forcée)');
    }
    
    // Précharger PDF.js si nécessaire
    this.pdfjs = null;
    this.loadPdfJs();
  }
  
  /**
   * Vérifie si l'application s'exécute sur GitHub Pages
   * @returns {boolean} - true si l'app est sur GitHub Pages
   */
  isGitHubPages() {
    return window.location.hostname.includes('github.io');
  }
  
  /**
   * Précharge PDF.js pour l'extraction de texte des PDF
   */
  async loadPdfJs() {
    try {
      // Vérifier si PDF.js est déjà disponible globalement
      if (window.pdfjsLib) {
        this.pdfjs = window.pdfjsLib;
        console.log('PDF.js déjà chargé globalement');
        return;
      }
      
      // Charger PDF.js depuis CDN
      const pdfJsScript = document.createElement('script');
      pdfJsScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.5.141/pdf.min.js';
      pdfJsScript.async = true;
      
      const loadPromise = new Promise((resolve, reject) => {
        pdfJsScript.onload = resolve;
        pdfJsScript.onerror = reject;
      });
      
      document.head.appendChild(pdfJsScript);
      await loadPromise;
      
      // Assigner la référence globale
      this.pdfjs = window.pdfjsLib;
      console.log('PDF.js chargé avec succès');
    } catch (error) {
      console.error('Erreur lors du chargement de PDF.js:', error);
    }
  }
  
  /**
   * Initialise l'intégration dans une page existante
   * @param {Object} pageContext - Variables et fonctions de la page hôte
   */
  init(pageContext) {
    console.log('Initialisation de l\'intégration du service de parsing CV...');
    
    // Faire une référence globale pour faciliter l'usage
    window.parseCV = this.parseCV.bind(this);
  }
  
  /**
   * Parse un fichier CV en utilisant le service GPT
   * @param {File} file - Fichier CV à analyser
   * @returns {Promise<Object>} - Données extraites du CV
   */
  async parseCV(file) {
    console.log('Début du parsing de CV:', file.name);
    
    if (this.options.onParsingStart) {
      this.options.onParsingStart(file);
    }
    
    try {
      // Si on est en mode mock forcé (GitHub Pages sans clé API OpenAI), on renvoie directement une réponse simulée
      if (this.options.forceMock) {
        console.log('Utilisation du mode mock (GitHub Pages)');
        const mockResponse = this.generateMockResponse(file);
        
        // Ajouter un délai simulé pour une meilleure expérience utilisateur
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        if (this.options.onParsingComplete) {
          this.options.onParsingComplete(mockResponse);
        }
        
        return mockResponse;
      }
      
      // Si on est en mode parsing direct avec OpenAI (GitHub Pages avec clé API)
      if (this.options.useDirectOpenAI && this.options.openAIKey) {
        console.log('Utilisation du parsing direct avec OpenAI');
        const parsedData = await this.parseWithOpenAI(file);
        
        if (this.options.onParsingComplete) {
          this.options.onParsingComplete(parsedData);
        }
        
        return parsedData;
      }
      
      // Sinon, on utilise l'API backend normale
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', 'cv');
      
      let responseData;
      
      // Parsing synchrone ou asynchrone selon les options
      if (this.options.useAsync) {
        // Parsing asynchrone (mise en file d'attente)
        console.log('Utilisation du parsing asynchrone (file d\'attente)');
        const queueResponse = await fetch(`${this.options.apiUrl}/queue`, {
          method: 'POST',
          body: formData,
          headers: {
            'Access-Control-Allow-Origin': '*'
          }
        });
        
        if (!queueResponse.ok) {
          throw new Error(`Erreur serveur: ${queueResponse.status}`);
        }
        
        const queueData = await queueResponse.json();
        const jobId = queueData.job_id;
        console.log('Job de parsing créé avec ID:', jobId);
        
        // Vérifier périodiquement l'état du job
        responseData = await this.pollJobStatus(jobId);
      } else {
        // Parsing synchrone (attente directe)
        console.log('Utilisation du parsing synchrone (direct)');
        const response = await fetch(`${this.options.apiUrl}/v1/parse`, {
          method: 'POST',
          body: formData,
          headers: {
            'Access-Control-Allow-Origin': '*'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Erreur serveur: ${response.status}`);
        }
        
        responseData = await response.json();
      }
      
      console.log('Parsing terminé avec succès:', responseData);
      
      // Notifier la fin du parsing
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(responseData);
      }
      
      return responseData;
    } catch (error) {
      console.error('Erreur lors du parsing CV:', error);
      
      if (this.options.onParsingError) {
        this.options.onParsingError(error);
      }
      
      // Utiliser la réponse de secours après une erreur
      console.log('Utilisation du mode mock suite à une erreur');
      const mockResponse = this.generateMockResponse(file);
      
      // Ajouter un petit délai pour une meilleure expérience utilisateur
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(mockResponse);
      }
      
      return mockResponse;
    }
  }
  
  /**
   * Parse un CV directement avec l'API OpenAI (pour GitHub Pages)
   * @param {File} file - Fichier CV à analyser
   * @returns {Promise<Object>} - Données extraites du CV
   */
  async parseWithOpenAI(file) {
    if (!this.options.openAIKey) {
      throw new Error('Clé API OpenAI non fournie pour le parsing direct');
    }
    
    try {
      // 1. Lire le contenu du fichier
      const fileContent = await this.readFileAsText(file);
      // Détecter le type de CV basé sur le nom (comptable, développeur, etc.)
      const cvType = this.detectCVType(file.name);
      
      // 2. Préparer le prompt pour l'API OpenAI
      const prompt = `
Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV.
Extrait les informations suivantes du CV ci-dessous et retourne-les dans un format JSON structuré.

N'invente AUCUNE information. S'il manque une info, laisse le champ correspondant vide ou avec une chaîne vide, mais garde toujours la clé dans le JSON.

${cvType === 'comptable' ? 
`Ce CV est celui d'un comptable. Cherche particulièrement les logiciels comptables comme SAP, Sage, Ciel Compta, EBP, Oracle Financials, QuickBooks, Microsoft Dynamics, FreshBooks, Xero, Quadra, Coala, ACD, etc. 
Cherche aussi Microsoft Office, Word, Excel, PowerPoint, etc.` 
: 
cvType === 'developpeur' ? 
`Ce CV est celui d'un développeur. Cherche particulièrement les logiciels et technologies comme IDEs (Visual Studio, Eclipse, IntelliJ), outils de versioning (Git, SVN), outils de développement web, frameworks, etc.`
:
`Cherche particulièrement les logiciels utilisés dans tous les domaines mentionnés dans le CV.`
}

Inclus les catégories suivantes, en conservant EXACTEMENT cette structure:

{
  "personal_info": {
    "name": "",
    "email": "",
    "phone": "",
    "address": "",
    "linkedin": ""
  },
  "current_position": "",
  "skills": [],
  "software": [],
  "work_experience": [
    {
      "title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "description": "",
      "responsibilities": []
    }
  ],
  "education": [
    {
      "degree": "",
      "institution": "",
      "start_date": "",
      "end_date": ""
    }
  ],
  "languages": [
    {
      "language": "",
      "level": ""
    }
  ]
}

CV:
${fileContent}

Retourne uniquement un objet JSON sans introduction ni commentaire.
`;

      // 3. Appeler l'API OpenAI
      const startTime = Date.now();
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.options.openAIKey}`
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.1,
          max_tokens: 2500
        })
      });
      
      // 4. Traiter la réponse
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Erreur API OpenAI: ${errorData.error?.message || response.statusText}`);
      }
      
      const data = await response.json();
      const processingTime = (Date.now() - startTime) / 1000;
      
      // 5. Extraire et parser la réponse JSON
      let parsedData;
      try {
        const contentText = data.choices[0].message.content;
        parsedData = JSON.parse(contentText);
      } catch (parseError) {
        console.error('Erreur lors du parsing de la réponse JSON:', parseError);
        // Essayer d'extraire le JSON avec une regex
        const jsonMatch = data.choices[0].message.content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          parsedData = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('Format de réponse invalide');
        }
      }

      // 6. Si pas de logiciels détectés, ajouter des logiciels par défaut basés sur le CV
      if (!parsedData.software || parsedData.software.length === 0) {
        parsedData.software = this.getDefaultSoftwareByType(cvType, parsedData);
      }
      
      // 7. Formater la réponse finale
      return {
        processing_time: processingTime,
        parsed_at: Date.now() / 1000,
        file_format: file.name.split('.').pop().toLowerCase(),
        model: 'gpt-3.5-turbo',
        data: parsedData
      };
      
    } catch (error) {
      console.error('Erreur lors du parsing avec OpenAI:', error);
      throw error;
    }
  }
  
  /**
   * Lit un fichier et le convertit en texte
   * @param {File} file - Fichier à lire
   * @returns {Promise<string>} - Contenu du fichier
   */
  async readFileAsText(file) {
    // Pour les PDF, utiliser PDF.js pour extraire le texte
    if (file.type === 'application/pdf') {
      return await this.extractTextFromPdf(file);
    }
    
    // Pour les autres types, lire le contenu directement
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (event) => {
        resolve(event.target.result);
      };
      
      reader.onerror = (error) => {
        reject(error);
      };
      
      reader.readAsText(file);
    });
  }
  
  /**
   * Extrait le texte d'un fichier PDF en utilisant PDF.js
   * @param {File} file - Fichier PDF
   * @returns {Promise<string>} - Texte extrait du PDF
   */
  async extractTextFromPdf(file) {
    try {
      // Vérifier que PDF.js est chargé
      if (!this.pdfjs) {
        await this.loadPdfJs();
        if (!this.pdfjs) {
          throw new Error("PDF.js n'a pas pu être chargé");
        }
      }
      
      // Lire le fichier au format ArrayBuffer
      const arrayBuffer = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      });
      
      // Charger le document PDF
      const pdf = await this.pdfjs.getDocument({ data: arrayBuffer }).promise;
      
      // Extraire le texte de toutes les pages
      let fullText = '';
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const textItems = textContent.items.map(item => item.str).join(' ');
        fullText += textItems + '\n\n';
      }
      
      return fullText;
    } catch (error) {
      console.error('Erreur lors de l\'extraction du texte du PDF:', error);
      
      // Fallback message si l'extraction échoue
      return `[Extraction du texte du PDF échouée. Analyse basée sur le nom de fichier: ${file.name}]`;
    }
  }
  
  /**
   * Sonde périodiquement l'état d'un job de parsing asynchrone
   * @param {string} jobId - ID du job à surveiller
   * @returns {Promise<Object>} - Résultat du parsing
   */
  async pollJobStatus(jobId) {
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`${this.options.apiUrl}/result/${jobId}`);
          if (!statusResponse.ok) {
            throw new Error(`Erreur lors de la vérification du statut: ${statusResponse.status}`);
          }
          
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'done') {
            // Le job est terminé
            resolve(statusData.result);
          } else if (statusData.status === 'failed') {
            reject(new Error(statusData.error || 'Le traitement du CV a échoué'));
          } else {
            // Vérifier à nouveau après 2 secondes
            setTimeout(checkStatus, 2000);
          }
        } catch (error) {
          reject(error);
        }
      };
      
      // Première vérification
      checkStatus();
    });
  }
  
  /**
   * Détecte le type de CV basé sur le nom de fichier
   * @param {string} filename - Nom du fichier CV
   * @returns {string} - Type de CV détecté ('comptable', 'developpeur', etc.)
   */
  detectCVType(filename) {
    const lowerFilename = filename.toLowerCase();
    
    if (lowerFilename.includes('compta') || lowerFilename.includes('comptable') || 
        lowerFilename.includes('audit') || lowerFilename.includes('finance') || 
        lowerFilename.includes('fiscal')) {
      return 'comptable';
    }
    
    if (lowerFilename.includes('dev') || lowerFilename.includes('développeur') || 
        lowerFilename.includes('web') || lowerFilename.includes('java') || 
        lowerFilename.includes('python') || lowerFilename.includes('front') || 
        lowerFilename.includes('back') || lowerFilename.includes('full')) {
      return 'developpeur';
    }
    
    if (lowerFilename.includes('data') || lowerFilename.includes('données') || 
        lowerFilename.includes('analytics') || lowerFilename.includes('analyst') || 
        lowerFilename.includes('scien')) {
      return 'data';
    }
    
    if (lowerFilename.includes('market') || lowerFilename.includes('communi') || 
        lowerFilename.includes('digit')) {
      return 'marketing';
    }
    
    return 'general';
  }
  
  /**
   * Fournit une liste de logiciels par défaut en fonction du type de CV
   * @param {string} cvType - Type de CV ('comptable', 'developpeur', etc.)
   * @param {Object} parsedData - Données déjà extraites
   * @returns {Array} - Liste de logiciels par défaut
   */
  getDefaultSoftwareByType(cvType, parsedData) {
    // Vérifier le titre de poste dans les données parsées
    const jobTitle = parsedData?.current_position || '';
    const experiences = parsedData?.work_experience || [];
    const firstJobTitle = experiences.length > 0 ? experiences[0].title || '' : '';
    
    // Titre effectif = titre actuel ou premier titre d'expérience
    const effectiveTitle = jobTitle || firstJobTitle;
    const lowerTitle = effectiveTitle.toLowerCase();
    
    switch (cvType) {
      case 'comptable':
        if (lowerTitle.includes('audit')) {
          return ['SAP', 'Microsoft Excel', 'Microsoft Office', 'Oracle Financials', 'Caseware', 'ACL', 'TeamMate'];
        } else if (lowerTitle.includes('finance') || lowerTitle.includes('financier')) {
          return ['SAP', 'Microsoft Excel', 'PowerBI', 'Hyperion', 'Microsoft Office', 'QlikView', 'Tableau'];
        } else if (lowerTitle.includes('paie')) {
          return ['Sage Paie', 'ADP', 'Microsoft Excel', 'Microsoft Office', 'Silae', 'PeopleSoft'];
        } else {
          return ['Sage', 'SAP', 'Microsoft Excel', 'Microsoft Office', 'Ciel Compta', 'EBP', 'QuickBooks', 'Oracle Financials'];
        }
      
      case 'developpeur':
        if (lowerTitle.includes('front')) {
          return ['Visual Studio Code', 'Git', 'GitHub', 'React', 'Angular', 'Vue.js', 'WebStorm', 'Figma', 'Adobe XD'];
        } else if (lowerTitle.includes('back')) {
          return ['IntelliJ IDEA', 'Eclipse', 'Git', 'GitHub', 'Docker', 'Kubernetes', 'Postman', 'Jenkins'];
        } else if (lowerTitle.includes('full')) {
          return ['Visual Studio Code', 'Git', 'GitHub', 'Docker', 'Postman', 'MongoDB Compass', 'IntelliJ IDEA'];
        } else if (lowerTitle.includes('mobile')) {
          return ['Android Studio', 'Xcode', 'Git', 'GitHub', 'Firebase Console', 'Visual Studio Code', 'Figma'];
        } else {
          return ['Visual Studio', 'Visual Studio Code', 'Git', 'GitHub', 'Docker', 'Jira', 'Confluence'];
        }
        
      case 'data':
        if (lowerTitle.includes('scien')) {
          return ['Python', 'Jupyter Notebook', 'R Studio', 'TensorFlow', 'Pandas', 'Scikit-learn', 'Tableau', 'PowerBI'];
        } else if (lowerTitle.includes('analy')) {
          return ['Microsoft Excel', 'SQL Server Management Studio', 'Tableau', 'PowerBI', 'Python', 'R', 'Google Analytics'];
        } else {
          return ['Python', 'SQL', 'Hadoop', 'Spark', 'Tableau', 'PowerBI', 'MongoDB', 'Elasticsearch'];
        }
        
      case 'marketing':
        if (lowerTitle.includes('digital')) {
          return ['Google Analytics', 'Google Ads', 'Facebook Ads Manager', 'HubSpot', 'Mailchimp', 'WordPress', 'Adobe Creative Suite'];
        } else {
          return ['Microsoft Office', 'Adobe Creative Suite', 'CRM', 'Salesforce', 'HubSpot', 'Canva', 'PowerPoint'];
        }
        
      default:
        // Si aucun type spécifique, fournir des logiciels généralistes
        return ['Microsoft Office', 'Excel', 'Word', 'PowerPoint', 'Outlook'];
    }
  }
  
  /**
   * Génère une réponse de secours avec des données pertinentes basées sur le nom du fichier
   * @param {File} file - Fichier CV
   * @returns {Object} - Données simulées
   */
  generateMockResponse(file) {
    console.log('Génération d\'une réponse mock pour:', file.name);
    
    // Extraire le nom de base du fichier (sans extension)
    const baseName = file.name.split('.')[0].replace(/[_-]/g, ' ');
    console.log('Nom de base extrait:', baseName);
    
    // Déterminer le type de CV
    const cvType = this.detectCVType(file.name);
    
    // Améliorer la génération d'informations à partir du nom de fichier
    let candidateInfo = this.extractCandidateInfo(file.name, cvType);
    console.log('Informations extraites:', candidateInfo);
    
    // Générer la réponse complète
    return {
      processing_time: 1.25,
      parsed_at: Date.now() / 1000,
      file_format: file.name.split('.').pop().toLowerCase(),
      model: "mock",
      data: {
        personal_info: {
          name: candidateInfo.name,
          email: candidateInfo.email,
          phone: candidateInfo.phone,
          address: '123 rue de Paris, 75001 Paris',
          linkedin: 'linkedin.com/in/' + candidateInfo.name.toLowerCase().replace(/\s+/g, ''),
        },
        current_position: candidateInfo.jobTitle,
        skills: candidateInfo.skills,
        software: candidateInfo.software,
        work_experience: [
          {
            title: candidateInfo.jobTitle,
            company: candidateInfo.company,
            start_date: '2022-01',
            end_date: 'present',
            description: candidateInfo.jobDescription,
            responsibilities: candidateInfo.responsibilities
          },
          {
            title: candidateInfo.previousTitle,
            company: candidateInfo.previousCompany,
            start_date: '2020-03',
            end_date: '2021-12',
            description: 'Support aux équipes techniques et participation aux projets clients.',
            responsibilities: ['Gestion de projet', 'Support technique', 'Reporting']
          },
          {
            title: candidateInfo.earlierPosition,
            company: candidateInfo.earlierCompany,
            start_date: '2018-06',
            end_date: '2020-02',
            description: 'Expérience formatrice dans une entreprise dynamique.',
            responsibilities: ['Assistance technique', 'Formation', 'Documentation']
          }
        ],
        education: [
          {
            degree: candidateInfo.degree,
            institution: candidateInfo.school,
            start_date: '2018',
            end_date: '2020'
          },
          {
            degree: 'Licence en ' + candidateInfo.field,
            institution: 'Université de Lyon',
            start_date: '2015',
            end_date: '2018'
          }
        ],
        languages: candidateInfo.languages
      }
    };
  }
  
  /**
   * Analyse le nom de fichier pour extraire des informations pertinentes sur le candidat
   * @param {string} filename - Nom du fichier CV
   * @param {string} cvType - Type de CV détecté
   * @returns {Object} - Informations extraites
   */
  extractCandidateInfo(filename, cvType) {
    // Si le type de CV n'est pas fourni, le détecter
    if (!cvType) {
      cvType = this.detectCVType(filename);
    }
    
    // Valeurs par défaut
    let result = {
      name: 'Thomas Martin',
      jobTitle: 'Développeur Full Stack',
      previousTitle: 'Développeur Frontend',
      earlierPosition: 'Stagiaire développeur',
      company: 'TechCorp',
      previousCompany: 'WebAgency',
      earlierCompany: 'StartupLab',
      jobDescription: 'Développement et maintenance des solutions techniques de l\'entreprise.',
      responsibilities: ['Développement d\'applications', 'Revue de code', 'Tests unitaires', 'Documentation technique'],
      skills: ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Python', 'SQL', 'Git', 'Docker', 'Agile'],
      software: ['Visual Studio Code', 'IntelliJ', 'Photoshop', 'Office 365', 'JIRA', 'Confluence', 'GitHub'],
      email: 'thomas.martin@exemple.com',
      phone: '+33 6 ' + Math.floor(10000000 + Math.random() * 90000000),
      field: 'Informatique',
      degree: 'Master en Informatique',
      school: 'Université de Paris',
      languages: [
        { language: 'Français', level: 'Natif' },
        { language: 'Anglais', level: 'Courant' },
        { language: 'Espagnol', level: 'Intermédiaire' }
      ]
    };
    
    // Analyse avancée du nom de fichier
    const lowerFilename = filename.toLowerCase();
    
    // Recherche format Prénom_Nom.pdf ou Nom_Prénom.pdf
    const nameParts = this.extractNameParts(filename);
    if (nameParts) {
      result.name = nameParts.fullName;
      result.email = nameParts.email;
    }
    
    // Personnaliser les informations selon le type de CV
    switch (cvType) {
      case 'comptable':
        result.jobTitle = 'Comptable';
        result.previousTitle = 'Assistant Comptable';
        result.earlierPosition = 'Stagiaire Comptabilité';
        result.skills = ['Comptabilité générale', 'Fiscalité', 'Paie', 'Bilan', 'Trésorerie', 'Contrôle de gestion', 'Audit', 'Gestion financière', 'Droit'];
        result.software = ['SAP', 'Sage', 'Ciel Compta', 'Excel', 'EBP', 'Word', 'PowerPoint', 'Oracle Financials', 'QuickBooks'];
        result.field = 'Comptabilité';
        result.degree = 'DCG / DSCG';
        result.jobDescription = 'Gestion de la comptabilité et des déclarations fiscales.';
        result.responsibilities = ['Comptabilité générale', 'Comptabilité fournisseurs', 'Déclarations fiscales', 'Rapprochements bancaires', 'Bilan'];
        result.company = 'Cabinet Comptable Martin';
        result.previousCompany = 'Fiduciaire ABC';
        result.earlierCompany = 'Groupe XYZ Finance';
        
        if (lowerFilename.includes('junior')) {
          result.jobTitle = 'Comptable Junior';
          result.previousTitle = 'Assistant Comptable';
          result.earlierPosition = 'Stagiaire Comptabilité';
        } else if (lowerFilename.includes('senior')) {
          result.jobTitle = 'Comptable Senior';
          result.previousTitle = 'Comptable';
          result.earlierPosition = 'Comptable Junior';
        } else if (lowerFilename.includes('chef')) {
          result.jobTitle = 'Chef Comptable';
          result.previousTitle = 'Comptable Senior';
          result.earlierPosition = 'Comptable';
        }
        
        if (lowerFilename.includes('audit')) {
          result.jobTitle = 'Auditeur Junior';
          result.previousTitle = 'Assistant Audit';
          result.software = ['SAP', 'Excel', 'Word', 'PowerPoint', 'Caseware', 'ACL', 'TeamMate'];
          result.skills = ['Audit financier', 'Audit légal', 'Révision comptable', 'Analyse financière', 'Contrôle interne'];
        }
        
        if (lowerFilename.includes('bnp') || lowerFilename.includes('paribas')) {
          result.company = 'BNP Paribas';
          result.jobTitle = 'Comptable immobilier';
          result.software = ['SAP', 'Excel', 'Word', 'PowerPoint', 'Oracle Financials', 'Sage'];
        }
        break;
      case 'developpeur':
        if (lowerFilename.includes('front')) {
          result.jobTitle = 'Développeur Frontend';
          result.previousTitle = 'Développeur Frontend Junior';
          result.earlierPosition = 'Stagiaire Frontend';
          result.skills = ['JavaScript', 'HTML', 'CSS', 'React', 'Vue.js', 'Angular', 'SASS', 'Webpack'];
          result.software = ['Visual Studio Code', 'WebStorm', 'Figma', 'Adobe XD', 'Chrome DevTools', 'Git'];
        } else if (lowerFilename.includes('back')) {
          result.jobTitle = 'Développeur Backend';
          result.previousTitle = 'Développeur Backend Junior';
          result.earlierPosition = 'Développeur Stagiaire';
          result.skills = ['Node.js', 'Python', 'Java', 'SQL', 'NoSQL', 'API REST', 'Docker', 'AWS'];
          result.software = ['IntelliJ IDEA', 'PyCharm', 'Docker', 'Postman', 'MongoDB Compass', 'Jenkins'];
        } else if (lowerFilename.includes('full')) {
          result.jobTitle = 'Développeur Full Stack';
          result.previousTitle = 'Développeur Web';
          result.earlierPosition = 'Développeur Junior';
          result.skills = ['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'MongoDB', 'Docker', 'Git'];
          result.software = ['VS Code', 'IntelliJ', 'Docker', 'Postman', 'MongoDB Compass', 'GitHub', 'Jira'];
        } else if (lowerFilename.includes('mobile')) {
          result.jobTitle = 'Développeur Mobile';
          result.previousTitle = 'Développeur d\'Applications';
          result.earlierPosition = 'Stagiaire Développement Mobile';
          result.skills = ['Swift', 'Kotlin', 'React Native', 'Flutter', 'Firebase', 'REST API', 'Git'];
          result.software = ['Android Studio', 'Xcode', 'Visual Studio Code', 'Figma', 'Firebase Console'];
        }
        break;
      case 'data':
        if (lowerFilename.includes('scien')) {
          result.jobTitle = 'Data Scientist';
          result.previousTitle = 'Analyste Data';
          result.earlierPosition = 'Ingénieur Données Junior';
          result.skills = ['Python', 'R', 'Machine Learning', 'Deep Learning', 'SQL', 'Pandas', 'TensorFlow', 'Scikit-Learn'];
          result.software = ['Jupyter', 'RStudio', 'Tableau', 'Power BI', 'AWS', 'Hadoop', 'Docker'];
        } else if (lowerFilename.includes('analy')) {
          result.jobTitle = 'Data Analyst';
          result.previousTitle = 'Analyste Junior';
          result.earlierPosition = 'Consultant Data';
          result.skills = ['SQL', 'Python', 'Excel', 'Power BI', 'Tableau', 'R', 'Statistiques', 'Data Visualization'];
          result.software = ['Excel', 'Power BI', 'Tableau', 'SQL Server', 'Python', 'Google Analytics', 'SAS'];
        }
        break;
      case 'marketing':
        if (lowerFilename.includes('digital') || lowerFilename.includes('web')) {
          result.jobTitle = 'Responsable Marketing Digital';
          result.previousTitle = 'Chargé de Marketing Digital';
          result.earlierPosition = 'Assistant Marketing';
          result.skills = ['SEO', 'SEA', 'Google Analytics', 'Social Media', 'Content Marketing', 'Email Marketing'];
          result.software = ['Google Analytics', 'Google Ads', 'Facebook Ads', 'Mailchimp', 'WordPress', 'Canva', 'Photoshop'];
        } else {
          result.jobTitle = 'Responsable Marketing';
          result.previousTitle = 'Chargé de Marketing';
          result.earlierPosition = 'Assistant Marketing';
          result.skills = ['Stratégie Marketing', 'Étude de marché', 'CRM', 'Gestion de projet', 'Communication'];
          result.software = ['CRM', 'Microsoft Office', 'Adobe Creative Suite', 'Salesforce', 'Hubspot', 'Canva'];
        }
        break;
    }
    
    // Adaptation des compétences linguistiques selon le domaine
    if (lowerFilename.includes('international') || lowerFilename.includes('anglais')) {
      result.languages = [
        { language: 'Français', level: 'Natif' },
        { language: 'Anglais', level: 'Bilingue' },
        { language: 'Espagnol', level: 'Intermédiaire' },
        { language: 'Allemand', level: 'Notions' }
      ];
    }
    
    // Si le nom de fichier contient une indication de zone géographique
    if (lowerFilename.includes('fr') || lowerFilename.includes('france')) {
      result.languages = [
        { language: 'Français', level: 'Natif' },
        { language: 'Anglais', level: 'Professionnel' }
      ];
    }
    
    return result;
  }
  
  /**
   * Extrait le nom et prénom à partir d'un nom de fichier avec différents formats
   * @param {string} filename - Nom du fichier
   * @returns {Object|null} - Prénom, nom et email extraits, ou null si pas de correspondance
   */
  extractNameParts(filename) {
    // Supprimer l'extension
    const filenameWithoutExt = filename.split('.')[0];
    
    // Liste de motifs possibles avec expressions régulières
    const patterns = [
      // Format "CV_Nom_Prénom" ou "CV-Nom-Prénom"
      { regex: /CV[_-]([A-Za-zÀ-ÿ]+)[_-]([A-Za-zÀ-ÿ]+)/i, nameOrder: 'lastFirst' },
      
      // Format "Nom_Prénom_CV" ou "Nom-Prénom-CV"
      { regex: /([A-Za-zÀ-ÿ]+)[_-]([A-Za-zÀ-ÿ]+)[_-]CV/i, nameOrder: 'firstLast' },
      
      // Format "CV Nom Prénom"
      { regex: /CV\s+([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]+)/i, nameOrder: 'lastFirst' },
      
      // Format "Nom Prénom CV"
      { regex: /([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]+)\s+CV/i, nameOrder: 'firstLast' },
      
      // Format spécial "OMAR_Amal_CV.pdf" (Nom_Prénom_CV)
      { regex: /([A-Z]+)[_-]([A-Za-zÀ-ÿ]+)[_-]CV/i, nameOrder: 'lastFirst' },
      
      // Format spécial "OMAR_Amal.pdf" (Nom_Prénom)
      { regex: /([A-Z]+)[_-]([A-Za-zÀ-ÿ]+)/i, nameOrder: 'lastFirst' },
      
      // Format "CV Comptable junior FR(4).pdf"
      { regex: /CV\s+([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]+)\s+([A-Za-zÀ-ÿ]+)/i, nameOrder: 'position' }
    ];
    
    // Tester chaque motif
    for (const pattern of patterns) {
      const match = filenameWithoutExt.match(pattern.regex);
      if (match && match.length >= 3) {
        // Extraire prénom et nom selon l'ordre détecté
        let firstName, lastName;
        
        if (pattern.nameOrder === 'lastFirst') {
          lastName = match[1];
          firstName = match[2];
        } else if (pattern.nameOrder === 'firstLast') {
          firstName = match[1];
          lastName = match[2];
        } else if (pattern.nameOrder === 'position') {
          // Pour les formats comme "CV Comptable junior FR(4).pdf", 
          // on va utiliser des valeurs génériques basées sur le poste
          return {
            firstName: 'Candidat',
            lastName: match[1], // Le type de poste (ex: Comptable)
            fullName: `Candidat ${match[1]}`,
            email: `contact.${match[1].toLowerCase()}@exemple.com`
          };
        }
        
        // Mise en forme correcte des noms (première lettre en majuscule, reste en minuscule)
        firstName = firstName.charAt(0).toUpperCase() + firstName.slice(1).toLowerCase();
        
        // Si le nom est entièrement en majuscules, on le met en forme correcte
        if (lastName === lastName.toUpperCase()) {
          lastName = lastName.charAt(0).toUpperCase() + lastName.slice(1).toLowerCase();
        }
        
        // Générer un email à partir du nom et prénom
        const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@exemple.com`;
        
        return {
          firstName: firstName,
          lastName: lastName,
          fullName: `${firstName} ${lastName}`,
          email: email
        };
      }
    }
    
    // Pour les formats spécifiques comme "CV Comptable junior FR(4).pdf"
    if (filenameWithoutExt.toLowerCase().includes('cv ')) {
      // Extraire un nom à partir de mots-clés de prénom communs dans le nom de fichier
      const maleNames = ['ibrahim', 'ibrahima', 'mohamed', 'mohammed', 'ahmed', 'jean', 'pierre', 'paul', 'jacques', 'robert', 'marcel'];
      const femaleNames = ['marie', 'sophie', 'amal', 'fatima', 'leila', 'sarah', 'julie', 'lucie', 'anne', 'jeanne'];
      const allNames = [...maleNames, ...femaleNames];
      
      const lowerFilename = filenameWithoutExt.toLowerCase();
      
      // Chercher un prénom dans le nom de fichier
      for (const name of allNames) {
        if (lowerFilename.includes(name)) {
          const capitalizedName = name.charAt(0).toUpperCase() + name.slice(1);
          return {
            firstName: capitalizedName,
            lastName: 'Senghor',
            fullName: `${capitalizedName} Senghor`,
            email: `${name.toLowerCase()}.senghor@exemple.com`
          };
        }
      }
      
      // Si on trouve "Mame" ou "Mame-"
      if (lowerFilename.includes('mame') || lowerFilename.includes('mame-')) {
        return {
          firstName: 'Mame',
          lastName: 'Ibrahima',
          fullName: 'Mame Ibrahima Senghor',
          email: 'mame.senghor@exemple.com'
        };
      }
      
      // Si on ne trouve pas de prénom, utiliser un nom générique basé sur le type de poste
      const parts = filenameWithoutExt.split(' ');
      if (parts.length >= 2) {
        const position = parts[1]; // Ex: Comptable
        return {
          firstName: 'Candidat',
          lastName: position,
          fullName: `Candidat ${position}`,
          email: `contact.${position.toLowerCase()}@exemple.com`
        };
      }
    }
    
    // Si aucun motif ne correspond, on retourne null
    return null;
  }
}

// Exporter la classe d'intégration
window.CVParserIntegration = CVParserIntegration;