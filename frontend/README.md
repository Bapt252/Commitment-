# Frontend - Interface de Parsing CV

Ce dossier contient l'interface utilisateur pour le parsing et l'analyse de CV du projet Commitment-.

## Fonctionnalités améliorées

### Interface de téléchargement de CV (`/cv-upload`)

L'interface de téléchargement de CV a été améliorée avec les fonctionnalités suivantes :

#### Options avancées

- **Force refresh** : Permet de forcer une nouvelle analyse du CV en ignorant le cache
- **Mode détaillé** : Active un parsing plus approfondi pour extraire davantage d'informations du CV

#### Affichage des résultats

- **Vue JSON** : Affiche les données brutes au format JSON
- **Vue structurée** : Présente les informations du CV de manière organisée et facile à lire
  - Informations personnelles
  - Compétences
  - Expérience professionnelle
  - Formation
  - Langues

#### Améliorations UI/UX

- Barre de progression pendant l'analyse
- Meilleure gestion des erreurs avec messages détaillés
- Affichage des informations sur le fichier (taille, nom, etc.)

## Intégration avec le service de parsing

L'interface communique avec le service de parsing CV via l'API proxy `/api/parse-cv`. Cette API a été améliorée pour :

- Transmettre les options supplémentaires au service backend
- Fournir des logs détaillés pour faciliter le débogage
- Gérer les erreurs de manière plus robuste

## Comment tester

1. Démarrez le projet avec Docker Compose :
   ```bash
   docker-compose up -d
   ```

2. Accédez à l'interface de téléchargement de CV :
   ```
   http://localhost:3000/cv-upload
   ```

3. Téléchargez un CV au format PDF ou DOCX

4. Sélectionnez les options souhaitées (force refresh, mode détaillé)

5. Cliquez sur "Analyser le CV" et attendez le résultat

6. Explorez les résultats dans les différentes vues (JSON ou structurée)

## Troubleshooting

Si vous rencontrez des problèmes :

1. Vérifiez que tous les services sont en cours d'exécution :
   ```bash
   docker-compose ps
   ```

2. Vérifiez les logs du frontend et du service de parsing :
   ```bash
   docker-compose logs frontend
   docker-compose logs cv-parser
   ```

3. Assurez-vous que votre fichier `.env` contient une clé API OpenAI valide
