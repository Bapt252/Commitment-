import axios from 'axios';

// URL de base du service de parsing CV
const API_URL = process.env.NEXT_PUBLIC_CV_PARSER_URL || 'http://localhost:5051';

/**
 * Service pour communiquer avec l'API de parsing CV
 */
export const cvParserService = {
  /**
   * Envoie un fichier CV pour parsing synchrone
   * @param file - Fichier CV à parser
   * @returns Les données parsées du CV
   */
  async parseCV(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`/api/parse-cv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // Normaliser les données pour assurer une structure cohérente
      return this.normalizeParserResult(response.data);
    } catch (error) {
      console.error('Erreur lors du parsing du CV:', error);
      throw error;
    }
  },

  /**
   * Envoie un fichier CV pour parsing asynchrone (mise en file d'attente)
   * @param file - Fichier CV à parser
   * @returns L'ID du job de parsing
   */
  async queueCVParsing(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_URL}/api/queue`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data.job_id;
    } catch (error) {
      console.error('Erreur lors de la mise en file d\'attente du CV:', error);
      throw error;
    }
  },

  /**
   * Vérifie le statut d'un job de parsing
   * @param jobId - ID du job de parsing
   * @returns Le statut du job
   */
  async checkJobStatus(jobId: string) {
    try {
      const response = await axios.get(`${API_URL}/api/result/${jobId}`);
      return {
        job_id: jobId,
        status: response.data.status === 'done' ? 'completed' : 
                response.data.status === 'failed' ? 'failed' : 
                response.data.status === 'running' ? 'processing' : 'pending',
        message: response.data.error || response.data.message,
        position: response.data.position_in_queue,
        total_jobs: response.data.total_jobs
      };
    } catch (error) {
      console.error('Erreur lors de la vérification du statut du job:', error);
      throw error;
    }
  },

  /**
   * Récupère le résultat d'un job de parsing
   * @param jobId - ID du job de parsing
   * @returns Le résultat du parsing
   */
  async getJobResult(jobId: string) {
    try {
      const response = await axios.get(`${API_URL}/api/result/${jobId}`);
      // Normaliser les données de résultat
      return this.normalizeParserResult(response.data.result);
    } catch (error) {
      console.error('Erreur lors de la récupération du résultat:', error);
      throw error;
    }
  },
  
  /**
   * Normalise le résultat du parsing pour garantir une structure cohérente
   * @param data - Données brutes du parsing
   * @returns Données normalisées
   */
  normalizeParserResult(data: any) {
    // Si les données sont imbriquées dans un sous-objet 'data'
    const parsedData = data.data || data;
    
    // S'assurer que toutes les propriétés principales existent
    const normalized = {
      personal_info: parsedData.personal_info || {},
      position: parsedData.position || "",
      skills: [],
      experience: [],
      education: [],
      languages: [],
      softwares: [],
      processing_time: parsedData.processing_time || 0
    };
    
    // Normaliser les informations personnelles
    normalized.personal_info = {
      name: parsedData.personal_info?.name || "",
      email: parsedData.personal_info?.email || "",
      phone: parsedData.personal_info?.phone || "",
      address: parsedData.personal_info?.address || ""
    };
    
    // Normaliser les compétences
    normalized.skills = Array.isArray(parsedData.skills) 
      ? parsedData.skills.map(skill => {
          if (typeof skill === 'object' && skill !== null) {
            return skill;
          }
          return { name: String(skill) };
        })
      : [];
      
    // Normaliser l'expérience professionnelle
    normalized.experience = Array.isArray(parsedData.experience) || Array.isArray(parsedData.experiences)
      ? (parsedData.experience || parsedData.experiences || []).map(exp => ({
          title: exp.title || "",
          company: exp.company || "",
          start_date: exp.start_date || "",
          end_date: exp.end_date || "",
          description: exp.description || ""
        }))
      : [];
      
    // Normaliser l'éducation
    normalized.education = Array.isArray(parsedData.education)
      ? parsedData.education.map(edu => ({
          degree: edu.degree || "",
          institution: edu.institution || "",
          start_date: edu.start_date || "",
          end_date: edu.end_date || ""
        }))
      : [];
      
    // Normaliser les langues
    normalized.languages = Array.isArray(parsedData.languages)
      ? parsedData.languages.map(lang => ({
          language: lang.language || "",
          level: lang.level || ""
        }))
      : [];
      
    // Normaliser les logiciels
    normalized.softwares = Array.isArray(parsedData.softwares)
      ? parsedData.softwares.map(software => software)
      : [];
    
    // Enlever le préfixe "undefined" des noms si présent
    if (normalized.personal_info.name && normalized.personal_info.name.startsWith("undefined ")) {
      normalized.personal_info.name = normalized.personal_info.name.replace("undefined ", "");
    }
    
    return normalized;
  }
};

export default cvParserService;