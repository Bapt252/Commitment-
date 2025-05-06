# Intégration de l'API OpenAI

Ce document explique comment l'API OpenAI est intégrée au projet Commitment- pour générer automatiquement des descriptions d'entreprise à partir de leur site web.

## Prérequis

- Compte OpenAI avec une clé API valide (https://platform.openai.com)
- Node.js version 14.x ou supérieure

## Configuration

La clé API OpenAI est stockée dans le fichier `.env` du backend :

```
OPENAI_API_KEY=votre_clé_api
```

Pour le déploiement, la clé est stockée dans les secrets GitHub et injectée dans l'environnement par le workflow GitHub Actions.

## Implémentation

### 1. Extraction du contenu du site web

Le backend utilise Axios pour récupérer le contenu HTML et Cheerio pour le parser :

```javascript
async function extractWebsiteContent(url) {
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
  
  // Chercher les sections importantes comme "À propos"
  let aboutText = '';
  $('div:contains("À propos"), div:contains("Qui sommes-nous")').each(function() {
    aboutText += $(this).text().trim() + ' ';
  });
  
  // Extraire le contenu des paragraphes pertinents
  let mainContent = '';
  $('p').each(function() {
    const text = $(this).text().trim();
    if (text.length > 50) {
      mainContent += text + ' ';
    }
  });
  
  return {
    title,
    metaDescription,
    aboutText: aboutText.substring(0, 1500),
    mainContent: mainContent.substring(0, 3000)
  };
}
```

### 2. Génération avec GPT

Le contenu extrait est envoyé à l'API OpenAI pour générer une description professionnelle :

```javascript
async function generateDescriptionWithGPT(websiteContent, url) {
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
}
```

### 3. Intégration frontend

Le bouton "Générer avec l'IA" dans le formulaire envoie une requête au backend :

```javascript
document.getElementById('generate-presentation').addEventListener('click', async function() {
  const websiteUrl = document.getElementById('website').value;
  const presentation = document.getElementById('presentation');
  const generateBtn = document.getElementById('generate-presentation');
  
  if (!websiteUrl) {
    showNotification('Veuillez d\'abord saisir l\'URL de votre site web', 'error');
    return;
  }
  
  // Animation du bouton et message de chargement
  generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Génération en cours...';
  generateBtn.disabled = true;
  
  try {
    // Appel API
    const response = await fetch('http://localhost:3000/api/generate-description', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: websiteUrl })
    });
    
    if (!response.ok) throw new Error('Erreur lors de la génération');
    
    const data = await response.json();
    presentation.value = data.description;
    
    // Restaurer le bouton
    generateBtn.innerHTML = '<i class="fas fa-magic"></i> Générer avec l\'IA';
    generateBtn.disabled = false;
    
    showNotification('Présentation générée avec succès !');
  } catch (error) {
    console.error('Erreur:', error);
    // Gestion d'erreur...
  }
});
```

## Améliorations possibles

- **Multilangue** : Détecter la langue du site web et générer la description dans la même langue
- **Mode économique** : Option pour utiliser GPT-3.5 au lieu de GPT-4 pour réduire les coûts
- **Cache** : Mettre en cache les résultats pour éviter des appels API répétés pour le même site
- **Analyse plus profonde** : Extraire plus d'informations comme l'historique, les produits, etc.
- **Personnalisation** : Permettre aux utilisateurs de choisir le style de la description