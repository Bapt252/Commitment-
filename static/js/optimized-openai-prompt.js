/**
 * Prompt OpenAI Optimisé pour Commitment
 * Améliore drastiquement la précision d'extraction avec l'API OpenAI
 * Prompts intelligents selon le type de CV détecté
 */

class CommitmentOptimizedPrompt {
    /**
     * Génère un prompt optimisé pour l'extraction de CV dans Commitment
     */
    static buildOptimizedPrompt(content) {
        return `Tu es un expert en analyse de CV travaillant pour la plateforme Commitment. Analyse ce CV avec une précision maximale et extrait UNIQUEMENT les informations présentes dans le texte.

INSTRUCTIONS CRITIQUES COMMITMENT :
- Extrait SEULEMENT les informations explicitement mentionnées dans le CV
- Pour les dates, utilise EXACTEMENT le format trouvé (MM/YYYY ou YYYY)
- Pour les niveaux de langue, identifie précisément les niveaux mentionnés (A1, A2, B1, B2, C1, C2, natif, courant, etc.)
- Ne fais AUCUNE supposition ou invention
- Si une information n'est pas claire, marque-la comme "À compléter"
- Priorité à l'exactitude sur la complétude

FORMAT JSON COMMITMENT (respecte exactement cette structure) :

{
  "personal_info": {
    "name": "nom complet exact tel qu'écrit",
    "email": "adresse email exacte",
    "phone": "numéro de téléphone exact avec format original",
    "location": "ville/région si mentionnée explicitement"
  },
  "current_position": "titre exact du poste actuel ou plus récent",
  "skills": [
    "compétence1 exacte telle qu'écrite",
    "compétence2 exacte telle qu'écrite"
  ],
  "software": [
    "logiciel1 exact tel qu'écrit",
    "logiciel2 exact tel qu'écrit"
  ],
  "languages": [
    {
      "language": "nom de langue exact",
      "level": "niveau exact mentionné (A1, B1, C1, Natif, Courant, etc.)"
    }
  ],
  "work_experience": [
    {
      "title": "titre exact du poste tel qu'écrit",
      "company": "nom exact de l'entreprise tel qu'écrit",
      "location": "lieu si mentionné",
      "start_date": "date de début exacte (MM/YYYY)",
      "end_date": "date de fin exacte (MM/YYYY ou Present)",
      "duration": "durée si calculable",
      "key_responsibilities": [
        "responsabilité1 exacte",
        "responsabilité2 exacte"
      ]
    }
  ],
  "education": [
    {
      "degree": "diplôme exact tel qu'écrit",
      "institution": "établissement exact tel qu'écrit",
      "location": "lieu si mentionné",
      "year": "année exacte (YYYY)",
      "field": "domaine d'études si mentionné"
    }
  ],
  "certifications": [
    {
      "name": "nom exact de la certification",
      "issuer": "organisme délivrant si mentionné",
      "year": "année si mentionnée"
    }
  ]
}

EXEMPLES DE BONNES EXTRACTIONS COMMITMENT :

✅ Pour "Executive Assistant" → "Executive Assistant"
✅ Pour "06/2024 - 01/2025" → start_date: "06/2024", end_date: "01/2025"
✅ Pour "French - A1" → {"language": "Français", "level": "A1"}
✅ Pour "Maison Christian Dior Couture" → "Maison Christian Dior Couture"
✅ Pour "SAP, Excel, Pennylane" → ["SAP", "Excel", "Pennylane"]

RÈGLES SPÉCIFIQUES COMMITMENT :

1. DATES : Garde le format exact (MM/YYYY). Si "présent", "actuel", "current" → "Present"
2. LANGUES : Identifie précisément A1/A2/B1/B2/C1/C2, Natif, Courant, Intermédiaire
3. COMPÉTENCES : Sépare compétences techniques des compétences métier/soft skills
4. ENTREPRISES : Nom exact sans modification ni abréviation
5. FORMATIONS : Inclus année, diplôme et établissement exacts
6. LOGICIELS : Nom exact des logiciels et outils mentionnés

ATTENTION AUX PIÈGES COMMITMENT :
- Ne confonds pas titre du poste et nom d'entreprise
- Les dates peuvent être dans différents formats (MM/YYYY, YYYY, MM/YY)
- Les niveaux de langue peuvent être mal orthographiés
- Certains logiciels peuvent être abrégés (ex: "MS Office" = "Microsoft Office")
- Vérifie les sections "Informatique", "Logiciels", "Outils"

CV À ANALYSER POUR COMMITMENT :
${content}

Réponds UNIQUEMENT avec le JSON valide, sans aucune autre explication.`;
    }

