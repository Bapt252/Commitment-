/**
 * Service mock amélioré pour analyser les fiches de poste
 * Analyse réellement le contenu pour produire des résultats plus fidèles
 */

// Délai simulé pour imiter un appel API (en ms)
const MOCK_DELAY = 800;

/**
 * Analyse le texte pour extraire les informations pertinentes
 * @param {String} text - Texte de la fiche de poste
 * @returns {Object} - Informations structurées extraites
 */
const analyzeJobText = (text) => {
  // Convertir le texte en minuscules pour faciliter la recherche
  const lowerText = text.toLowerCase();
  
  // Extraire le titre du poste
  let title = "";
  const titlePatterns = [
    /développeur\s+front\s*[\-]?[\s]?end/i,
    /ingénieur\s+dev\s*ops/i,
    /data\s+scientist/i,
    /développeur\s+full\s*[\-]?[\s]?stack/i,
    /développeur\s+back\s*[\-]?[\s]?end/i,
    /développeur\s+web/i,
    /architecte\s+logiciel/i
  ];
  
  for (const pattern of titlePatterns) {
    const match = text.match(pattern);
    if (match) {
      title = match[0].charAt(0).toUpperCase() + match[0].slice(1);
      break;
    }
  }
  
  // Si aucun titre n'est détecté, essayer d'extraire les premiers mots du texte
  if (!title) {
    const firstLine = text.split('\n')[0].trim();
    title = firstLine.length > 5 ? firstLine : "Développeur";
  }
  
  // Détecter le type de contrat
  let contractType = "";
  if (lowerText.includes("cdi")) {
    contractType = "CDI";
  } else if (lowerText.includes("cdd")) {
    contractType = "CDD";
  } else if (lowerText.includes("freelance") || lowerText.includes("indépendant")) {
    contractType = "Freelance";
  } else if (lowerText.includes("stage")) {
    contractType = "Stage";
  } else if (lowerText.includes("alternance") || lowerText.includes("apprentissage")) {
    contractType = "Alternance";
  } else {
    contractType = "Non spécifié";
  }
  
  // Détecter l'expérience requise
  let experience = "";
  const expMatches = [
    lowerText.match(/(\d+)\s*[\-à]\s*(\d+)\s*ans?\s+d['']expérience/i),
    lowerText.match(/(\d+)\s+ans?\s+d['']expérience/i),
    lowerText.match(/expérience\s+de\s+(\d+)\s+ans/i),
    lowerText.match(/expérimenté/i)
  ].filter(Boolean);
  
  if (expMatches.length > 0) {
    const match = expMatches[0];
    if (match[2]) { // Range like "3-5 ans"
      experience = `${match[1]}-${match[2]} ans d'expérience`;
    } else if (match[1]) { // Single value like "5 ans"
      experience = `${match[1]} ans d'expérience`;
    } else { // Just "expérimenté"
      experience = "Développeur expérimenté";
    }
  } else if (lowerText.includes("junior")) {
    experience = "Profil junior";
  } else if (lowerText.includes("senior")) {
    experience = "Profil senior";
  } else if (lowerText.includes("confirmé")) {
    experience = "Profil confirmé";
  } else {
    experience = "Non spécifié";
  }
  
  // Détecter les compétences requises
  const skillKeywords = {
    // Frontend
    frontend: ["html", "css", "javascript", "js", "typescript", "ts", "react", "angular", "vue", "svelte", "jquery", "bootstrap", "tailwind", "sass", "less", "webpack", "vite", "responsive", "figma", "sketch", "adobe xd", "redux"],
    // Backend
    backend: ["node", "express", "django", "flask", "spring", "java", "php", "laravel", "symfony", "ruby", "rails", "python", "go", "golang", "rest", "graphql", "api", "sql", "mysql", "postgresql", "mongodb", "nosql", "orm", "microservices"],
    // DevOps
    devops: ["docker", "kubernetes", "k8s", "aws", "azure", "gcp", "ci/cd", "jenkins", "gitlab", "github actions", "terraform", "ansible", "linux", "unix", "bash", "shell", "nginx", "apache", "monitoring", "prometheus", "grafana"],
    // Data
    data: ["python", "r", "sql", "nosql", "hadoop", "spark", "machine learning", "ml", "ai", "tensorflow", "pytorch", "pandas", "numpy", "etl", "data mining", "statistics", "mathématiques", "big data", "power bi", "tableau"],
    // General
    general: ["git", "agile", "scrum", "jira", "confluence", "kanban", "tdd", "bdd", "clean code", "design patterns", "architecture", "sécurité", "testing", "jest", "mocha", "cypress"]
  };
  
  // Identifier les compétences présentes dans le texte
  const detectedSkills = {};
  Object.entries(skillKeywords).forEach(([category, skills]) => {
    detectedSkills[category] = skills.filter(skill => 
      lowerText.includes(skill.toLowerCase())
    );
  });
  
  // Rassembler toutes les compétences détectées
  let allDetectedSkills = [];
  Object.values(detectedSkills).forEach(skills => {
    allDetectedSkills = [...allDetectedSkills, ...skills];
  });
  
  // Formater les compétences (première lettre en majuscule)
  const formattedSkills = allDetectedSkills.map(skill => 
    skill.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  );
  
  // Séparer en compétences requises et souhaitées
  // Les compétences mentionnées comme "souhaité", "apprécié", "un plus" vont dans preferred
  const requiredSkills = [];
  const preferredSkills = [];
  
  // Répartir les compétences entre requises et souhaitées
  formattedSkills.forEach(skill => {
    // Rechercher si la compétence est mentionnée avec des termes comme "souhaité", "apprécié", etc.
    const skillContext = findSkillContext(lowerText, skill.toLowerCase());
    
    if (skillContext.includes("souhaité") || 
        skillContext.includes("apprécié") || 
        skillContext.includes("plus") || 
        skillContext.includes("bonus")) {
      preferredSkills.push(skill);
    } else {
      requiredSkills.push(skill);
    }
  });
  
  // Détecter l'entreprise
  let company = "";
  const companyPatterns = [
    /notre (entreprise|société|structure|agence)/i,
    /(chez|pour)\s+([A-Z][a-zA-Z]+)/i
  ];
  
  for (const pattern of companyPatterns) {
    const match = text.match(pattern);
    if (match) {
      if (match[2]) {
        company = match[2];
      } else {
        company = "Entreprise non spécifiée";
      }
      break;
    }
  }
  
  // Détecter la localisation
  let location = "";
  const locationPatterns = [
    /(à|sur|en|au)\s+([A-Z][a-zA-Z]+(-[A-Z][a-zA-Z]+)?)/i,
    /basé\s+(à|en|au)\s+([A-Z][a-zA-Z]+(-[A-Z][a-zA-Z]+)?)/i,
    /(paris|lyon|marseille|toulouse|bordeaux|lille|nantes|strasbourg|montpellier|nice|france)/i
  ];
  
  for (const pattern of locationPatterns) {
    const match = text.match(pattern);
    if (match) {
      if (match[2]) {
        location = match[2];
      } else if (match[1]) {
        location = match[1].charAt(0).toUpperCase() + match[1].slice(1);
      }
      break;
    }
  }
  
  // Extraire responsabilités, avantages, etc. des paragraphes pertinents
  const responsibilities = extractListItems(text, ["responsabilités", "missions", "tâches", "rôle", "poste"]);
  const benefits = extractListItems(text, ["avantages", "offrons", "proposons", "package"]);
  
  // Construire le résultat
  return {
    title: title || "Développeur",
    company: company || "Nexten Technologies",
    location: location || "Paris",
    contract_type: contractType,
    required_skills: removeDuplicates(requiredSkills),
    preferred_skills: removeDuplicates(preferredSkills),
    responsibilities: responsibilities.length > 0 ? responsibilities : ["Développement d'applications"],
    requirements: [experience],
    benefits: benefits.length > 0 ? benefits : ["Environnement de travail agréable"],
    salary_range: extractSalaryRange(text),
    remote_policy: extractRemotePolicy(text),
    application_process: ""
  };
};

