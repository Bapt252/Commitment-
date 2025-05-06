# Commitment - Plateforme de recrutement innovante

## Générateur de description d'entreprise avec IA

Cette fonctionnalité utilise l'API GPT pour automatiquement générer une description professionnelle d'entreprise à partir de son site web.

### Fonctionnement

1. L'utilisateur saisit l'URL du site web de son entreprise
2. L'utilisateur clique sur le bouton "Générer avec l'IA"
3. Le backend extrait le contenu pertinent du site web
4. Le contenu est analysé par l'API GPT pour générer une description concise
5. La description est affichée dans le formulaire

### Installation

#### Backend

1. Installer les dépendances :
```bash
cd backend
npm install
```

2. Créer un fichier `.env` avec votre clé API OpenAI :
```
PORT=3000
OPENAI_API_KEY=votre_clé_api
```

3. Démarrer le serveur :
```bash
npm start
```

#### Frontend

Aucune installation supplémentaire n'est nécessaire. Le frontend est déjà configuré pour communiquer avec le backend sur `http://localhost:3000`.

### Utilisation

1. Ouvrir le formulaire de questionnaire client
2. Saisir l'URL du site web dans le champ "Site internet"
3. Cliquer sur "Générer avec l'IA"
4. La description sera automatiquement générée et remplira le champ "Présentation rapide"

### Technologies utilisées

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Node.js, Express
- **Web Scraping**: Axios, Cheerio
- **IA**: OpenAI API (GPT-4 ou GPT-3.5)

### Sécurité

La clé API OpenAI est stockée de manière sécurisée dans les variables d'environnement du serveur et dans les secrets GitHub pour le déploiement.