    /**
     * Prompt spécialisé pour les CVs techniques
     */
    static buildTechnicalPrompt(content) {
        return `Tu es un expert technique en recrutement IT pour Commitment. Ce CV contient probablement des compétences techniques spécialisées.

FOCUS TECHNIQUE COMMITMENT :
- Identifie précisément les langages de programmation (JavaScript, Python, Java, etc.)
- Repère les frameworks et bibliothèques (React, Angular, Vue.js, Django, etc.)
- Détecte les outils DevOps et cloud (Docker, Kubernetes, AWS, Azure, etc.)
- Extrais les méthodologies (Agile, Scrum, DevOps, etc.)
- Identifie les bases de données et systèmes (MySQL, PostgreSQL, MongoDB, etc.)

TECHNOLOGIES À RECHERCHER PRIORITAIREMENT :
- Langages : JavaScript, Python, Java, C#, PHP, Ruby, Go, Rust, Swift, Kotlin
- Frontend : React, Angular, Vue.js, Svelte, Next.js, Nuxt.js, HTML, CSS
- Backend : Node.js, Express, Django, Flask, Spring, .NET, API REST
- Mobile : React Native, Flutter, Ionic, Xamarin
- Cloud : AWS, Azure, GCP, Docker, Kubernetes, Terraform
- Databases : MySQL, PostgreSQL, MongoDB, Redis, Elasticsearch
- DevOps : Jenkins, GitLab CI, Docker, Terraform, Ansible, Git

${this.buildOptimizedPrompt(content)}`;
    }

    /**
     * Prompt spécialisé pour les CVs business/management
     */
    static buildBusinessPrompt(content) {
        return `Tu es un expert en recrutement business et management pour Commitment. Ce CV contient probablement des compétences managériales et business.

FOCUS BUSINESS COMMITMENT :
- Identifie les compétences en leadership et management d'équipe
- Repère les outils business (CRM, ERP, outils de gestion, etc.)
- Détecte les certifications professionnelles (PMP, Prince2, etc.)
- Extrais les réalisations quantifiées (budgets gérés, taille équipes, etc.)
- Identifie les secteurs d'activité et domaines d'expertise

COMPÉTENCES BUSINESS À RECHERCHER PRIORITAIREMENT :
- Management : Leadership, Gestion d'équipe, Coaching, Formation, Recrutement
- Commercial : Vente, Négociation, Prospection, Relation client, CRM
- Finance : Budgets, Comptabilité, Contrôle de gestion, Analyse financière
- Marketing : Stratégie marketing, Marketing digital, Communication, Analytics
- Project Management : Gestion de projet, Agile, Scrum, PMP, Prince2
- Outils : Salesforce, HubSpot, Tableau, Power BI, SAP, Oracle, Excel avancé
- Assistant : Secrétariat, Organisation, Planning, Coordination, Support exécutif

${this.buildOptimizedPrompt(content)}`;
    }

    /**
     * Prompt spécialisé pour les CVs Executive Assistant (comme Sabine)
     */
    static buildExecutiveAssistantPrompt(content) {
        return `Tu es un expert en recrutement d'Executive Assistant pour Commitment. Ce CV concerne un poste d'assistant de direction.

FOCUS EXECUTIVE ASSISTANT COMMITMENT :
- Identifie les compétences en assistance de direction et support exécutif
- Repère les outils de bureautique et de gestion (Microsoft Office, SAP, etc.)
- Détecte les compétences en organisation et planification
- Extrais l'expérience avec les COMEX, CODIR, direction générale
- Identifie les compétences linguistiques pour communication internationale

COMPÉTENCES EXECUTIVE ASSISTANT À RECHERCHER :
- Organisation : Tenue d'agendas, Gestion planning, Organisation déplacements
- Communication : Rédaction, Coordination, Interface direction/équipes
- Gestion : Suivi budgétaire, Notes de frais, Préparation rapports
- Outils : Microsoft Office, Outlook, SAP, Concur, Pennylane, Coupa
- Qualités : Autonomie, Discrétion, Rigueur, Sens communication, Proactivité
- Événementiel : Organisation séminaires, team building, réunions

${this.buildOptimizedPrompt(content)}`;
    }