/**
 * Trouve le contexte d'une compétence dans le texte
 * @param {String} text - Texte complet
 * @param {String} skill - Compétence à chercher
 * @returns {String} - Contexte autour de la compétence
 */
const findSkillContext = (text, skill) => {
  const index = text.indexOf(skill);
  if (index === -1) return "";
  
  // Extraire 50 caractères avant et après la compétence
  const start = Math.max(0, index - 50);
  const end = Math.min(text.length, index + skill.length + 50);
  return text.substring(start, end);
};

/**
 * Extrait des éléments de liste à partir de sections identifiées par des mots-clés
 * @param {String} text - Texte complet
 * @param {Array} keywords - Mots-clés pour identifier les sections
 * @returns {Array} - Liste des éléments extraits
 */
const extractListItems = (text, keywords) => {
  const items = [];
  const paragraphs = text.split('\n').filter(p => p.trim() !== '');
  
  // Trouver les paragraphes contenant les mots-clés
  for (const paragraph of paragraphs) {
    const lowerPara = paragraph.toLowerCase();
    const containsKeyword = keywords.some(keyword => lowerPara.includes(keyword));
    
    if (containsKeyword) {
      // Essayer d'extraire des éléments de liste
      const listItems = paragraph.split(/[•\-\*\:,;]/).map(item => item.trim()).filter(item => item.length > 10);
      
      if (listItems.length > 1) {
        items.push(...listItems);
      } else if (paragraph.length > 20) {
        // Si ce n'est pas une liste, ajouter le paragraphe comme un tout
        items.push(paragraph);
      }
    }
  }
  
  // Limiter à 5 éléments maximum
  return items.slice(0, 5);
};

