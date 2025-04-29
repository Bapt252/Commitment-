/**
 * Exemple de données parsées pour tester le pré-remplissage du formulaire
 * À stocker dans sessionStorage pour simuler des données venant du backend
 */

// Format correspondant au format de données du backend (format brut avant transformation)
const mockParsedData = {
  "processing_time": 1.23,
  "parsed_at": 1714505237.987,
  "file_format": ".pdf",
  "model": "gpt-4o-mini",
  "data": {
    "personal_info": {
      "name": "Thomas Dupont",
      "email": "thomas.dupont@email.com",
      "phone": "06 12 34 56 78",
      "address": "15 Rue de la République, 75001 Paris"
    },
    "position": "Développeur Full Stack JavaScript",
    "skills": [
      { "name": "JavaScript" },
      { "name": "React" },
      { "name": "Node.js" },
      { "name": "TypeScript" },
      { "name": "Express" }
    ],
    "experience": [
      {
        "title": "Développeur Frontend",
        "company": "TechStart",
        "start_date": "Janvier 2021",
        "end_date": "Présent",
        "description": "Développement d'applications web avec React"
      },
      {
        "title": "Développeur Junior",
        "company": "WebAgency",
        "start_date": "Juin 2019",
        "end_date": "Décembre 2020",
        "description": "Maintenance et développement d'applications web"
      }
    ],
    "education": [
      {
        "degree": "Master en Informatique",
        "institution": "Université Paris-Saclay",
        "start_date": "2017",
        "end_date": "2019"
      },
      {
        "degree": "Licence Informatique",
        "institution": "Université de Lyon",
        "start_date": "2014",
        "end_date": "2017"
      }
    ],
    "languages": [
      { "language": "Français", "level": "Natif" },
      { "language": "Anglais", "level": "Courant" },
      { "language": "Espagnol", "level": "Intermédiaire" }
    ],
    "softwares": [
      "VS Code",
      "Git",
      "Docker",
      "Figma",
      "Jira"
    ]
  }
};

/**
 * Fonction pour stocker les données dans sessionStorage
 * À exécuter dans la console pour tester le pré-remplissage
 */
function storeParseDataForTesting() {
  sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
  console.log("Données parsées stockées dans sessionStorage. Rechargez la page pour voir le pré-remplissage automatique.");
}

// Si vous êtes en mode développement, vous pouvez décommenter cette ligne pour charger 
// automatiquement les données de test
// storeParseDataForTesting();