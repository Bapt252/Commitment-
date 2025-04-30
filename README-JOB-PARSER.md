# Guide d'utilisation du Parser de Fiches de Poste

Ce guide explique comment utiliser le service de parsing de fiches de poste dans le projet Commitment-. Ce service permet d'extraire des informations structurées à partir de fiches de poste au format PDF, DOCX ou TXT.

## Prérequis

- Docker et Docker Compose installés
- Un fichier de fiche de poste au format PDF, DOCX ou TXT
- jq (installé automatiquement par les scripts si nécessaire)

## Configuration

Le service utilise GPT-4o-mini par défaut pour extraire les données des fiches de poste. Vous avez deux options de configuration:

### 1. Utilisation avec une clé API OpenAI (recommandé)

1. Assurez-vous que votre fichier `.env` à la racine du projet contient une clé API OpenAI valide:
   ```
   OPENAI=sk-votre-clé-api-openai
   OPENAI_API_KEY=sk-votre-clé-api-openai
   USE_MOCK_PARSER=false
   ```

2. Redémarrez le service avec le script dédié:
   ```bash
   ./make-job-parser-executable.sh  # Une seule fois pour rendre les scripts exécutables
   ./restart-job-parser.sh
   ```

### 2. Utilisation en mode mock (sans clé API OpenAI)

Si vous n'avez pas de clé API OpenAI, vous pouvez utiliser le mode mock:

1. Modifiez le fichier `.env`:
   ```
   USE_MOCK_PARSER=true
   ```

2. Redémarrez le service:
   ```bash
   ./restart-job-parser.sh
   ```

## Test du service

Pour tester le service, utilisez le script `curl-test-job-parser.sh`:

```bash
./curl-test-job-parser.sh /chemin/vers/votre/fiche_de_poste.pdf
```

Le résultat du parsing sera affiché dans le terminal au format JSON.

## Structure des données extraites

Le service extrait les informations suivantes des fiches de poste:

```json
{
  "title": "Titre du poste",
  "company": "Nom de l'entreprise",
  "location": "Lieu de travail",
  "contract_type": "Type de contrat (CDI, CDD, etc.)",
  "required_skills": [
    "Compétence requise 1",
    "Compétence requise 2"
  ],
  "preferred_skills": [
    "Compétence préférée 1",
    "Compétence préférée 2"
  ],
  "responsibilities": [
    "Responsabilité 1",
    "Responsabilité 2"
  ],
  "requirements": [
    "Prérequis 1",
    "Prérequis 2"
  ],
  "benefits": [
    "Avantage 1",
    "Avantage 2"
  ],
  "salary_range": "Fourchette de salaire",
  "remote_policy": "Politique de télétravail",
  "application_process": "Processus de candidature",
  "company_description": "Description de l'entreprise"
}
```

## API REST

Le service expose également une API REST pour s'intégrer avec d'autres applications:

```bash
# Parsing direct (synchrone)
curl -X POST -F "file=@/chemin/vers/fiche.pdf" http://localhost:5053/api/parse-job

# Parsing asynchrone (file d'attente)
curl -X POST -F "file=@/chemin/vers/fiche.pdf" http://localhost:5053/api/queue

# Vérification du statut d'un job (remplacez JOB_ID par l'ID reçu)
curl http://localhost:5053/api/status/JOB_ID

# Récupération du résultat
curl http://localhost:5053/api/result/JOB_ID
```

## Dépannage

Si vous rencontrez des problèmes avec le service, essayez les étapes suivantes:

1. Vérifiez que le fichier `.env` ne contient pas de conflits Git (pas de marqueurs `<<<<<<< HEAD`)
2. Redémarrez le service avec l'option `--clean`:
   ```bash
   ./restart-job-parser.sh --clean
   ```
3. Consultez les logs du service:
   ```bash
   docker-compose logs job-parser
   docker-compose logs job-parser-worker
   ```

## Intégration avec le système de matching

Le parser de fiches de poste s'intègre avec le service de matching pour suggérer des candidats correspondant aux compétences requises. Consultez la documentation du service de matching pour plus d'informations.

---

Pour plus d'informations sur le service de parsing de fiches de poste, consultez la documentation dans `job-parser-service/README.md`.
