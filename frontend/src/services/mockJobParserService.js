/**
 * Service mock pour simuler le parsing de fiches de poste
 * À utiliser temporairement jusqu'à ce que le backend soit réparé
 */

// Délai simulé pour imiter un appel API (en ms)
const MOCK_DELAY = 1500;

/**
 * Génère un résultat de parsing factice mais réaliste
 * @param {String} filename - Nom du fichier ou texte court du contenu
 * @returns {Object} - Résultat simulé du parsing
 */
const generateMockResult = (filename = "", text = "") => {
  // Détection basique du type de poste à partir du nom de fichier ou du début du texte
  const content = text || filename;
  let title = "Développeur Full Stack";
  let skills = [
    "JavaScript", "React", "Node.js", "MongoDB", "Git", "Agile"
  ];
  
  if (content.toLowerCase().includes("devops")) {
    title = "Ingénieur DevOps";
    skills = ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Ansible"];
  } else if (content.toLowerCase().includes("data")) {
    title = "Data Scientist";
    skills = ["Python", "R", "SQL", "Machine Learning", "TensorFlow", "Pandas"];
  } else if (content.toLowerCase().includes("front")) {
    title = "Développeur Frontend";
    skills = ["HTML", "CSS", "JavaScript", "React", "Vue.js", "UX/UI"];
  } else if (content.toLowerCase().includes("back")) {
    title = "Développeur Backend";
    skills = ["Java", "Spring", "Node.js", "SQL", "MongoDB", "API REST"];
  }

  return {
    data: {
      title: title,
      company: "Nexten Technologies",
      location: "Paris, France",
      contract_type: "CDI",
      required_skills: skills,
      preferred_skills: [
        "TypeScript",
        "GraphQL",
        "Jest"
      ],
      responsibilities: [
        "Développer et maintenir des applications web modernes",
        "Travailler en équipe en utilisant une méthodologie Agile",
        "Participer aux revues de code et assurer la qualité du code",
        "Intégrer les services backend avec les interfaces utilisateur",
        "Résoudre les problèmes techniques et optimiser les performances"
      ],
      requirements: [
        "3-5 ans d'expérience en développement logiciel",
        "Solide expérience en JavaScript et frameworks modernes",
        "Bonnes pratiques de développement (tests, documentation, CI/CD)",
        "Bon niveau d'anglais technique",
        "Diplôme en informatique ou expérience équivalente"
      ],
      benefits: [
        "Télétravail partiel (3j/semaine)",
        "Mutuelle d'entreprise",
        "Tickets restaurant",
        "RTT",
        "Formation continue",
        "Événements d'entreprise"
      ],
      salary_range: "45K€ - 70K€ selon expérience",
      remote_policy: "Hybride (3j télétravail/semaine)",
      application_process: "CV et lettre de motivation à envoyer à recrutement@nexten.fr"
    },
    processing_time: Math.random() * 2 + 0.5, // Entre 0.5 et 2.5 secondes
    parsed_at: Date.now() / 1000,
    file_format: filename.split('.').pop() || "txt",
    model: "mock-gpt"
  };
};

/**
 * Simule le parsing direct d'une fiche de poste
 * @param {File} file - Fichier de la fiche de poste
 * @returns {Promise<Object>} - Résultat simulé du parsing
 */
export const parseJobDirect = async (file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(generateMockResult(file.name));
    }, MOCK_DELAY);
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
