/**
 * Service pour interagir avec l'API de parsing de fiches de poste
 */

import axios from 'axios';

// Récupérer l'URL de l'API depuis les variables d'environnement
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5050';
const JOB_PARSER_URL = `${API_URL}/api`;

/**
 * Parse une fiche de poste directement (appel synchrone)
 * @param {File} file - Fichier de la fiche de poste
 * @returns {Promise<Object>} - Résultat du parsing avec les données structurées
 */
export const parseJobDirect = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${JOB_PARSER_URL}/parse-job`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Erreur lors du parsing de la fiche de poste:', error);
    throw new Error(
      error.response?.data?.detail || 
      'Erreur lors du parsing de la fiche de poste'
    );
  }
};

/**
 * Soumet une fiche de poste pour analyse en mode asynchrone (mise en file d'attente)
 * @param {File} file - Fichier de la fiche de poste
 * @param {String} priority - Priorité du job (standard, premium, batch)
 * @returns {Promise<Object>} - Informations sur le job créé
 */
export const queueJobParsing = async (file, priority = 'standard') => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${JOB_PARSER_URL}/queue`, formData, {
      params: { priority },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Erreur lors de la mise en file d\'attente du parsing:', error);
    throw new Error(
      error.response?.data?.detail || 
      'Erreur lors de la mise en file d\'attente du parsing'
    );
  }
};

/**
 * Récupère le résultat d'un job de parsing
 * @param {String} jobId - Identifiant du job
 * @returns {Promise<Object>} - Résultat du parsing ou statut du job
 */
export const getJobParsingResult = async (jobId) => {
  try {
    const response = await axios.get(`${JOB_PARSER_URL}/result/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération du résultat:', error);
    throw new Error(
      error.response?.data?.detail || 
      'Erreur lors de la récupération du résultat'
    );
  }
};

/**
 * Parse du texte de fiche de poste (sans fichier)
 * @param {String} text - Texte de la fiche de poste
 * @returns {Promise<Object>} - Résultat du parsing avec les données structurées
 */
export const parseJobText = async (text) => {
  try {
    // Créer un fichier blob depuis le texte
    const blob = new Blob([text], { type: 'text/plain' });
    const file = new File([blob], 'job-description.txt', { type: 'text/plain' });
    
    // Utiliser la fonction parseJobDirect
    return await parseJobDirect(file);
  } catch (error) {
    console.error('Erreur lors du parsing du texte:', error);
    throw new Error(
      error.response?.data?.detail || 
      'Erreur lors du parsing du texte'
    );
  }
};
