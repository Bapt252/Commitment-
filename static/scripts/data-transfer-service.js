/**
 * DataTransferService - Un service pour standardiser le transfert de données entre pages
 * Permet de résoudre les problèmes de format de données entre les pages
 * candidate-upload.html et candidate-questionnaire.html
 */

window.DataTransferService = (function() {
  // Clé utilisée pour le stockage dans localStorage
  const STORAGE_KEY = 'parsedCvData';
  
  /**
   * Stocke les données du CV parsé de manière standardisée
   * @param {Object} data - Les données à stocker
   */
  function storeData(data) {
    if (!data) {
      console.warn('Aucune donnée à stocker');
      return false;
    }
    
    console.log('Données brutes à stocker:', data);
    
    // Créer un format normalisé pour assurer la compatibilité
    const normalizedData = {
      // Assurer que les informations personnelles sont accessibles
      personal_info: data.personal_info || (data.data && data.data.personal_info) || {},
      
      // Assurer que le titre de poste est accessible par différents chemins pour la compatibilité
      current_position: extractCurrentPosition(data),
      
      // Conserver également la structure entière pour le traitement avancé
      fullData: data,
      
      // Ajouter un timestamp pour la fraîcheur
      timestamp: new Date().toISOString()
    };
    
    // S'assurer que le nom est toujours disponible
    if (data.personal_info && data.personal_info.name) {
      normalizedData.personal_info.name = data.personal_info.name;
    } else if (data.data && data.data.personal_info && data.data.personal_info.name) {
      normalizedData.personal_info.name = data.data.personal_info.name;
    }
    
    // Stocker les données normalisées
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(normalizedData));
      // Également stocker dans sessionStorage pour la redondance
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(normalizedData));
      console.log('Données stockées avec succès dans localStorage et sessionStorage:', normalizedData);
      return true;
    } catch (error) {
      console.error('Erreur lors du stockage des données:', error);
      return false;
    }
  }
  
  /**
   * Extrait l'intitulé de poste depuis n'importe quel format de données
   * @param {Object} data - Les données brutes
   * @returns {String} - L'intitulé de poste extrait
   */
  function extractCurrentPosition(data) {
    // Vérifier toutes les sources possibles pour l'intitulé de poste
    if (data.current_position) {
      return data.current_position;
    }
    
    if (data.data && data.data.current_position) {
      return data.data.current_position;
    }
    
    if (data.jobTitle) {
      return data.jobTitle;
    }
    
    // Vérifier si available dans work_experience
    if (data.data && data.data.work_experience && data.data.work_experience.length > 0) {
      return data.data.work_experience[0].title || '';
    }
    
    if (data.work_experience && data.work_experience.length > 0) {
      return data.work_experience[0].title || '';
    }
    
    return '';
  }
  
  /**
   * Récupère les données du CV parsé depuis le stockage
   * @returns {Object|null} - Les données ou null si non trouvées
   */
  function retrieveData() {
    try {
      // Essayer d'abord localStorage
      let storedData = localStorage.getItem(STORAGE_KEY);
      
      // Si rien n'est trouvé dans localStorage, essayer sessionStorage
      if (!storedData) {
        storedData = sessionStorage.getItem(STORAGE_KEY);
        console.log('Données récupérées depuis sessionStorage');
      } else {
        console.log('Données récupérées depuis localStorage');
      }
      
      if (!storedData) {
        console.warn('Aucune donnée trouvée dans le stockage');
        return null;
      }
      
      const parsedData = JSON.parse(storedData);
      console.log('Données récupérées depuis le stockage:', parsedData);
      return parsedData;
    } catch (error) {
      console.error('Erreur lors de la récupération des données:', error);
      return null;
    }
  }
  
  /**
   * Pré-remplit manuellement les champs essentiels du formulaire
   * Cette fonction sert de solution de secours si form-prefiller échoue
   */
  function prefillEssentialFields() {
    const data = retrieveData();
    if (!data) return false;
    
    try {
      // Cibler les champs essentiels
      const nameField = document.getElementById('full-name');
      const jobField = document.getElementById('job-title');
      
      // Remplir le nom s'il est disponible
      if (nameField && data.personal_info && data.personal_info.name) {
        nameField.value = data.personal_info.name;
        // Déclencher l'événement pour les validations
        nameField.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      // Remplir le titre de poste s'il est disponible
      if (jobField && data.current_position) {
        jobField.value = data.current_position;
        // Déclencher l'événement pour les validations
        jobField.dispatchEvent(new Event('input', { bubbles: true }));
      }
      
      console.log('Champs essentiels pré-remplis manuellement');
      return true;
    } catch (error) {
      console.error('Erreur lors du pré-remplissage manuel:', error);
      return false;
    }
  }
  
  /**
   * Efface les données stockées
   */
  function clearData() {
    localStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
    console.log('Données effacées du stockage');
  }
  
  // Interface publique
  return {
    storeData,
    retrieveData,
    prefillEssentialFields,
    clearData
  };
})();

// Auto-exécution pour les pages de questionnaire
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si nous sommes sur la page du questionnaire
  if (window.location.href.includes('candidate-questionnaire.html')) {
    console.log('Page de questionnaire détectée - Application du pré-remplissage de secours');
    
    // Attendre un peu pour laisser form-prefiller s'exécuter d'abord
    setTimeout(function() {
      // Vérifier si le champ de titre de poste est vide
      const jobField = document.getElementById('job-title');
      if (jobField && !jobField.value) {
        console.log('Le champ titre de poste est vide, application du pré-remplissage manuel');
        window.DataTransferService.prefillEssentialFields();
      }
    }, 1000);
  }
});