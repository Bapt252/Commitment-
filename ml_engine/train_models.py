import os
import json
import argparse
from data_collection import setup_database, get_training_data
from ner_model import convert_to_spacy_format, create_ner_model
from skills_classifier import SkillsClassifier

def train_all_models(data_limit=1000, ner_iterations=100):
    """Entraîne tous les modèles avec les données disponibles"""
    print("Initialisation de la base de données...")
    engine = setup_database()
    
    print(f"Récupération des données d'entraînement (limite: {data_limit})...")
    training_data = get_training_data(engine, limit=data_limit)
    
    if not training_data:
        print("Aucune donnée d'entraînement disponible.")
        print("Veuillez d'abord alimenter la base de données avec des fiches de poste annotées.")
        return
    
    print(f"{len(training_data)} exemples d'entraînement trouvés.")
    
    # Créer le répertoire des modèles s'il n'existe pas
    os.makedirs("./models", exist_ok=True)
    
    # Entraîner le modèle NER
    print("\nEntraînement du modèle NER...")
    ner_training_data = convert_to_spacy_format(training_data)
    create_ner_model(ner_training_data, n_iter=ner_iterations)
    
    # Entraîner le classificateur de compétences
    print("\nEntraînement du classificateur de compétences...")
    classifier = SkillsClassifier()
    results = classifier.train(training_data)
    classifier.save_model()
    
    print("\nTous les modèles ont été entraînés avec succès !")
    print("Stats du classificateur de compétences:")
    print(f"  - Nombre de compétences reconnues: {results['num_skills']}")
    print(f"  - F1-score macro: {results['macro_f1']:.4f}")
    print(f"  - F1-score micro: {results['micro_f1']:.4f}")

def setup_sample_data():
    """Crée des données d'exemple pour les tests"""
    print("Initialisation de la base de données d'exemple...")
    engine = setup_database()
    
    print("Chargement des données d'exemple...")
    with open("./sample_data/job_postings.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    from data_collection import store_job_posting, store_annotation
    
    for item in sample_data:
        job_id = store_job_posting(engine, item["raw_text"], source="sample_data")
        
        annotation = {
            "job_title": item["job_title"],
            "experience": item["experience"],
            "skills": item["skills"],
            "education": item["education"],
            "contract": item["contract"],
            "location": item["location"],
            "salary": item["salary"],
            "confidence_scores": {
                "job_title": 0.95,
                "experience": 0.9,
                "skills": 0.9,
                "education": 0.9,
                "contract": 0.95,
                "location": 0.9,
                "salary": 0.85
            }
        }
        
        annotation_id = store_annotation(engine, job_id, annotation, source="manual", annotator_id="system")
    
    print(f"{len(sample_data)} fiches de poste d'exemple ajoutées à la base de données.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement des modèles ML pour l'analyse de fiches de poste")
    parser.add_argument("--setup-sample", action="store_true", help="Initialiser des données d'exemple")
    parser.add_argument("--limit", type=int, default=1000, help="Nombre maximum d'exemples d'entraînement")
    parser.add_argument("--ner-iter", type=int, default=100, help="Nombre d'itérations pour le modèle NER")
    
    args = parser.parse_args()
    
    if args.setup_sample:
        setup_sample_data()
    
    train_all_models(data_limit=args.limit, ner_iterations=args.ner_iter)