    /**
     * Détermine le type de CV et choisit le prompt approprié
     */
    static getOptimalPrompt(content) {
        const lowerContent = content.toLowerCase();
        
        // Mots-clés techniques
        const techKeywords = [
            'javascript', 'python', 'java', 'react', 'angular', 'node.js', 'php',
            'developer', 'développeur', 'engineer', 'ingénieur', 'programmer',
            'full stack', 'frontend', 'backend', 'devops', 'cloud', 'api', 'sql'
        ];
        
        // Mots-clés business/management
        const businessKeywords = [
            'manager', 'director', 'chef', 'responsable', 'directeur',
            'sales', 'marketing', 'finance', 'accounting', 'project manager',
            'business', 'commercial', 'vente', 'gestion', 'management'
        ];
        
        // Mots-clés Executive Assistant
        const assistantKeywords = [
            'assistant', 'executive assistant', 'assistante', 'secrétaire',
            'support', 'coordination', 'agenda', 'planning', 'organisation'
        ];
        
        const techScore = techKeywords.reduce((score, keyword) => 
            score + (lowerContent.includes(keyword) ? 1 : 0), 0
        );
        
        const businessScore = businessKeywords.reduce((score, keyword) => 
            score + (lowerContent.includes(keyword) ? 1 : 0), 0
        );
        
        const assistantScore = assistantKeywords.reduce((score, keyword) => 
            score + (lowerContent.includes(keyword) ? 1 : 0), 0
        );
        
        console.log(`🎯 Analyse type CV Commitment: Tech=${techScore}, Business=${businessScore}, Assistant=${assistantScore}`);
        
        if (assistantScore >= 2 && lowerContent.includes('executive')) {
            console.log('👔 Utilisation du prompt Executive Assistant pour Commitment');
            return this.buildExecutiveAssistantPrompt(content);
        } else if (techScore > businessScore && techScore >= 2) {
            console.log('🔧 Utilisation du prompt technique pour Commitment');
            return this.buildTechnicalPrompt(content);
        } else if (businessScore >= 2) {
            console.log('💼 Utilisation du prompt business pour Commitment');
            return this.buildBusinessPrompt(content);
        } else {
            console.log('📄 Utilisation du prompt généraliste pour Commitment');
            return this.buildOptimizedPrompt(content);
        }
    }

    /**
     * Post-traitement des résultats OpenAI pour Commitment
     */
    static postProcessOpenAIResult(aiResponse) {
        try {
            // Nettoyer la réponse
            let cleanResponse = aiResponse.trim();
            
            // Supprimer les balises markdown
            cleanResponse = cleanResponse.replace(/```json\n?/g, '').replace(/```\n?/g, '');
            
            // Parser le JSON
            const parsed = JSON.parse(cleanResponse);
            
            // Validation et nettoyage spécifique à Commitment
            const cleaned = this.validateAndCleanCommitmentData(parsed);
            
            return {
                data: cleaned,
                source: 'commitment_optimized_openai',
                timestamp: new Date().toISOString(),
                quality_score: this.calculateCommitmentQualityScore(cleaned),
                platform: 'commitment'
            };
            
        } catch (error) {
            console.error('❌ Erreur post-traitement OpenAI Commitment:', error);
            throw new Error(`Erreur parsing réponse OpenAI: ${error.message}`);
        }
    }

    /**
     * Valide et nettoie les données extraites pour Commitment
     */
    static validateAndCleanCommitmentData(data) {
        const cleaned = { ...data };
        
        // Nettoyer les informations personnelles
        if (cleaned.personal_info) {
            cleaned.personal_info.name = this.cleanString(cleaned.personal_info.name);
            cleaned.personal_info.email = this.cleanEmail(cleaned.personal_info.email);
            cleaned.personal_info.phone = this.cleanPhone(cleaned.personal_info.phone);
        }
        
        // Nettoyer les expériences avec validation spécifique Commitment
        if (cleaned.work_experience && Array.isArray(cleaned.work_experience)) {
            cleaned.work_experience = cleaned.work_experience
                .filter(exp => exp.title && exp.title !== 'À compléter')
                .map(exp => ({
                    ...exp,
                    title: this.cleanString(exp.title),
                    company: this.cleanString(exp.company),
                    start_date: this.formatCommitmentDate(exp.start_date),
                    end_date: this.formatCommitmentDate(exp.end_date)
                }));
        }
        
        // Nettoyer les compétences avec priorité business pour Commitment
        if (cleaned.skills && Array.isArray(cleaned.skills)) {
            cleaned.skills = cleaned.skills
                .filter(skill => skill && skill.length > 1)
                .map(skill => this.cleanString(skill))
                .slice(0, 15); // Limiter à 15 compétences pour éviter la surcharge
        }
        
        // Nettoyer les logiciels avec focus outils business
        if (cleaned.software && Array.isArray(cleaned.software)) {
            cleaned.software = cleaned.software
                .filter(software => software && software.length > 1)
                .map(software => this.cleanString(software))
                .slice(0, 10); // Limiter à 10 logiciels
        }
        
        // Nettoyer les langues avec normalisation
        if (cleaned.languages && Array.isArray(cleaned.languages)) {
            cleaned.languages = cleaned.languages
                .filter(lang => lang.language && lang.level)
                .map(lang => ({
                    language: this.cleanString(lang.language),
                    level: this.normalizeCommitmentLanguageLevel(lang.level)
                }));
        }
        
        return cleaned;
    }

