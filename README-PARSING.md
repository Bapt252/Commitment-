# Guide de test du Parser de CV

Ce guide vous explique comment tester le service de parsing de CV dans le projet Commitment-. Plusieurs scripts ont été créés pour faciliter cette opération.

## Prérequis

- Docker et Docker Compose installés
- Un fichier CV au format PDF, DOCX ou TXT (par défaut, le système cherche `MonSuperCV.pdf` sur votre bureau)
- jq (installé automatiquement par les scripts si nécessaire)

## Méthodes de test

Trois scripts principaux sont disponibles pour tester le parsing de CV :

### 1. Test rapide avec mode mock (sans clé API OpenAI)

Le mode mock utilise un parser simplifié qui ne nécessite pas de clé API OpenAI. C'est la méthode la plus rapide pour tester l'interface.

```bash
# Rendre le script exécutable
chmod +x test-mock-cv.sh

# Exécuter avec votre CV
./test-mock-cv.sh /chemin/vers/votre/cv.pdf

# Ou sans arguments pour utiliser le CV par défaut sur le bureau
./test-mock-cv.sh
```

### 2. Test avec le parser réel (nécessite une clé API OpenAI)

Pour utiliser le parser basé sur GPT-4o-mini, vous devez d'abord configurer votre clé API OpenAI.

1. Modifiez le fichier `.env` à la racine du projet :
   ```
   OPENAI=sk-votre-clé-api-openai
   OPENAI_API_KEY=sk-votre-clé-api-openai
   USE_MOCK_PARSER=false
   ```

2. Exécutez le script de test :
   ```bash
   chmod +x test-mon-cv.sh
   ./test-mon-cv.sh /chemin/vers/votre/cv.pdf
   ```

### 3. Redémarrage des services

Si vous rencontrez des problèmes avec les services, vous pouvez les redémarrer :

```bash
chmod +x restart-services.sh
./restart-services.sh

# Pour un redémarrage complet avec nettoyage des conteneurs
./restart-services.sh --clean
```

## Résolution de problèmes

### Les services sont "unhealthy" ou redémarrent en boucle

Vérifiez les logs pour identifier le problème :

```bash
docker-compose logs cv-parser
docker-compose logs cv-parser-worker
```

### Problèmes de configuration OpenAI

Si vous rencontrez des erreurs liées à l'API OpenAI, vous avez deux options :

1. Utilisez le mode mock (plus rapide et ne nécessite pas de clé API) :
   ```bash
   ./test-mock-cv.sh
   ```

2. Assurez-vous que votre clé API est correctement configurée dans le fichier `.env`

### Port incorrect ou service inaccessible

Les scripts sont conçus pour détecter automatiquement le port utilisé par le service. Si vous rencontrez des problèmes, vérifiez l'état des services :

```bash
docker-compose ps
```

## Comprendre les résultats du parsing

Le résultat du parsing est sauvegardé dans un fichier JSON (`resultat_mon_cv.json` ou `resultat_mock_cv.json`). Ce fichier contient les informations extraites du CV :

- Informations personnelles (nom, email, téléphone, etc.)
- Compétences
- Expériences professionnelles
- Formation
- Langues

Exemple de structure JSON :
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+33 6 12 34 56 78"
  },
  "skills": ["Python", "JavaScript", "Docker"],
  "work_experience": [
    {
      "title": "Développeur Full Stack",
      "company": "TechCorp",
      "start_date": "2020-01",
      "end_date": "2023-03",
      "description": "..."
    }
  ],
  "education": [
    {
      "degree": "Master en Informatique",
      "institution": "Université de Paris",
      "start_date": "2016",
      "end_date": "2018"
    }
  ],
  "languages": [
    {
      "language": "Français",
      "level": "Natif"
    },
    {
      "language": "Anglais",
      "level": "Courant"
    }
  ]
}
```

## API REST pour le parsing

Vous pouvez également utiliser directement l'API REST du service de parsing de CV :

```bash
# Parsing synchrone
curl -X POST -F "file=@/chemin/vers/votre/cv.pdf" http://localhost:5051/api/v1/parse

# Parsing asynchrone (file d'attente)
curl -X POST -F "file=@/chemin/vers/votre/cv.pdf" http://localhost:5051/api/queue

# Vérification du statut d'un job (remplacez JOB_ID par l'ID reçu)
curl http://localhost:5051/api/status/JOB_ID

# Récupération du résultat
curl http://localhost:5051/api/result/JOB_ID
```

## Utilisation dans une application

Pour intégrer le parsing de CV dans votre application, vous pouvez utiliser les endpoints décrits ci-dessus. Les résultats sont au format JSON et peuvent être facilement intégrés dans vos interfaces utilisateur ou traitements automatisés.

---

Pour plus d'informations sur le service de parsing de CV, consultez la documentation dans `cv-parser-service/README.md`.