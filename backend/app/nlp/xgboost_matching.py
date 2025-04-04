import numpy as np
import pandas as pd
import xgboost as xgb
import pickle
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path
import json
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class XGBoostMatchingEngine:
    """
    Moteur de matching basé sur XGBoost pour générer des recommandations
    entre candidats et entreprises.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chargement des configurations
        self.load_config()
        
        # Initialisation des encodeurs
        self.label_encoders = {}
        self.one_hot_encoders = {}
        
        # Attributs pour le modèle
        self.model = None
        self.feature_names = None
        
        # Charger le modèle s'il existe
        self.load_model()
    
    def load_config(self):
        """
        Charge les paramètres de configuration pour le modèle XGBoost
        """
        try:
            config_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_config.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.model_config = config.get("model_params", {})
                    self.feature_weights = config.get("feature_weights", {})
            else:
                # Configuration par défaut
                self.model_config = {
                    "objective": "binary:logistic",
                    "eval_metric": "logloss",
                    "eta": 0.1,
                    "max_depth": 6,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "min_child_weight": 1,
                    "scale_pos_weight": 1
                }
                
                # Pondération des features
                self.feature_weights = {
                    "skills_match": 3.5,
                    "experience_match": 2.0,
                    "values_match": 2.0,
                    "work_environment_match": 1.5,
                    "education_match": 1.0
                }
                
                # Créer le répertoire data s'il n'existe pas
                data_dir = Path(__file__).resolve().parent.parent.parent / "data"
                data_dir.mkdir(exist_ok=True)
                
                # Sauvegarder la configuration par défaut
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "model_params": self.model_config,
                        "feature_weights": self.feature_weights
                    }, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {e}")
            # Utiliser des valeurs par défaut
            self.model_config = {
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "eta": 0.1,
                "max_depth": 6
            }
            self.feature_weights = {
                "skills_match": 3.5,
                "experience_match": 2.0,
                "values_match": 2.0,
                "work_environment_match": 1.5,
                "education_match": 1.0
            }
    
    def load_model(self):
        """
        Charge le modèle XGBoost pré-entraîné s'il existe
        """
        model_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_model.pkl"
        encoders_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_encoders.pkl"
        features_path = Path(__file__).resolve().parent.parent.parent / "data" / "xgboost_features.json"
        
        try:
            if model_path.exists() and encoders_path.exists() and features_path.exists():
                # Charger le modèle
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                # Charger les encodeurs
                with open(encoders_path, 'rb') as f:
                    encoders_data = pickle.load(f)
                    self.label_encoders = encoders_data.get('label_encoders', {})
                    self.one_hot_encoders = encoders_data.get('one_hot_encoders', {})
                
                # Charger les noms des features
                with open(features_path, 'r', encoding='utf-8') as f:
                    self.feature_names = json.load(f)
                
                self.logger.info("Modèle XGBoost chargé avec succès")
            else:
                self.logger.info("Aucun modèle XGBoost pré-entraîné trouvé")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du modèle: {e}")
    
    def save_model(self):
        """
        Sauvegarde le modèle XGBoost et les encodeurs
        """
        try:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            model_path = data_dir / "xgboost_model.pkl"
            encoders_path = data_dir / "xgboost_encoders.pkl"
            features_path = data_dir / "xgboost_features.json"
            
            # Sauvegarder le modèle
            if self.model:
                with open(model_path, 'wb') as f:
                    pickle.dump(self.model, f)
            
            # Sauvegarder les encodeurs
            with open(encoders_path, 'wb') as f:
                encoders_data = {
                    'label_encoders': self.label_encoders,
                    'one_hot_encoders': self.one_hot_encoders
                }
                pickle.dump(encoders_data, f)
            
            # Sauvegarder les noms des features
            if self.feature_names:
                with open(features_path, 'w', encoding='utf-8') as f:
                    json.dump(self.feature_names, f, indent=2)
            
            self.logger.info("Modèle XGBoost sauvegardé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du modèle: {e}")
    
    def preprocess_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prétraite les données pour l'entraînement ou la prédiction
        
        Args:
            data: Liste de dictionnaires contenant les données de matching
            
        Returns:
            DataFrame pandas contenant les features prétraitées
        """
        try:
            # Convertir en DataFrame
            df = pd.DataFrame(data)
            
            # Traiter les colonnes catégorielles
            for col in df.select_dtypes(include=['object']).columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].fillna('Unknown'))
                else:
                    # Pour les nouvelles valeurs non vues lors de l'entraînement
                    known_categories = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(lambda x: x if x in known_categories else 'Unknown')
                    df[col] = self.label_encoders[col].transform(df[col].fillna('Unknown'))
            
            # Ajouter les features basées sur les matching scores
            for feature in ['skills_match', 'experience_match', 'values_match', 
                           'work_environment_match', 'education_match']:
                if feature in df.columns:
                    # Appliquer la pondération configurée
                    weight = self.feature_weights.get(feature, 1.0)
                    df[f'{feature}_weighted'] = df[feature] * weight
            
            # Garder une trace des noms de colonnes pour la prédiction
            self.feature_names = list(df.columns)
            
            return df
        
        except Exception as e:
            self.logger.error(f"Erreur lors du prétraitement des données: {e}")
            raise
    
    def train(self, training_data: List[Dict[str, Any]], target_column: str = 'is_match') -> Dict[str, Any]:
        """
        Entraîne le modèle XGBoost avec les données fournies
        
        Args:
            training_data: Données d'entraînement avec les paires candidat-entreprise
            target_column: Nom de la colonne contenant la cible (1 pour match, 0 pour non-match)
            
        Returns:
            Dict: Métriques d'évaluation du modèle
        """
        try:
            # Prétraiter les données
            df = self.preprocess_data(training_data)
            
            # Diviser en features et target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Diviser en ensembles d'entraînement et de test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Créer les matrices DMatrix
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dtest = xgb.DMatrix(X_test, label=y_test)
            
            # Configurer les paramètres
            params = self.model_config.copy()
            
            # Entraîner le modèle
            evallist = [(dtrain, 'train'), (dtest, 'eval')]
            self.model = xgb.train(params, dtrain, num_boost_round=100, 
                                  evals=evallist, early_stopping_rounds=10)
            
            # Évaluer le modèle
            y_pred = self.model.predict(dtest)
            y_pred_binary = (y_pred > 0.5).astype(int)
            
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred_binary),
                'precision': precision_score(y_test, y_pred_binary),
                'recall': recall_score(y_test, y_pred_binary),
                'f1': f1_score(y_test, y_pred_binary)
            }
            
            # Sauvegarder le modèle
            self.save_model()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'entraînement du modèle: {e}")
            raise
    
    def predict_match(self, candidate: Dict[str, Any], company: Dict[str, Any]) -> float:
        """
        Prédit le score de matching entre un candidat et une entreprise
        
        Args:
            candidate: Profil du candidat
            company: Profil de l'entreprise
            
        Returns:
            float: Score de matching entre 0 et 100
        """
        try:
            if not self.model:
                self.logger.warning("Aucun modèle XGBoost n'a été chargé, utilisation du matching basé sur les règles")
                # Utiliser le matching engine traditionnel
                from app.nlp.matching_engine import get_matching_engine
                matching_engine = get_matching_engine()
                match_result = matching_engine.calculate_match_score(candidate, company)
                return match_result["global_score"]
            
            # Extraire les features pour ce candidat et cette entreprise
            features = self.extract_match_features(candidate, company)
            
            # Prétraiter les features
            features_df = self.preprocess_data([features])
            
            # Assurer que toutes les colonnes requises sont présentes
            if self.feature_names:
                missing_cols = set(self.feature_names) - set(features_df.columns)
                for col in missing_cols:
                    features_df[col] = 0
                
                # Ordonner les colonnes selon le modèle d'entraînement
                features_df = features_df[self.feature_names]
            
            # Créer la matrice DMatrix
            dfeatures = xgb.DMatrix(features_df)
            
            # Prédire le score
            prediction = self.model.predict(dfeatures)[0]
            
            # Convertir en pourcentage
            match_score = prediction * 100
            
            return float(match_score)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prédiction du matching: {e}")
            # Utiliser un fallback basé sur les règles en cas d'erreur
            return self.calculate_rule_based_score(candidate, company)
    
    def extract_match_features(self, candidate: Dict[str, Any], company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les features pertinentes pour le matching entre un candidat et une entreprise
        
        Args:
            candidate: Profil du candidat
            company: Profil de l'entreprise
            
        Returns:
            Dict: Features pour le modèle XGBoost
        """
        # Extraire les caractéristiques du candidat
        candidate_skills = candidate.get("competences", [])
        candidate_experience = candidate.get("experience", [])
        candidate_values = candidate.get("values", {})
        candidate_preferences = candidate.get("work_preferences", {})
        candidate_education = candidate.get("formation", {})
        
        # Extraire les caractéristiques de l'entreprise
        company_skills = company.get("technologies", [])
        company_experience = company.get("extracted_data", {}).get("experience", "")
        company_values = company.get("extracted_data", {}).get("values", {})
        company_environment = company.get("extracted_data", {}).get("work_environment", {})
        company_education = company.get("extracted_data", {}).get("education", {})
        
        # Calculer les scores de base pour chaque catégorie (utiliser notre logique de matching existante)
        from app.nlp.matching_engine import get_matching_engine
        traditional_engine = get_matching_engine()
        
        # Scores par catégorie
        skills_match = traditional_engine.calculate_skills_match(candidate_skills, company_skills)
        experience_match = traditional_engine.calculate_experience_match(candidate_experience, company_experience)
        values_match = traditional_engine.calculate_values_match(candidate_values, company_values)
        environment_match = traditional_engine.calculate_environment_match(candidate_preferences, company_environment)
        education_match = traditional_engine.calculate_education_match(candidate_education, company_education)
        
        # Features agrégées
        features = {
            # Scores de base
            "skills_match": skills_match,
            "experience_match": experience_match,
            "values_match": values_match,
            "work_environment_match": environment_match,
            "education_match": education_match,
            
            # Caractéristiques du candidat
            "candidate_num_skills": len(candidate_skills),
            "candidate_years_experience": self.extract_years_experience(candidate_experience),
            "candidate_education_level": self.extract_education_level(candidate_education),
            
            # Caractéristiques de l'entreprise
            "company_num_skills": len(company_skills),
            "company_required_experience": self.extract_required_experience(company_experience),
            
            # Caractéristiques d'interaction
            "skills_overlap": len(set(s.lower() for s in candidate_skills).intersection(
                set(s.lower() for s in company_skills))) if candidate_skills and company_skills else 0,
            
            # Indiquer si c'est un match (pour l'entraînement)
            "is_match": 0  # À remplir lors de l'entraînement avec des données étiquetées
        }
        
        return features
    
    def extract_years_experience(self, experience_data) -> int:
        """
        Extrait le nombre total d'années d'expérience du candidat
        """
        if not experience_data:
            return 0
        
        total_years = 0
        
        # Si c'est une liste d'expériences
        if isinstance(experience_data, list):
            import re
            
            for exp in experience_data:
                if isinstance(exp, dict) and "period" in exp:
                    period = exp["period"]
                    # Extraire les années avec regex
                    matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|présent|present|actuel|current)', period)
                    if matches:
                        start_year = int(matches[0][0])
                        if any(x in matches[0][1].lower() for x in ["présent", "present", "actuel", "current"]):
                            import datetime
                            end_year = datetime.datetime.now().year
                        else:
                            end_year = int(matches[0][1])
                        
                        total_years += (end_year - start_year)
        
        # Si on n'a rien trouvé mais qu'on a des expériences, approximation
        if total_years == 0 and len(experience_data) > 0:
            total_years = len(experience_data) * 2
        
        return total_years
    
    def extract_required_experience(self, experience_text) -> int:
        """
        Extrait le nombre d'années d'expérience requis par l'entreprise
        """
        if not experience_text:
            return 0
        
        import re
        
        # Patterns pour l'extraction des années d'expérience
        matches = re.findall(r'(\d+)[\\s\\-+]*ans?|(\d+)[\\s\\-+]*year|(\d+)[\\s\\-+]*année', experience_text)
        
        # Flatten les tuples et prendre la première valeur non vide
        flat_matches = [int(val) for match in matches for val in match if val]
        
        if flat_matches:
            return flat_matches[0]
        
        # Si on n'a pas trouvé de nombre explicite
        if "junior" in experience_text.lower() or "débutant" in experience_text.lower():
            return 1
        elif "confirmé" in experience_text.lower() or "intermédiaire" in experience_text.lower():
            return 3
        elif "senior" in experience_text.lower() or "expert" in experience_text.lower():
            return 5
        
        return 2  # Valeur par défaut
    
    def extract_education_level(self, education_data) -> int:
        """
        Extrait le niveau d'éducation et le convertit en valeur numérique
        """
        education_levels = {
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5
        }
        
        if not education_data:
            return 3  # Valeur moyenne par défaut
        
        from app.nlp.matching_engine import get_matching_engine
        matching_engine = get_matching_engine()
        education_level = matching_engine._extract_education_level(education_data)
        
        if education_level:
            return education_levels.get(education_level, 3)
        
        return 3  # Valeur moyenne par défaut
    
    def calculate_rule_based_score(self, candidate: Dict[str, Any], company: Dict[str, Any]) -> float:
        """
        Calcule un score de matching basé sur des règles, utilisé comme fallback
        
        Args:
            candidate: Profil du candidat
            company: Profil de l'entreprise
            
        Returns:
            float: Score de matching entre 0 et 100
        """
        # Utiliser le matching engine traditionnel
        from app.nlp.matching_engine import get_matching_engine
        matching_engine = get_matching_engine()
        match_result = matching_engine.calculate_match_score(candidate, company)
        return match_result["global_score"]
    
    def generate_candidate_recommendations(self, 
                                         company_profile: Dict[str, Any],
                                         candidate_profiles: List[Dict[str, Any]], 
                                         limit: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations de candidats pour une entreprise en utilisant XGBoost
        
        Args:
            company_profile: Profil de l'entreprise
            candidate_profiles: Liste des profils de candidats
            limit: Nombre maximum de recommandations à retourner
            
        Returns:
            List: Candidats recommandés avec scores de matching
        """
        try:
            recommendations = []
            
            for candidate in candidate_profiles:
                # Calcul du score de matching avec XGBoost
                match_score = self.predict_match(candidate, company_profile)
                
                # Également calculer les scores par catégorie pour l'explicabilité
                # Utiliser le matching engine traditionnel pour cela
                from app.nlp.matching_engine import get_matching_engine
                traditional_engine = get_matching_engine()
                category_scores = traditional_engine.calculate_match_score(
                    candidate, company_profile)["category_scores"]
                
                # Ajouter à la liste de recommandations
                recommendations.append({
                    "candidate_id": candidate.get("id", "unknown"),
                    "candidate_name": candidate.get("name", "Candidat sans nom"),
                    "match_score": match_score,
                    "category_scores": category_scores,
                    "title": candidate.get("titre", "Titre non spécifié")
                })
            
            # Trier par score de matching
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Limiter le nombre de résultats
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des recommandations de candidats: {e}")
            
            # En cas d'erreur, utiliser le matching engine traditionnel
            from app.nlp.matching_engine import get_matching_engine
            traditional_engine = get_matching_engine()
            return traditional_engine.generate_candidate_recommendations(
                company_profile, candidate_profiles, limit)

# Instance singleton du moteur de matching XGBoost
_xgboost_matching_engine = None

def get_xgboost_matching_engine():
    """
    Récupère l'instance unique du moteur de matching XGBoost
    
    Returns:
        XGBoostMatchingEngine: Instance du moteur de matching XGBoost
    """
    global _xgboost_matching_engine
    if _xgboost_matching_engine is None:
        _xgboost_matching_engine = XGBoostMatchingEngine()
    return _xgboost_matching_engine