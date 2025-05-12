# Configuration du Backend Job Parser avec GPT

Ce dossier contient le serveur backend pour le Job Parser qui permet d'analyser les fiches de poste grâce à GPT.

## Prérequis

- Python 3.7+ installé sur votre machine
- Pip (gestionnaire de paquets Python)
- Une clé API OpenAI

## Installation

1. Installez les dépendances requises :

```bash
pip install flask flask-cors openai
```

2. Configurez la clé API OpenAI en tant que variable d'environnement :

Sous Linux/Mac :
```bash
export OPENAI_API_KEY="votre-clé-api-openai"
```

Sous Windows (CMD) :
```batch
set OPENAI_API_KEY=votre-clé-api-openai
```

Sous Windows (PowerShell) :
```powershell
$env:OPENAI_API_KEY="votre-clé-api-openai"
```

## Démarrage du serveur

1. Naviguez dans le dossier `backend` :

```bash
cd backend
```

2. Démarrez le serveur Flask :

```bash
python api.py
```

Le serveur démarrera sur le port 5000 par défaut. Vous pouvez modifier le port en définissant la variable d'environnement `PORT`.

## Connexion avec le frontend

Le frontend est déjà configuré pour se connecter à `/api/job-parser`. Vous devez donc vous assurer que le serveur est accessible à cette URL.

### Méthode 1 : Configuration avec un serveur proxy inverse (recommandé pour la production)

Configurez un serveur proxy comme Nginx pour rediriger les requêtes `/api/job-parser` vers le serveur backend.

Exemple de configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        root /chemin/vers/Commitment-;
        index index.html;
    }
    
    location /api/job-parser {
        proxy_pass http://localhost:5000/api/job-parser;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Méthode 2 : Modification temporaire pour le développement

Pour le développement, vous pouvez modifier temporairement le fichier `js/job-parser-api.js` pour pointer directement vers le serveur backend :

```javascript
const JOB_PARSER_CONFIG = {
    // URL de base de l'API (à modifier selon l'environnement)
    apiBaseUrl: 'http://localhost:5000/api/job-parser',
    
    // Autres options...
};
```

## Tester le backend

Vous pouvez tester le backend avec curl :

```bash
# Test de soumission d'un job d'analyse
curl -X POST http://localhost:5000/api/job-parser/queue -F "text=Développeur Web Senior. Entreprise: TechCorp. Expérience: 5+ ans. Compétences: JavaScript, React, Node.js."

# Obtention du résultat (remplacez JOB_ID par l'ID obtenu)
curl http://localhost:5000/api/job-parser/result/JOB_ID
```

## Structure des réponses API

### Soumission d'un job

**Endpoint:** `POST /api/job-parser/queue`

**Corps de la requête:**
- `file`: Fichier contenant la fiche de poste (PDF, DOCX, TXT)
- OU
- `text`: Texte de la fiche de poste

**Réponse:**
```json
{
    "job_id": "uuid-du-job",
    "status": "pending"
}
```

### Récupération du résultat

**Endpoint:** `GET /api/job-parser/result/{job_id}`

**Réponse (en cours):**
```json
{
    "status": "pending|processing",
    "message": "Job en cours de traitement"
}
```

**Réponse (terminé avec succès):**
```json
{
    "status": "done",
    "result": {
        "title": "Titre du poste",
        "company": "Nom de l'entreprise",
        "location": "Lieu",
        "skills": ["Compétence 1", "Compétence 2", ...],
        "experience": "Niveau d'expérience requis",
        "responsibilities": ["Responsabilité 1", "Responsabilité 2", ...],
        "requirements": ["Prérequis 1", "Prérequis 2", ...],
        "salary": "Fourchette de salaire",
        "benefits": ["Avantage 1", "Avantage 2", ...]
    }
}
```

**Réponse (échec):**
```json
{
    "status": "failed",
    "error": "Description de l'erreur"
}
```
