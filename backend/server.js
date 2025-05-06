// server.js
require('dotenv').config(); // Pour gérer les variables d'environnement
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const { OpenAI } = require('openai');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Configuration de l'API OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY // Stocké dans les secrets GitHub
});

// Route pour générer la description à partir d'une URL
app.post('/api/generate-description', async (req, res) => {
  try {
    const { url } = req.body;
    
    if (!url) {
      return res.status(400).json({ error: 'URL requise' });
    }
    
    // Extraction du contenu du site web
    const websiteContent = await extractWebsiteContent(url);
    
    // Génération de la description avec GPT
    const description = await generateDescriptionWithGPT(websiteContent, url);
    
    res.json({ description });
  } catch (error) {
    console.error('Erreur:', error);
    res.status(500).json({ error: 'Une erreur est survenue lors de la génération de la description' });
  }
});

// Fonction pour extraire le contenu pertinent d'un site web
async function extractWebsiteContent(url) {
  try {
    // S'assurer que l'URL est correctement formatée
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }
    
    const response = await axios.get(url);
    const html = response.data;
    const $ = cheerio.load(html);
    
    // Extraire les informations pertinentes
    const title = $('title').text().trim();
    const metaDescription = $('meta[name="description"]').attr('content') || '';
    
    // Extraire le texte des sections importantes
    let aboutText = '';
    
    // Chercher les sections "à propos", "qui sommes-nous", etc.
    $('div:contains("À propos"), div:contains("Qui sommes-nous"), div:contains("About"), section:contains("À propos"), section:contains("Qui sommes-nous"), section:contains("About")').each(function() {
      aboutText += $(this).text().trim() + ' ';
    });
    
    // Chercher du texte dans les paragraphes de la page d'accueil
    let mainContent = '';
    $('p').each(function() {
      const text = $(this).text().trim();
      if (text.length > 50) { // Ignorer les petits paragraphes
        mainContent += text + ' ';
      }
    });
    
    // Limiter la taille du contenu pour éviter de dépasser les limites de l'API
    mainContent = mainContent.substring(0, 3000);
    
    return {
      title,
      metaDescription,
      aboutText: aboutText.substring(0, 1500),
      mainContent
    };
  } catch (error) {
    console.error('Erreur lors de l\'extraction du contenu:', error);
    return {
      title: '',
      metaDescription: '',
      aboutText: '',
      mainContent: ''
    };
  }
}

// Fonction pour générer la description avec GPT
async function generateDescriptionWithGPT(websiteContent, url) {
  try {
    const prompt = `
    Analyse le contenu suivant extrait du site web ${url} et génère une description professionnelle et concise de l'entreprise en français (150-200 mots maximum).
    La description doit inclure : l'activité principale, le secteur, la mission/valeurs, et les points forts/différenciants si identifiables.
    
    Titre du site: ${websiteContent.title}
    
    Meta description: ${websiteContent.metaDescription}
    
    Section À propos: ${websiteContent.aboutText}
    
    Contenu principal: ${websiteContent.mainContent}
    `;
    
    const response = await openai.chat.completions.create({
      model: "gpt-4-turbo", // Ou "gpt-3.5-turbo" selon votre abonnement
      messages: [
        { role: "system", content: "Tu es un expert en communication d'entreprise capable de synthétiser efficacement les informations clés sur une entreprise à partir de son site web." },
        { role: "user", content: prompt }
      ],
      max_tokens: 300,
      temperature: 0.7
    });
    
    return response.choices[0].message.content.trim();
  } catch (error) {
    console.error('Erreur lors de la génération avec GPT:', error);
    throw new Error('Impossible de générer la description avec GPT');
  }
}

// Démarrer le serveur
app.listen(PORT, () => {
  console.log(`Serveur démarré sur le port ${PORT}`);
});