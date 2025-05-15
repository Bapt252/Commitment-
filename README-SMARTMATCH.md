# Nexten SmartMatch

Nexten SmartMatch est un système intelligent de mise en correspondance bidirectionnelle entre CV et fiches de poste. Il offre une solution complète d'analyse et de matching pour optimiser le processus de recrutement.

## Fonctionnalités

- **Matching bidirectionnel** : Faites correspondre des CV à des postes ou des postes à des CV selon vos besoins.
- **Analyse approfondie** : Extraction et mise en correspondance de multiples critères (compétences, expérience, formation, localisation, etc.).
- **Intégration avec les services de parsing existants** : Compatibilité avec les services de parsing de CV et d'offres d'emploi déjà en place.
- **API REST complète** : Interface facile à intégrer dans n'importe quelle application.
- **Scoring détaillé** : Obtenez des scores de correspondance précis avec une explication détaillée des résultats.

## Architecture

L'architecture de SmartMatch est composée de plusieurs modules :

1. **SmartMatcher** : Le moteur de matching qui calcule les correspondances entre les CV et les fiches de poste.
2. **ParsingAdapter** : Un adaptateur qui se connecte aux services de parsing existants pour extraire les données structurées des CV et des fiches de poste.
3. **MatchingPipeline** : Une classe qui coordonne le processus complet, de l'extraction des données au matching.
4. **API REST FastAPI** : Une interface REST pour exposer les fonctionnalités de SmartMatch.

```
┌──────────────────┐    ┌───────────────────┐
│   Matching API   │◄───┤ Matching Pipeline │
└─────────┬────────┘    └────────┬──────────┘
          │                      │
          │                      │
          ▼                      ▼
┌──────────────────┐    ┌───────────────────┐
│  Parsing Adapter │    │   Smart Matcher   │
└─────────┬────────┘    └───────────────────┘
          │
          │
          ▼
┌──────────────────┐    ┌───────────────────┐
│   CV Parser      │    │    Job Parser     │
└──────────────────┘    └───────────────────┘
```

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Bapt252/Commitment-.git
   cd Commitment-
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements-smartmatch.txt
   ```

3. Configurez les variables d'environnement (créez un fichier `.env`) :
   ```
   CV_PARSER_URL=http://localhost:5051
   JOB_PARSER_URL=http://localhost:5055
   PORT=5052
   RELOAD=True
   ```

## Utilisation

### Démarrer l'API

```bash
python run_matching_api.py
```

### Endpoints API

- `/health` : Vérification de l'état de santé du service
- `/api/match/cv-to-job` : Matcher un CV à une fiche de poste
- `/api/match/job-to-cv` : Matcher une fiche de poste à un CV
- `/api/match/multi-cv` : Matcher plusieurs CV à une fiche de poste
- `/api/match/job-to-multi-cv` : Matcher une fiche de poste à plusieurs CV
- `/api/match/score-explanation` : Obtenir des explications sur le calcul du score

### Exemples d'utilisation

#### Matcher un CV à une fiche de poste

```bash
curl -X POST http://localhost:5052/api/match/cv-to-job \
  -F "cv_file=@/chemin/vers/cv.pdf" \
  -F "job_description=Description du poste..."
```

#### Matcher une fiche de poste à un CV

```bash
curl -X POST http://localhost:5052/api/match/job-to-cv \
  -F "job_description=Description du poste..." \
  -F "cv_file=@/chemin/vers/cv.pdf"
```

## Intégration

SmartMatch s'intègre facilement à d'autres systèmes :

1. **Services de parsing** : Configurez les URL des services de parsing dans le fichier `.env` ou lors de la création des adaptateurs.
2. **APIs externes** : Utilisez l'API REST pour intégrer SmartMatch à n'importe quelle application.

## Personnalisation

Vous pouvez personnaliser le comportement de SmartMatch de plusieurs façons :

- **Pondération des critères** : Modifiez les poids attribués à chaque critère de matching dans la configuration du SmartMatcher.
- **Adaptation du format de données** : Personnalisez la transformation des données dans le ParsingAdapter pour s'adapter à vos formats spécifiques.
- **Ajout de critères** : Étendez le SmartMatcher pour prendre en compte des critères supplémentaires.

## Limitations actuelles

- L'analyse des emplacements géographiques pourrait être améliorée en intégrant Google Maps API pour une meilleure gestion des distances.
- L'analyse sémantique des descriptions de postes et des expériences pourrait être approfondie avec des modèles NLP plus avancés.

## Roadmap

- [ ] Intégrer Google Maps API pour l'analyse de localisation
- [ ] Ajouter des modèles NLP avancés pour l'analyse sémantique
- [ ] Implémenter le support multilingue
- [ ] Ajouter des statistiques et un tableau de bord d'analyse
- [ ] Développer des fonctionnalités de suggestion pour améliorer les CV et les fiches de poste
