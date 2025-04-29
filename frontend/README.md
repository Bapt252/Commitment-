# Frontend - Interface de Parsing CV

Ce dossier contient l'interface utilisateur pour le parsing et l'analyse de CV du projet Commitment-.

## Nouvelles fonctionnalités

### Page d'analyse de CV (`/cv-parser`)

Une nouvelle page d'analyse de CV a été créée avec les fonctionnalités suivantes :

- Upload de fichiers CV (PDF, DOC, DOCX, TXT)
- Support du drag & drop pour faciliter l'upload
- Choix entre parsing synchrone et asynchrone
- Visualisation des résultats d'analyse structurée
- Téléchargement des données au format JSON
- Interface responsive et agréable à utiliser

### Intégration directe avec le service de parsing GPT

Le frontend communique maintenant directement avec le service de parsing CV basé sur GPT :

- Appels API directs vers le service de parsing CV
- Support du parsing synchrone (attente directe du résultat)
- Support du parsing asynchrone via file d'attente (recommandé pour les gros fichiers)
- Gestion des états de chargement et des erreurs
- Affichage de la progression dans la file d'attente pour le mode asynchrone

## Comment démarrer

1. Assurez-vous que le service de parsing CV est en cours d'exécution :
   ```bash
   docker-compose up -d cv-parser
   ```

2. Créez un fichier `.env` dans le dossier frontend (vous pouvez copier `.env.example`) :
   ```bash
   cp .env.example .env
   ```

3. Configurez les variables d'environnement dans le fichier `.env` :
   ```
   NEXT_PUBLIC_CV_PARSER_URL=http://localhost:5051/api/v1
   ```

4. Installez les dépendances et démarrez le frontend :
   ```bash
   npm install
   npm run dev
   ```

5. Accédez à l'interface d'analyse de CV :
   ```
   http://localhost:3000/cv-parser
   ```

## Intégration avec le service de parsing GPT

L'intégration avec le service de parsing CV basé sur GPT est gérée par le service `cvParserService.ts`. Ce service offre les fonctionnalités suivantes :

- `parseCV(file)` : Analyse un CV de manière synchrone et renvoie immédiatement les résultats
- `queueCVParsing(file)` : Place un CV dans la file d'attente pour une analyse asynchrone et renvoie un ID de job
- `checkJobStatus(jobId)` : Vérifie l'état d'un job de parsing asynchrone
- `getJobResult(jobId)` : Récupère le résultat d'un job de parsing une fois celui-ci terminé

## Structure des données

Les données extraites des CV sont typées avec TypeScript pour une meilleure expérience de développement :

- `CVData` : Structure complète des données extraites d'un CV
- `PersonalInfo` : Informations personnelles (nom, email, téléphone, etc.)
- `WorkExperience` : Expériences professionnelles
- `Education` : Formations
- `Language` : Langues maîtrisées

## Composants clés

- `CVUploader` : Composant pour l'upload et le parsing de CV
- `CVViewer` : Composant pour l'affichage structuré des données extraites du CV

## Configuration

Assurez-vous que les variables d'environnement suivantes sont correctement configurées dans votre fichier `.env` :

```
NEXT_PUBLIC_CV_PARSER_URL=http://localhost:5051/api/v1
```

Pour un déploiement en production, remplacez l'URL par celle de votre service de parsing CV en production.

## Troubleshooting

Si vous rencontrez des problèmes :

1. Vérifiez que le service de parsing CV est en cours d'exécution :
   ```bash
   docker-compose ps cv-parser
   ```

2. Vérifiez les logs du service de parsing CV :
   ```bash
   docker-compose logs cv-parser
   ```

3. Assurez-vous que les ports sont correctement configurés et accessibles

4. Si vous utilisez le mode asynchrone, vérifiez que le service worker est en cours d'exécution :
   ```bash
   docker-compose logs cv-parser-worker
   ```

5. Vérifiez votre fichier `.env` pour vous assurer que l'URL du service de parsing est correcte