/**
 * Extrait la fourchette de salaire du texte
 * @param {String} text - Texte complet
 * @returns {String} - Fourchette de salaire extraite
 */
const extractSalaryRange = (text) => {
  const lowerText = text.toLowerCase();
  
  // Chercher des patterns comme "40-50K€" ou "entre 40K et 50K€"
  const patterns = [
    /(\d+)[\s\-à]+(\d+)\s*k€/i,
    /(\d+)\s*k€[\s\-à]+(\d+)\s*k€/i,
    /entre\s+(\d+)\s*k€?\s+et\s+(\d+)\s*k€/i,
    /salaire\s*:?\s*(\d+)[\s\-à]+(\d+)\s*k€/i,
    /rémunération\s*:?\s*(\d+)[\s\-à]+(\d+)\s*k€/i
  ];
  
  for (const pattern of patterns) {
    const match = lowerText.match(pattern);
    if (match && match[1] && match[2]) {
      return `${match[1]}K€ - ${match[2]}K€`;
    }
  }
  
  return "Selon expérience";
};

/**
 * Extrait la politique de télétravail du texte
 * @param {String} text - Texte complet
 * @returns {String} - Politique de télétravail extraite
 */
const extractRemotePolicy = (text) => {
  const lowerText = text.toLowerCase();
  
  if (lowerText.includes("100% télétravail") || lowerText.includes("full remote")) {
    return "100% télétravail";
  } else if (lowerText.includes("télétravail partiel") || lowerText.includes("hybrid")) {
    // Chercher le nombre de jours
    const daysMatch = lowerText.match(/(\d+)\s*jours?\s*(?:de)?\s*télétravail/i);
    if (daysMatch && daysMatch[1]) {
      return `Hybride (${daysMatch[1]}j télétravail/semaine)`;
    }
    return "Hybride";
  } else if (lowerText.includes("télétravail")) {
    return "Télétravail possible";
  } else if (lowerText.includes("présentiel") || lowerText.includes("sur site")) {
    return "Présentiel";
  }
  
  return "Non spécifié";
};

/**
 * Supprime les doublons d'un tableau
 * @param {Array} array - Tableau à nettoyer
 * @returns {Array} - Tableau sans doublons
 */
const removeDuplicates = (array) => {
  return [...new Set(array)];
};

/**
 * Génère un résultat de parsing basé sur l'analyse du texte
 * @param {String} filename - Nom du fichier (optionnel)
 * @param {String} text - Texte à analyser (optionnel)
 * @returns {Object} - Résultat structuré de l'analyse
 */
