// frontend/src/pages/api/parse-cv.js
import axios from 'axios';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';

// Désactiver le body parser de Next.js pour les formulaires
export const config = {
  api: {
    bodyParser: false,
  },
};

// Définir un répertoire sécurisé pour les fichiers temporaires
const UPLOAD_DIR = path.resolve(process.cwd(), 'tmp/uploads');

// Fonction pour vérifier si un chemin est sécurisé (dans le répertoire autorisé)
function isPathSafe(filePath) {
  const normalizedPath = path.normalize(filePath);
  const resolvedPath = path.resolve(normalizedPath);
  return resolvedPath.startsWith(UPLOAD_DIR);
}

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
    // S'assurer que le répertoire de téléchargement existe
    try {
      if (!fs.existsSync(UPLOAD_DIR)) {
        fs.mkdirSync(UPLOAD_DIR, { recursive: true });
      }
    } catch (err) {
      console.error('Erreur lors de la création du répertoire de téléchargement:', err);
      return res.status(500).json({ error: 'Erreur lors de la configuration du serveur' });
    }

    // Configurer formidable pour utiliser un répertoire sécurisé
    const form = new formidable.IncomingForm({
      uploadDir: UPLOAD_DIR,
      keepExtensions: true,
      maxFileSize: 10 * 1024 * 1024 // 10MB
    });

    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('Erreur lors du parsing du formulaire:', err);
        return res.status(500).json({ error: 'Erreur lors du parsing du formulaire' });
      }

      const file = files.file;
      if (!file) {
        return res.status(400).json({ error: 'Fichier manquant' });
      }

      // Vérifier si le chemin du fichier est sécurisé
      if (!isPathSafe(file.filepath)) {
        console.error('Tentative d\'accès à un chemin non autorisé:', file.filepath);
        return res.status(403).json({ error: 'Accès au fichier non autorisé' });
      }

      try {
        // Lire le fichier de manière sécurisée
        const fileBuffer = fs.readFileSync(path.resolve(file.filepath));
        
        // Créer un FormData pour l'envoi au service de parsing
        const formData = new FormData();
        
        // Ajouter le fichier au FormData avec un nom sécurisé
        const safeFilename = path.basename(file.originalFilename || 'document.pdf');
        formData.append('file', new Blob([fileBuffer]), safeFilename);

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

          // Nettoyer le fichier temporaire
          try {
            fs.unlinkSync(file.filepath);
          } catch (cleanupErr) {
            console.error('Erreur lors du nettoyage du fichier temporaire:', cleanupErr);
          }

          // Normaliser les données avant de les renvoyer
          const normalizedData = normalizeParserResult(response.data);
          res.status(200).json(normalizedData);
        } catch (error) {
          // Nettoyer le fichier temporaire en cas d'erreur
          try {
            fs.unlinkSync(file.filepath);
          } catch (cleanupErr) {
            console.error('Erreur lors du nettoyage du fichier temporaire:', cleanupErr);
          }

          console.error('Erreur lors du parsing du CV:', error);
          res.status(500).json({ 
            error: 'Erreur lors du parsing du CV',
            details: error.response?.data || error.message
          });
        }
      } catch (fileError) {
        console.error('Erreur lors de la lecture du fichier:', fileError);
        res.status(500).json({ error: 'Erreur lors de la lecture du fichier' });
      }
    });
  } catch (error) {
    console.error('Erreur serveur:', error);
    res.status(500).json({ error: 'Erreur serveur interne' });
  }
}