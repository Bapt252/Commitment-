import axios from 'axios';

// URL de base du service de parsing CV
const API_URL = process.env.NEXT_PUBLIC_CV_PARSER_URL || 'http://localhost:5051/api/v1';

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
      
      const response = await axios.post(`${API_URL}/parse`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
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
      
      const response = await axios.post(`${API_URL}/queue`, formData, {
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
      const response = await axios.get(`${API_URL}/status/${jobId}`);
      return response.data;
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
      const response = await axios.get(`${API_URL}/result/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du résultat:', error);
      throw error;
    }
  }
};

export default cvParserService;
