# Nexten SmartMatch

Nexten SmartMatch est un système de matching bidirectionnel avancé qui permet de mettre en relation des candidats et des entreprises en fonction de critères multiples, incluant la compatibilité des compétences, la localisation, les préférences de travail à distance, l'expérience et les attentes salariales.

## Caractéristiques principales

- **Matching bidirectionnel** : Prend en compte à la fois les besoins des entreprises et les préférences des candidats
- **Analyse sémantique des compétences** : Va au-delà de la simple correspondance de mots-clés pour comprendre la similarité entre les compétences
- **Intégration Google Maps** : Calcule les temps de trajet réels entre les localisations des candidats et des entreprises
- **Gestion des préférences de travail à distance** : Prend en compte les politiques de télétravail des entreprises et les préférences des candidats
- **Génération d'insights** : Fournit des analyses détaillées sur les résultats de matching

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Une clé API Google Maps (pour le calcul des temps de trajet)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration de la clé API Google Maps

Deux options s'offrent à vous :

1. Configuration par variable d'environnement :

```bash
export GOOGLE_MAPS_API_KEY="votre_clé_api_google_maps"
```

2. Configuration directe dans le code :

```python
from app.compat import GoogleMapsClient

# Initialiser le client avec votre clé API
maps_client = GoogleMapsClient(api_key="votre_clé_api_google_maps")
```

## Utilisation

### Utilisation simple

```python
from app.smartmatch import SmartMatchEngine
from app.data_loader import DataLoader

# Charger les données
data_loader = DataLoader()
candidates = data_loader.load_candidates("chemin/vers/candidats.json")
companies = data_loader.load_companies("chemin/vers/entreprises.json")

# Initialiser le moteur de matching
engine = SmartMatchEngine()

# Exécuter le matching
matching_results = engine.match(candidates, companies)

# Afficher les résultats
for match in matching_results[:5]:  # Top 5 des meilleurs matchings
    print(f"Candidat {match['candidate_id']} - Entreprise {match['company_id']} - Score: {match['score']:.2f}")
```

### Utilisation avancée

```python
from app.smartmatch import SmartMatchEngine
from app.data_loader import DataLoader
from app.insight_generator import InsightGenerator

# Charger les données
data_loader = DataLoader()
candidates = data_loader.load_candidates("chemin/vers/candidats.json")
companies = data_loader.load_companies("chemin/vers/entreprises.json")

# Initialiser le moteur de matching avec des pondérations personnalisées
engine = SmartMatchEngine()
engine.set_weights({
    "skills": 0.4,
    "location": 0.25,
    "remote_policy": 0.15,
    "experience": 0.1,
    "salary": 0.1
})

# Exécuter le matching
matching_results = engine.match(candidates, companies)

# Générer des insights
insight_generator = InsightGenerator()
insights = insight_generator.generate_insights(matching_results)

# Afficher les insights
for insight in insights:
    print(f"[{insight['type']}] {insight['message']}")

# Exporter les résultats
data_loader.save_results(matching_results, "resultats_matching.json")
```

### Utilisation en ligne de commande

Vous pouvez également utiliser l'outil en ligne de commande :

```bash
python main.py --candidates chemin/vers/candidats.json --companies chemin/vers/entreprises.json --output resultats.json
```

Options disponibles :
- `--candidates` : Chemin vers le fichier de données des candidats (JSON ou CSV)
- `--companies` : Chemin vers le fichier de données des entreprises (JSON ou CSV)
- `--output` : Chemin du fichier de sortie pour les résultats (JSON ou CSV)
- `--weights` : Pondérations personnalisées au format JSON (ex: '{"skills": 0.4, "location": 0.3, ...}')
- `--threshold` : Seuil minimum pour considérer un match (défaut: 0.6)
- `--google-maps-key` : Clé API Google Maps pour le calcul des temps de trajet
- `--verbose` : Afficher des informations détaillées pendant l'exécution

## Format des données

### Format des données des candidats

```json
[
  {
    "id": "cand001",
    "name": "Jean Dupont",
    "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
    "experience": 4,
    "location": "Paris, France",
    "remote_preference": "hybrid",
    "salary_expectation": 65000
  },
  // Autres candidats...
]
```

### Format des données des entreprises

```json
[
  {
    "id": "comp001",
    "name": "TechSolutions SAS",
    "required_skills": ["Python", "JavaScript", "React", "Node.js"],
    "location": "Paris, France",
    "remote_policy": "hybrid",
    "salary_range": {"min": 55000, "max": 80000},
    "required_experience": 3
  },
  // Autres entreprises...
]
```

## Intégration au site web

Pour intégrer le système SmartMatch à un site web, vous pouvez utiliser l'API RESTful fournie. Voici un exemple simple d'intégration avec Flask :

```python
from flask import Flask, request, jsonify
from app.smartmatch import SmartMatchEngine

app = Flask(__name__)

@app.route('/api/match', methods=['POST'])
def match():
    data = request.json
    candidates = data.get('candidates', [])
    companies = data.get('companies', [])
    
    engine = SmartMatchEngine()
    matching_results = engine.match(candidates, companies)
    
    return jsonify({
        'matches': matching_results
    })

if __name__ == '__main__':
    app.run(debug=True)
```

## Tests

Pour exécuter les tests unitaires :

```bash
python test_smartmatch.py
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.