const generateMockResult = (filename = "", text = "") => {
  // Si le texte est fourni, l'analyser
  if (text) {
    const result = analyzeJobText(text);
    
    return {
      data: result,
      processing_time: Math.random() * 2 + 0.5, // Entre 0.5 et 2.5 secondes
      parsed_at: Date.now() / 1000,
      file_format: filename ? filename.split('.').pop() : "txt",
      model: "mock-gpt-improved"
    };
  }
  
  // Si le texte n'est pas fourni mais qu'un nom de fichier est présent,
  // générer un résultat basique basé sur les indices du nom de fichier
  if (filename) {
    const lowerFilename = filename.toLowerCase();
    let jobTitle = "Développeur";
    let skills = ["JavaScript", "React", "Node.js"];
    
    if (lowerFilename.includes("devops")) {
      jobTitle = "Ingénieur DevOps";
      skills = ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"];
    } else if (lowerFilename.includes("front")) {
      jobTitle = "Développeur Frontend";
      skills = ["HTML", "CSS", "JavaScript", "React"];
    } else if (lowerFilename.includes("back")) {
      jobTitle = "Développeur Backend";
      skills = ["Java", "Spring", "API REST", "SQL"];
    } else if (lowerFilename.includes("data")) {
      jobTitle = "Data Scientist";
      skills = ["Python", "R", "SQL", "Machine Learning"];
    }
    
    // Générer un résultat simplifié
    return {
      data: {
        title: jobTitle,
        company: "Entreprise",
        location: "Paris",
        contract_type: lowerFilename.includes("cdi") ? "CDI" : 
                      lowerFilename.includes("cdd") ? "CDD" : "Non spécifié",
        required_skills: skills,
        preferred_skills: ["Git", "Agile"],
        responsibilities: ["Développement d'applications"],
        requirements: ["3 ans d'expérience minimum"],
        benefits: ["Bonne ambiance de travail"],
        salary_range: "Selon expérience",
        remote_policy: "Non spécifié",
        application_process: ""
      },
      processing_time: Math.random() * 2 + 0.5,
      parsed_at: Date.now() / 1000,
      file_format: filename.split('.').pop(),
      model: "mock-gpt-basic"
    };
  }
  
  // Résultat par défaut si ni texte ni nom de fichier n'est fourni
  return {
    data: {
      title: "Développeur",
      company: "Entreprise",
      location: "Paris",
      contract_type: "CDI",
      required_skills: ["JavaScript", "HTML", "CSS"],
      preferred_skills: ["React", "Node.js"],
      responsibilities: ["Développement d'applications"],
      requirements: ["Expérience en développement web"],
      benefits: ["Environnement de travail agréable"],
      salary_range: "Selon expérience",
      remote_policy: "Non spécifié",
      application_process: ""
    },
    processing_time: Math.random() * 2 + 0.5,
    parsed_at: Date.now() / 1000,
    file_format: "txt",
    model: "mock-gpt-default"
  };
};

/**
 * Simule le parsing direct d'une fiche de poste
 * @param {File} file - Fichier de la fiche de poste
 * @returns {Promise<Object>} - Résultat simulé du parsing
 */
export const parseJobDirect = async (file) => {
  return new Promise((resolve, reject) => {
    // Lire le contenu du fichier
    const reader = new FileReader();
    
    reader.onload = (event) => {
      const text = event.target.result;
      
      // Analyser le texte
      setTimeout(() => {
        try {
          const result = generateMockResult(file.name, text);
          resolve(result);
        } catch (error) {
          reject(new Error("Erreur lors de l'analyse du fichier"));
        }
      }, MOCK_DELAY);
    };
    
    reader.onerror = () => {
      reject(new Error("Erreur lors de la lecture du fichier"));
    };
    
    // Démarrer la lecture du fichier
    reader.readAsText(file);
  });
};

/**
 * Simule le parsing de texte d'une fiche de poste
 * @param {String} text - Texte de la fiche de poste
 * @returns {Promise<Object>} - Résultat simulé du parsing
 */
export const parseJobText = async (text) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(generateMockResult("texte.txt", text));
    }, MOCK_DELAY);
  });
};

/**
 * Simule la mise en file d'attente d'un job de parsing
 * @param {File} file - Fichier de la fiche de poste
 * @param {String} priority - Priorité du job
 * @returns {Promise<Object>} - Informations sur le job créé
 */
export const queueJobParsing = async (file, priority = 'standard') => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const jobId = Math.random().toString(36).substring(2, 15);
      resolve({
        job_id: jobId,
        status: "queued",
        priority: priority,
        estimated_wait: "30s",
        webhook_configured: false
      });
    }, 500);
  });
};

/**
 * Simule la récupération du résultat d'un job de parsing
 * @param {String} jobId - Identifiant du job
 * @returns {Promise<Object>} - Résultat du parsing ou statut du job
 */
export const getJobParsingResult = async (jobId) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        status: "done",
        job_id: jobId,
        result: generateMockResult("job_result.pdf").data,
        completed_at: new Date().toISOString()
      });
    }, MOCK_DELAY);
  });
};
