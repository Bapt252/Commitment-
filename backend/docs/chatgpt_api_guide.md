# Guide d'utilisation de l'API ChatGPT dans Commitment

Ce guide explique comment utiliser l'API ChatGPT intégrée dans la plateforme Commitment.

## Aperçu

L'API ChatGPT permet d'interagir directement avec les modèles GPT d'OpenAI pour des conversations naturelles. Elle peut être utilisée pour :

- Assister les recruteurs dans la rédaction d'offres d'emploi
- Aider les candidats à optimiser leur CV ou lettre de motivation
- Répondre aux questions sur le fonctionnement de la plateforme
- Analyser des textes ou des données

## Configuration

L'API utilise le secret GitHub "OPENAI" qui est déjà configuré dans votre dépôt. Par défaut, elle utilise le modèle `gpt-4o-mini`.

## Utilisation de l'API REST

### 1. Démarrer une conversation

Pour démarrer une nouvelle conversation avec ChatGPT :

```http
POST /api/chat-gpt/chat/session
Content-Type: application/json

{
  "message": "Bonjour, peux-tu m'aider à rédiger une offre d'emploi pour un développeur Python ?",
  "model": "gpt-4o-mini"  // Optionnel, utilise gpt-4o-mini par défaut
}
```

Réponse :

```json
{
  "response": "Bonjour ! Je serais ravi de vous aider à rédiger une offre d'emploi pour un développeur Python...",
  "history": [
    {
      "role": "system",
      "content": "Tu es un assistant intelligent et utile pour Commitment, une plateforme de matching entre candidats et offres d'emploi."
    },
    {
      "role": "user",
      "content": "Bonjour, peux-tu m'aider à rédiger une offre d'emploi pour un développeur Python ?"
    },
    {
      "role": "assistant",
      "content": "Bonjour ! Je serais ravi de vous aider à rédiger une offre d'emploi pour un développeur Python..."
    }
  ]
}
```

### 2. Continuer une conversation

Pour continuer la conversation, incluez l'historique des messages précédents :

```http
POST /api/chat-gpt/chat
Content-Type: application/json

{
  "message": "Ajoute aussi des compétences en data science",
  "history": [
    {
      "role": "system",
      "content": "Tu es un assistant intelligent et utile pour Commitment, une plateforme de matching entre candidats et offres d'emploi."
    },
    {
      "role": "user",
      "content": "Bonjour, peux-tu m'aider à rédiger une offre d'emploi pour un développeur Python ?"
    },
    {
      "role": "assistant",
      "content": "Bonjour ! Je serais ravi de vous aider à rédiger une offre d'emploi pour un développeur Python..."
    }
  ]
}
```

## Intégration dans le frontend

### Exemple d'intégration JavaScript

```javascript
// Fonction pour envoyer un message à l'API ChatGPT
async function sendMessageToChatGPT(message, history = null) {
  const endpoint = history ? '/api/chat-gpt/chat' : '/api/chat-gpt/chat/session';
  
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}` // Si authentification requise
    },
    body: JSON.stringify({
      message,
      history
    })
  });
  
  return await response.json();
}

// Exemple d'utilisation dans une interface de chat
let chatHistory = null;

// Premier message
async function startChat() {
  const userMessage = document.getElementById('userInput').value;
  const result = await sendMessageToChatGPT(userMessage);
  
  // Afficher la réponse
  displayMessage(result.response, 'assistant');
  
  // Enregistrer l'historique pour les messages suivants
  chatHistory = result.history;
}

// Messages suivants
async function continueChat() {
  const userMessage = document.getElementById('userInput').value;
  const result = await sendMessageToChatGPT(userMessage, chatHistory);
  
  // Afficher la réponse
  displayMessage(result.response, 'assistant');
  
  // Mettre à jour l'historique
  chatHistory = result.history;
}
```

## Exemples d'utilisation

### 1. Assistant de rédaction d'offres d'emploi

```javascript
// Exemple de prompt pour générer une offre d'emploi
const jobDescription = "Nous recherchons un développeur Python avec au moins 3 ans d'expérience.";
const companyInfo = "Notre entreprise est spécialisée dans l'IA et le machine learning.";
const location = "Paris, possibilité de télétravail partiel";

const message = `Génère une offre d'emploi complète pour un développeur Python avec ces informations :
- Description du poste : ${jobDescription}
- À propos de l'entreprise : ${companyInfo}
- Localisation : ${location}
- Salaire : 45-55K€`;

const result = await sendMessageToChatGPT(message);
```

### 2. Analyse de CV

```javascript
// Exemple de prompt pour analyser un CV
const cvText = "..."; // Texte du CV extrait
const message = `Analyse ce CV et donne-moi un résumé des points forts et des points d'amélioration :
${cvText}`;

const result = await sendMessageToChatGPT(message);
```

## Bonnes pratiques

1. **Soyez précis dans vos instructions** : Plus vos prompts sont clairs, meilleurs seront les résultats.

2. **Conservez l'historique** : Pour une conversation cohérente, assurez-vous de conserver et transmettre l'historique complet.

3. **Validez les réponses** : Les réponses de GPT doivent toujours être vérifiées par un humain avant d'être utilisées dans un contexte professionnel.

4. **Optimisez les coûts** : Limitez la longueur des conversations pour réduire les coûts de l'API.

## Dépannage

Si vous rencontrez des problèmes avec l'API ChatGPT :

1. Vérifiez que le secret GitHub "OPENAI" est correctement configuré
2. Assurez-vous que votre application a accès aux secrets GitHub en production
3. Vérifiez les logs pour identifier les erreurs potentielles
4. Assurez-vous que le format de vos requêtes API est correct

Pour tout problème persistant, contactez l'équipe de développement.
