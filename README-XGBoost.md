# Implémentation du système de matching XGBoost

Ce module ajoute un système de matching avancé basé sur XGBoost pour améliorer la précision des recommandations entre candidats et entreprises.

## Fonctionnalités

- Matching avancé avec XGBoost, un algorithme d'apprentissage automatique performant
- Extraction automatique de caractéristiques (features) à partir des profils
- Génération de recommandations plus précises et personnalisées
- Comparaison avec l'algorithme de matching traditionnel

## Installation

1. Assurez-vous d'avoir installé toutes les dépendances requises :

```bash
pip install -r backend/requirements.txt
```

2. Générez et entraînez le modèle XGBoost :

```bash
cd backend
python train_xgboost_model.py --samples 2000
```

## Utilisation

### Backend

Le système de matching XGBoost est disponible via l'API REST :

- `GET /api/v1/companies/match-xgboost/{company_id}/candidates` : Obtenir des recommandations de candidats pour une entreprise en utilisant XGBoost

### Frontend

Pour utiliser le système de matching XGBoost dans le frontend :

1. Incluez les fichiers JavaScript et CSS dans votre HTML :

```html
<link rel="stylesheet" href="../static/styles/xgboost-matching.css">
<script src="../static/scripts/xgboost_matching.js"></script>
```

2. Utilisez l'API JavaScript pour obtenir les recommandations :

```javascript
// Récupérer les recommandations XGBoost
const companyId = '123'; // ID de l'entreprise
const options = { limit: 10, minScore: 60 };

try {
  const results = await window.xgboostMatching.getXGBoostMatchingResults(companyId, options);
  
  // Afficher les résultats dans un conteneur
  const container = document.getElementById('matching-results');
  window.xgboostMatching.displayXGBoostResults(results, container);
  
  // Comparer avec l'algorithme traditionnel (optionnel)
  const comparison = await window.xgboostMatching.compareMatchingAlgorithms(companyId);
  console.log('Comparaison des algorithmes :', comparison);
} catch (error) {
  console.error('Erreur lors du matching :', error);
}
```

## Architecture

Le système de matching XGBoost est composé de plusieurs composants :

1. **XGBoostMatchingEngine** (`backend/app/nlp/xgboost_matching.py`) : Moteur principal qui gère l'extraction de caractéristiques, l'entraînement du modèle et les prédictions.

2. **API Endpoint** (`backend/app/api/endpoints/companies.py`) : Point d'entrée REST pour les requêtes de matching.

3. **Script d'entraînement** (`backend/train_xgboost_model.py`) : Outil pour générer des données synthétiques et entraîner le modèle.

4. **Client JavaScript** (`static/scripts/xgboost_matching.js`) : Interface pour interagir avec l'API depuis le frontend.

5. **Styles CSS** (`static/styles/xgboost-matching.css`) : Styles pour l'affichage des résultats.

## Caractéristiques utilisées

Le modèle XGBoost utilise les caractéristiques suivantes pour effectuer le matching :

- **Compétences** : Correspondance entre les compétences du candidat et les technologies de l'entreprise
- **Expérience** : Adéquation entre l'expérience du candidat et les exigences de l'entreprise
- **Valeurs** : Alignement entre les valeurs personnelles du candidat et la culture d'entreprise
- **Environnement de travail** : Compatibilité des préférences de travail (remote, hybrid, office)
- **Formation** : Correspondance du niveau d'éducation

## Analyse comparative

Le système permet de comparer les résultats de l'algorithme traditionnel basé sur des règles avec le nouveau modèle XGBoost. Cette comparaison aide à comprendre les différences et à évaluer les améliorations apportées par l'apprentissage automatique.