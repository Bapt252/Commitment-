# Guide du Backend Commitment-

Ce document décrit la structure du backend du projet et comment résoudre les problèmes courants.

## Structure des dossiers

```
backend/
├── app/                    # Application principale
│   ├── api/                # API endpoints
│   │   ├── api.py          # Configuration du routeur API
│   │   └── endpoints/      # Endpoints spécifiques
│   │       ├── companies.py
│   │       ├── jobs.py
│   │       └── users.py
│   ├── core/               # Configuration centrale
│   ├── db/                 # Modèles et opérations de base de données
│   ├── main.py             # Point d'entrée de l'application
│   └── nlp/                # Modules de traitement du langage naturel
│       ├── document_parser.py
│       ├── job_parser.py   # Contient les parsers pour offres d'emploi
│       └── ...
├── data/                   # Données utilisées par l'application
├── logs/                   # Fichiers de logs
├── tests/                  # Tests unitaires et d'intégration
├── .env.example            # Exemple de fichier de variables d'environnement
├── README.md               # Documentation du backend
├── requirements.txt        # Dépendances Python
├── run.py                  # Script pour démarrer l'application
└── setup_nlp.py            # Configuration des modèles NLP
```

## Résolution du problème d'importation JobDescriptionExtractor

Si vous rencontrez l'erreur :
```
ImportError: cannot import name 'JobDescriptionExtractor' from 'app.nlp.job_parser'
```

### Solution 1: Vérifier le fichier job_parser.py

Examinez le fichier `backend/app/nlp/job_parser.py` pour vérifier si la classe `JobDescriptionExtractor` est bien définie:

```python
# Elle devrait ressembler à quelque chose comme ça
class JobDescriptionExtractor:
    def __init__(self, ...):
        ...
    
    def extract_skills(self, ...):
        ...
```

Si la classe n'existe pas dans ce fichier, c'est la source du problème.

### Solution 2: Implémentation de la classe manquante

Vous pouvez créer une version simple de la classe pour éviter l'erreur:

```python
# À ajouter dans backend/app/nlp/job_parser.py
class JobDescriptionExtractor:
    """
    Classe temporaire pour extraire des informations des descriptions de poste.
    À compléter avec la vraie implémentation.
    """
    def __init__(self):
        self.ready = False
        print("JobDescriptionExtractor initialized (placeholder)")
    
    def extract_skills(self, text):
        return {"skills": []}
    
    def extract_info(self, text):
        return {
            "title": "",
            "company": "",
            "location": "",
            "skills": [],
            "experience": "",
            "education": ""
        }
```

### Solution 3: Corriger l'importation

Si la classe existe sous un nom différent dans le fichier, vous pouvez modifier l'importation dans `document_parser.py`:

```python
# Dans document_parser.py, recherchez cette ligne:
from app.nlp.job_parser import JobDescriptionExtractor, parse_job_description

# Et modifiez-la pour utiliser le nom correct de la classe
```

## Comment exécuter le backend

1. **Installer les dépendances**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configurer les variables d'environnement**:
   ```bash
   cp .env.example .env
   # Modifiez .env selon vos besoins
   ```

3. **Démarrer le serveur**:
   ```bash
   python run.py
   ```

## Dépannage

### L'API ne démarre pas

1. **Vérifiez les logs**: Les erreurs devraient apparaître dans la console ou dans le dossier `logs/`.

2. **Vérifiez les dépendances**: Assurez-vous que toutes les dépendances sont installées:
   ```bash
   pip install -r requirements.txt
   ```

3. **Vérifiez les modèles NLP**: Si vous utilisez des modèles NLP, assurez-vous qu'ils sont correctement téléchargés:
   ```bash
   python setup_nlp.py
   ```

### Problèmes avec les chemins d'importation

Si vous avez des erreurs d'importation, assurez-vous que vous exécutez les commandes depuis le bon répertoire. Les importations Python dans ce projet utilisent des chemins relatifs à partir du dossier `backend/`.

```bash
# Assurez-vous d'être dans ce dossier
cd /chemin/vers/fresh-commitment/backend
# Et non dans 
# cd /chemin/vers/fresh-commitment/Commitment-/Commitment-/backend
```