    /**
     * Nettoie une chaîne de caractères
     */
    static cleanString(str) {
        if (!str) return 'À compléter';
        return str.trim().replace(/\s+/g, ' ');
    }

    /**
     * Nettoie un email
     */
    static cleanEmail(email) {
        if (!email || !email.includes('@')) return 'À compléter';
        return email.toLowerCase().trim();
    }

    /**
     * Nettoie un numéro de téléphone
     */
    static cleanPhone(phone) {
        if (!phone) return 'À compléter';
        // Garder le format original pour Commitment
        return phone.trim();
    }

    /**
     * Formate une date pour Commitment
     */
    static formatCommitmentDate(date) {
        if (!date) return 'À définir';
        if (date.toLowerCase().includes('present') || 
            date.toLowerCase().includes('actuel') ||
            date.toLowerCase().includes('current')) {
            return 'Present';
        }
        return date;
    }

    /**
     * Normalise les niveaux de langue pour Commitment
     */
    static normalizeCommitmentLanguageLevel(level) {
        if (!level) return 'À évaluer';
        
        const levelMap = {
            'a1': 'A1 - Débutant',
            'a2': 'A2 - Élémentaire', 
            'b1': 'B1 - Intermédiaire',
            'b2': 'B2 - Avancé',
            'c1': 'C1 - Autonome',
            'c2': 'C2 - Maîtrise',
            'natif': 'Natif',
            'native': 'Natif',
            'courant': 'Courant',
            'fluent': 'Courant'
        };
        
        const normalizedLevel = level.toLowerCase().trim();
        return levelMap[normalizedLevel] || level;
    }

    /**
     * Calcule un score de qualité pour Commitment
     */
    static calculateCommitmentQualityScore(data) {
        let score = 0;
        let maxScore = 0;
        
        // Informations personnelles (25 points)
        maxScore += 25;
        if (data.personal_info?.name !== 'À compléter') score += 10;
        if (data.personal_info?.email !== 'À compléter') score += 8;
        if (data.personal_info?.phone !== 'À compléter') score += 7;
        
        // Expérience (35 points - priorité Commitment)
        maxScore += 35;
        if (data.work_experience?.length > 0) {
            score += 20;
            const validExperiences = data.work_experience.filter(exp => 
                exp.start_date !== 'À définir' && exp.end_date !== 'À définir'
            );
            score += (validExperiences.length / data.work_experience.length) * 15;
        }
        
        // Compétences (20 points)
        maxScore += 20;
        if (data.skills?.length > 0) score += Math.min(data.skills.length * 2, 20);
        
        // Langues (10 points)
        maxScore += 10;
        if (data.languages?.length > 0) {
            score += 5;
            const validLevels = data.languages.filter(lang => lang.level !== 'À évaluer');
            score += (validLevels.length / data.languages.length) * 5;
        }
        
        // Formation (10 points)
        maxScore += 10;
        if (data.education?.length > 0) score += Math.min(data.education.length * 5, 10);
        
        return Math.round((score / maxScore) * 100);
    }
}

// Fonction d'intégration dans le système Commitment existant
function integrateCommitmentOptimizedPrompt() {
    if (typeof window.GPTParserClient !== 'undefined') {
        const OriginalGPTParserClient = window.GPTParserClient;
        
        class CommitmentOptimizedGPTParserClient extends OriginalGPTParserClient {
            /**
             * Version optimisée de l'analyse OpenAI pour Commitment
             */
            async analyzeWithOpenAI(content) {
                const prompt = CommitmentOptimizedPrompt.getOptimalPrompt(content);
                
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
                                    content: 'Tu es un expert en analyse de CV pour la plateforme Commitment. Extrait uniquement les informations présentes et réponds en JSON valide.'
                                },
                                {
                                    role: 'user',
                                    content: prompt
                                }
                            ],
                            temperature: 0.1,
                            max_tokens: 2500
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`Erreur API OpenAI Commitment: ${response.status}`);
                    }

                    const data = await response.json();
                    const aiResponse = data.choices[0].message.content;
                    
                    return CommitmentOptimizedPrompt.postProcessOpenAIResult(aiResponse);

                } catch (error) {
                    console.error('Erreur OpenAI optimisé Commitment:', error);
                    throw error;
                }
            }
        }
        
        window.GPTParserClient = CommitmentOptimizedGPTParserClient;
        console.log('✅ Prompt OpenAI optimisé Commitment intégré');
    }
}

// Export pour utilisation
if (typeof window !== 'undefined') {
    window.CommitmentOptimizedPrompt = CommitmentOptimizedPrompt;
    window.integrateCommitmentOptimizedPrompt = integrateCommitmentOptimizedPrompt;
    
    // Intégration automatique
    integrateCommitmentOptimizedPrompt();
}

console.log('✅ Prompt OpenAI optimisé Commitment chargé !');
