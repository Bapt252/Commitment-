// frontend/src/pages/api/parse-cv.js
import axios from 'axios';
import formidable from 'formidable';
import fs from 'fs';

// Désactiver le body parser de Next.js pour les formulaires
export const config = {
  api: {
    bodyParser: false,
  },
};

// Fonction pour normaliser les données reçues du service de parsing CV
function normalizeParserResult(data) {
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
    
  // Normaliser l'expérience professionnelle - tenir compte des deux noms possibles (experience/experiences)
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
    ? parsedData.softwares
    : [];
  
  // Enlever le préfixe "undefined" des noms si présent
  if (normalized.personal_info.name && normalized.personal_info.name.startsWith("undefined ")) {
    normalized.personal_info.name = normalized.personal_info.name.replace("undefined ", "");
  }
  
  return normalized;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    // Utiliser formidable pour parser le formulaire multipart
    const form = new formidable.IncomingForm();
    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('Erreur lors du parsing du formulaire:', err);
        return res.status(500).json({ error: 'Erreur lors du parsing du formulaire' });
      }

      const file = files.file;
      if (!file) {
        return res.status(400).json({ error: 'Fichier manquant' });
      }

      // Créer un FormData pour l'envoi au service de parsing
      const formData = new FormData();
      
      // Ajouter le fichier au FormData
      formData.append('file', new Blob([fs.readFileSync(file.filepath)]), file.originalFilename);

      // Ajouter les options supplémentaires
      if (fields.force_refresh) {
        formData.append('force_refresh', fields.force_refresh);
      }
      if (fields.detailed_mode) {
        formData.append('detailed_mode', fields.detailed_mode);
      }

      try {
        // URL du service de parsing CV
        const CV_PARSER_URL = process.env.CV_PARSER_SERVICE_URL || 'http://cv-parser:5000';
        
        // Appeler le service de parsing CV
        const response = await axios.post(`${CV_PARSER_URL}/api/parse-cv/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        // Normaliser les données avant de les renvoyer
        const normalizedData = normalizeParserResult(response.data);
        res.status(200).json(normalizedData);
      } catch (error) {
        console.error('Erreur lors du parsing du CV:', error);
        res.status(500).json({ 
          error: 'Erreur lors du parsing du CV',
          details: error.response?.data || error.message
        });
      }
    });
  } catch (error) {
    console.error('Erreur serveur:', error);
    res.status(500).json({ error: 'Erreur serveur interne' });
  }
}