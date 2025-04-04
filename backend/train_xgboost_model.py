import os
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from app.nlp.xgboost_matching import get_xgboost_matching_engine
from app.nlp.matching_engine import get_matching_engine

def generate_synthetic_data(num_samples=1000, seed=42):
    """
    Génère des données synthétiques pour l'entraînement du modèle XGBoost
    """
    np.random.seed(seed)
    
    # Liste de compétences techniques
    skills_list = [
        "Python", "JavaScript", "Java", "C#", "C++", "SQL", "PHP", "Ruby", "Swift", "Kotlin", 
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "TensorFlow", 
        "PyTorch", "Scikit-learn", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Git", 
        "Agile", "Scrum", "CI/CD", "DevOps"
    ]
    
    # Liste de valeurs d'entreprise
    values_list = [
        "innovation", "collaboration", "excellence", "intégrité", "responsabilité", 
        "diversité", "inclusion", "développement_durable", "qualité", "service_client", 
        "créativité", "performance"
    ]
    
    # Modes de travail
    work_modes = ["remote", "hybrid", "office"]
    
    # Lieux
    locations = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Toulouse", "Nantes", "Strasbourg"]
    
    # Génération de données
    data = []
    
    for i in range(num_samples):
        # Génération aléatoire de profils candidat et entreprise
        
        # Compétences du candidat (5-10 compétences aléatoires)
        candidate_num_skills = np.random.randint(5, 11)
        candidate_skills = np.random.choice(skills_list, candidate_num_skills, replace=False).tolist()
        
        # Compétences de l'entreprise (3-8 compétences aléatoires)
        company_num_skills = np.random.randint(3, 9)
        company_skills = np.random.choice(skills_list, company_num_skills, replace=False).tolist()
        
        # Expérience du candidat (2-10 ans)
        candidate_experience = np.random.randint(2, 11)
        
        # Expérience requise par l'entreprise (1-8 ans)
        company_required_experience = np.random.randint(1, 9)
        
        # Valeurs du candidat (3-5 valeurs aléatoires)
        candidate_num_values = np.random.randint(3, 6)
        candidate_values = np.random.choice(values_list, candidate_num_values, replace=False).tolist()
        
        # Valeurs de l'entreprise (3-5 valeurs aléatoires)
        company_num_values = np.random.randint(3, 6)
        company_values = np.random.choice(values_list, company_num_values, replace=False).tolist()
        
        # Mode de travail
        candidate_work_mode = np.random.choice(work_modes)
        company_work_mode = np.random.choice(work_modes)
        
        # Localisation
        candidate_location = np.random.choice(locations)
        company_location = np.random.choice(locations)
        
        # Niveau d'éducation (1-5)
        candidate_education = np.random.randint(1, 6)
        company_education = np.random.randint(1, 6)
        
        # Créer les structures pour le matching engine
        candidate_profile = {
            "competences": candidate_skills,
            "experience": [{"period": f"{2024-candidate_experience} - 2024", "title": "Poste"}],
            "values": {"detected_values": {value: np.random.random() for value in candidate_values}},
            "work_preferences": {"preferred_work_mode": candidate_work_mode, "preferred_location": candidate_location},
            "formation": {"level": candidate_education}
        }
        
        company_profile = {
            "technologies": company_skills,
            "extracted_data": {
                "experience": f"{company_required_experience} ans",
                "values": {"detected_values": {value: np.random.random() for value in company_values}},
                "work_environment": {"work_mode": [company_work_mode], "locations": [company_location]},
                "education": {"level": company_education}
            }
        }
        
        # Calculer les scores de matching
        matching_engine = get_matching_engine()
        match_result = matching_engine.calculate_match_score(candidate_profile, company_profile)
        
        # Extraire les features pour le modèle XGBoost
        xgboost_engine = get_xgboost_matching_engine()
        match_features = xgboost_engine.extract_match_features(candidate_profile, company_profile)
        
        # Déterminer si c'est un match (basé sur un seuil)
        # Un score de 65+ est considéré comme un match
        is_match = 1 if match_result["global_score"] >= 65 else 0
        match_features["is_match"] = is_match
        
        # Ajouter aux données
        data.append(match_features)
    
    return data

def train_model(data_path=None, num_samples=1000):
    """
    Entraîne le modèle XGBoost avec des données réelles ou synthétiques
    """
    print("Initialisation de l'entraînement du modèle XGBoost...")
    
    # Obtenir l'instance du moteur XGBoost
    xgboost_engine = get_xgboost_matching_engine()
    
    # Charger les données d'entraînement
    if data_path and os.path.exists(data_path):
        print(f"Chargement des données depuis {data_path}...")
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
            training_data = df.to_dict('records')
        elif data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
        else:
            print("Format de fichier non supporté. Génération de données synthétiques à la place.")
            training_data = generate_synthetic_data(num_samples)
    else:
        print(f"Génération de {num_samples} exemples de données synthétiques pour l'entraînement...")
        training_data = generate_synthetic_data(num_samples)
    
    print(f"Entraînement avec {len(training_data)} exemples...")
    
    # Entraîner le modèle
    metrics = xgboost_engine.train(training_data)
    
    print("\nEntraînement terminé!")
    print("Métriques d'évaluation:")
    print(f"  - Précision: {metrics['accuracy']:.4f}")
    print(f"  - Précision (precision): {metrics['precision']:.4f}")
    print(f"  - Rappel (recall): {metrics['recall']:.4f}")
    print(f"  - F1-score: {metrics['f1']:.4f}")
    
    # Sauvegarder les données d'entraînement pour référence
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    training_file = data_dir / "xgboost_training_data.json"
    with open(training_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Données d'entraînement sauvegardées dans {training_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement du modèle XGBoost pour le matching")
    parser.add_argument("--data", type=str, help="Chemin vers le fichier de données d'entraînement (CSV ou JSON)")
    parser.add_argument("--samples", type=int, default=1000, help="Nombre d'exemples à générer si aucun fichier n'est fourni")
    
    args = parser.parse_args()
    
    train_model(args.data, args.samples)