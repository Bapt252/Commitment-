# Guide d'intégration du Job Parser

Ce guide explique comment connecter le backend job parser avec le frontend pour analyser les fiches de poste avec GPT.

## Composants ajoutés

Cette intégration ajoute les composants suivants au projet Commitment :

1. **Page d'analyse de fiche de poste** (`templates/job-description-parser.html`)
   - Interface utilisateur permettant de télécharger ou coller des fiches de poste
   - Affiche les résultats d'analyse de manière structurée

2. **Script d'intégration** (`static/js/job-description-parser.js`)
   - Gère l'interaction entre l'interface utilisateur et l'API backend
   - Traite les fichiers téléchargés et le texte collé
   - Formate et affiche les résultats

3. **Serveur proxy CORS** (`proxy-server.js` et `package.json`)
   - Facilite la communication entre le frontend et le backend
   - Résout les problèmes de CORS lors des requêtes cross-origin

## Installation et démarrage

### 1. Installation des dépendances

```bash
# À la racine du projet Commitment-
npm install
```

### 2. Démarrage des services

```bash
# Démarrer le backend job-parser avec Docker
docker-compose up job-parser

# Dans un autre terminal, démarrer le proxy CORS
node proxy-server.js
```

### 3. Accès à l'interface

Ouvrez l'URL suivante dans votre navigateur :
```
http://localhost:8000/templates/client-questionnaire.html
```

Ou accédez directement à la version GitHub Pages :
```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html
```

## Fonctionnement

L'intégration fonctionne comme suit :

1. L'utilisateur accède au formulaire client et clique sur "Analyser ma fiche de poste"
2. Le modal s'ouvre avec l'interface d'analyse de fiche de poste
3. L'utilisateur télécharge un fichier (PDF, DOCX, TXT) ou colle le texte d'une fiche de poste
4. Le frontend envoie la fiche au backend via le proxy CORS
5. Le backend (job-parser-service) analyse la fiche avec GPT-4o-mini et retourne les informations structurées
6. Les résultats s'affichent dans l'interface et l'utilisateur peut les transférer au formulaire principal
7. Les données sont intégrées au formulaire client-questionnaire.html

## Configuration

Si nécessaire, vous pouvez modifier les points suivants :

### URL de l'API

Dans `static/js/job-description-parser.js`, modifiez la constante `API_ENDPOINT` :

```javascript
// Pour utiliser le proxy CORS (recommandé)
const API_ENDPOINT = 'http://localhost:8000/api/job-parser/parse-job';

// Pour utiliser directement le service backend (peut causer des erreurs CORS)
// const API_ENDPOINT = 'http://localhost:5053/api/parse-job';
```

### Port du proxy CORS

Dans `proxy-server.js`, modifiez la constante `PORT` si le port 8000 est déjà utilisé :

```javascript
const PORT = 8000; // Remplacer par un autre port si nécessaire
```

## Dépannage

### Problèmes courants

1. **Erreur "No 'Access-Control-Allow-Origin' header"**
   - Le proxy CORS n'est pas démarré ou n'est pas correctement configuré
   - Vérifiez que le proxy est bien en cours d'exécution

2. **Erreur de connexion à l'API**
   - Vérifiez que le service job-parser est bien démarré
   - Consultez les logs Docker pour identifier les erreurs

3. **Fichier non accepté**
   - Vérifiez que vous utilisez un format de fichier supporté (PDF, DOCX, TXT)
   - Vérifiez que le fichier n'est pas trop volumineux

4. **Résultats d'analyse incomplets**
   - GPT peut avoir des difficultés à extraire certaines informations
   - Essayez avec une description de poste plus structurée ou complète

## Structure des données

Le backend renvoie un objet JSON avec la structure suivante :

```json
{
  "title": "Titre du poste",
  "skills": ["Compétence 1", "Compétence 2", "..."],
  "experience": "Niveau d'expérience requis",
  "contract_type": "Type de contrat",
  "location": "Lieu de travail",
  "salary": "Fourchette de salaire",
  "responsibilities": "Principales responsabilités"
}
```

Ces données sont ensuite formatées et affichées dans l'interface, puis peuvent être transférées au formulaire principal.
