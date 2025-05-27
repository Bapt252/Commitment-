"""
Système d'apprentissage pour SuperSmartMatch Unifié
Module optionnel pour l'apprentissage continu
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MatchingRecord:
    """Enregistrement d'un matching pour l'apprentissage"""
    match_id: str
    cv_features: Dict
    job_features: Dict
    questionnaire_features: Dict
    predicted_score: float
    actual_feedback: Optional[float] = None
    timestamp: datetime = None
    user_satisfaction: Optional[int] = None  # 1-5
    hired: Optional[bool] = None

class LearningSystem:
    """
    Système d'apprentissage continu pour améliorer les performances
    du matching au fil du temps
    """
    
    def __init__(self, data_dir: str = "models/learning_data"):
        if not ML_AVAILABLE:
            raise ImportError("Dépendances ML non disponibles. Installez : scikit-learn, pandas, numpy, joblib")
        
        self.data_dir = data_dir
        self.model_path = os.path.join(data_dir, "matching_model.joblib")
        self.records_path = os.path.join(data_dir, "matching_records.json")
        
        # Créer le dossier si nécessaire
        os.makedirs(data_dir, exist_ok=True)
        
        # Modèle de machine learning
        self.model = None
        self.feature_names = []
        self.model_metadata = {}
        
        # Données d'entraînement
        self.training_records = []
        
        # Configuration d'apprentissage
        self.min_records_for_training = 50
        self.retrain_threshold_days = 7
        self.performance_threshold = 0.7
        
        self._load_existing_data()
        self._load_model()
    
    def _load_existing_data(self):
        """Charge les données d'entraînement existantes"""
        try:
            if os.path.exists(self.records_path):
                with open(self.records_path, 'r') as f:
                    records_data = json.load(f)
                
                self.training_records = []
                for record_data in records_data:
                    record = MatchingRecord(
                        match_id=record_data['match_id'],
                        cv_features=record_data['cv_features'],
                        job_features=record_data['job_features'],
                        questionnaire_features=record_data['questionnaire_features'],
                        predicted_score=record_data['predicted_score'],
                        actual_feedback=record_data.get('actual_feedback'),
                        timestamp=datetime.fromisoformat(record_data['timestamp']),
                        user_satisfaction=record_data.get('user_satisfaction'),
                        hired=record_data.get('hired')
                    )
                    self.training_records.append(record)
                
                logger.info(f"Chargé {len(self.training_records)} enregistrements d'apprentissage")
            
        except Exception as e:
            logger.error(f"Erreur chargement données: {e}")
            self.training_records = []
    
    def _save_records(self):
        """Sauvegarde les enregistrements d'apprentissage"""
        try:
            records_data = []
            for record in self.training_records:
                record_data = {
                    'match_id': record.match_id,
                    'cv_features': record.cv_features,
                    'job_features': record.job_features,
                    'questionnaire_features': record.questionnaire_features,
                    'predicted_score': record.predicted_score,
                    'actual_feedback': record.actual_feedback,
                    'timestamp': record.timestamp.isoformat(),
                    'user_satisfaction': record.user_satisfaction,
                    'hired': record.hired
                }
                records_data.append(record_data)
            
            with open(self.records_path, 'w') as f:
                json.dump(records_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde données: {e}")
    
    def _load_model(self):
        """Charge le modèle ML existant"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.model_metadata = model_data['metadata']
                logger.info(f"Modèle chargé: {self.model_metadata.get('version', 'inconnue')}")
            else:
                logger.info("Aucun modèle existant trouvé")
                
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            self.model = None
    
    def _save_model(self):
        """Sauvegarde le modèle ML"""
        try:
            if self.model:
                model_data = {
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'metadata': self.model_metadata
                }
                joblib.dump(model_data, self.model_path)
                logger.info("Modèle sauvegardé")
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde modèle: {e}")
    
    def record_match(self, parsed_data, predicted_score: float, match_id: str):
        """Enregistre un matching pour l'apprentissage"""
        try:
            # Extraction des features
            cv_features = self._extract_cv_features(parsed_data.cv_data)
            job_features = self._extract_job_features(parsed_data.job_data)
            questionnaire_features = self._extract_questionnaire_features(parsed_data.questionnaire_data)
            
            # Création de l'enregistrement
            record = MatchingRecord(
                match_id=match_id,
                cv_features=cv_features,
                job_features=job_features,
                questionnaire_features=questionnaire_features,
                predicted_score=predicted_score,
                timestamp=datetime.now()
            )
            
            self.training_records.append(record)
            self._save_records()
            
            logger.debug(f"Matching enregistré: {match_id}")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement matching: {e}")
    
    def process_feedback(self, match_id: str, feedback_data: Dict):
        """Traite le feedback utilisateur"""
        try:
            # Trouver l'enregistrement correspondant
            record = None
            for r in self.training_records:
                if r.match_id == match_id:
                    record = r
                    break
            
            if not record:
                logger.warning(f"Enregistrement {match_id} non trouvé")
                return
            
            # Mise à jour avec le feedback
            record.actual_feedback = feedback_data.get('rating', 0)  # 0-100
            record.user_satisfaction = feedback_data.get('satisfaction', 3)  # 1-5
            record.hired = feedback_data.get('hired', False)
            
            self._save_records()
            
            logger.info(f"Feedback traité pour {match_id}: {record.actual_feedback}")
            
            # Vérifier s'il faut réentraîner
            if self.should_retrain():
                self.retrain_models()
                
        except Exception as e:
            logger.error(f"Erreur traitement feedback: {e}")
    
    def _extract_cv_features(self, cv_data: Dict) -> Dict:
        """Extrait les features du CV"""
        if not cv_data:
            return {}
        
        return {
            'num_competences': len(cv_data.get('competences', [])),
            'experience_totale': cv_data.get('experience_totale', 0),
            'niveau_formation': cv_data.get('niveau_formation', 0),
            'has_localisation': bool(cv_data.get('localisation')),
            'text_length': len(cv_data.get('texte_complet', '')),
            'has_certifications': bool(cv_data.get('certifications')),
            'num_experiences': len(cv_data.get('experiences', [])),
            'parsing_confidence': cv_data.get('parsing_confidence', 0.5)
        }
    
    def _extract_job_features(self, job_data: Dict) -> Dict:
        """Extrait les features du job"""
        if not job_data:
            return {}
        
        return {
            'num_competences_requises': len(job_data.get('competences_requises', [])),
            'experience_requise': job_data.get('experience_requise', 0),
            'niveau_formation_requis': job_data.get('niveau_formation_requis', 0),
            'has_salaire': bool(job_data.get('salaire_max')),
            'salaire_max': job_data.get('salaire_max', 0),
            'has_localisation': bool(job_data.get('localisation')),
            'description_length': len(job_data.get('description', '')),
            'is_remote': 'remote' in job_data.get('modalite_travail', '').lower(),
            'parsing_confidence': job_data.get('parsing_confidence', 0.5)
        }
    
    def _extract_questionnaire_features(self, questionnaire_data: Dict) -> Dict:
        """Extrait les features du questionnaire"""
        if not questionnaire_data:
            return {
                'has_questionnaire': False,
                'motivation': 5,
                'disponibilite': 5,
                'mobilite': 5,
                'has_salary_expectation': False,
                'has_experience_description': False
            }
        
        return {
            'has_questionnaire': True,
            'motivation': questionnaire_data.get('motivation', 5),
            'disponibilite': questionnaire_data.get('disponibilite', 5),
            'mobilite': questionnaire_data.get('mobilite', 5),
            'salaire_souhaite': questionnaire_data.get('salaire_souhaite', 0),
            'has_salary_expectation': bool(questionnaire_data.get('salaire_souhaite')),
            'has_experience_description': bool(questionnaire_data.get('experience_specifique')),
            'has_career_goals': bool(questionnaire_data.get('objectifs_carriere'))
        }
    
    def _create_feature_vector(self, cv_features: Dict, job_features: Dict, questionnaire_features: Dict) -> np.ndarray:
        """Crée un vecteur de features pour le ML"""
        # Définir l'ordre des features
        if not self.feature_names:
            self.feature_names = [
                # CV features
                'cv_num_competences', 'cv_experience_totale', 'cv_niveau_formation',
                'cv_has_localisation', 'cv_text_length', 'cv_has_certifications',
                'cv_num_experiences', 'cv_parsing_confidence',
                
                # Job features
                'job_num_competences_requises', 'job_experience_requise', 'job_niveau_formation_requis',
                'job_has_salaire', 'job_salaire_max', 'job_has_localisation',
                'job_description_length', 'job_is_remote', 'job_parsing_confidence',
                
                # Questionnaire features
                'quest_has_questionnaire', 'quest_motivation', 'quest_disponibilite',
                'quest_mobilite', 'quest_salaire_souhaite', 'quest_has_salary_expectation',
                'quest_has_experience_description', 'quest_has_career_goals',
                
                # Derived features
                'competences_ratio', 'experience_ratio', 'formation_ratio', 'salary_ratio'
            ]
        
        # Construire le vecteur
        features = []
        
        # CV features
        features.extend([
            cv_features.get('num_competences', 0),
            cv_features.get('experience_totale', 0),
            cv_features.get('niveau_formation', 0),
            int(cv_features.get('has_localisation', False)),
            cv_features.get('text_length', 0),
            int(cv_features.get('has_certifications', False)),
            cv_features.get('num_experiences', 0),
            cv_features.get('parsing_confidence', 0.5)
        ])
        
        # Job features
        features.extend([
            job_features.get('num_competences_requises', 0),
            job_features.get('experience_requise', 0),
            job_features.get('niveau_formation_requis', 0),
            int(job_features.get('has_salaire', False)),
            job_features.get('salaire_max', 0),
            int(job_features.get('has_localisation', False)),
            job_features.get('description_length', 0),
            int(job_features.get('is_remote', False)),
            job_features.get('parsing_confidence', 0.5)
        ])
        
        # Questionnaire features
        features.extend([
            int(questionnaire_features.get('has_questionnaire', False)),
            questionnaire_features.get('motivation', 5),
            questionnaire_features.get('disponibilite', 5),
            questionnaire_features.get('mobilite', 5),
            questionnaire_features.get('salaire_souhaite', 0),
            int(questionnaire_features.get('has_salary_expectation', False)),
            int(questionnaire_features.get('has_experience_description', False)),
            int(questionnaire_features.get('has_career_goals', False))
        ])
        
        # Derived features
        cv_comp = cv_features.get('num_competences', 1)
        job_comp = job_features.get('num_competences_requises', 1)
        competences_ratio = min(cv_comp / job_comp, 2.0) if job_comp > 0 else 0
        
        cv_exp = cv_features.get('experience_totale', 0)
        job_exp = job_features.get('experience_requise', 1)
        experience_ratio = min(cv_exp / job_exp, 2.0) if job_exp > 0 else 0
        
        cv_form = cv_features.get('niveau_formation', 0)
        job_form = job_features.get('niveau_formation_requis', 1)
        formation_ratio = min(cv_form / job_form, 2.0) if job_form > 0 else 0
        
        cv_sal = questionnaire_features.get('salaire_souhaite', 0)
        job_sal = job_features.get('salaire_max', 1)
        salary_ratio = min(cv_sal / job_sal, 2.0) if job_sal > 0 and cv_sal > 0 else 1.0
        
        features.extend([competences_ratio, experience_ratio, formation_ratio, salary_ratio])
        
        return np.array(features)
    
    def should_retrain(self) -> bool:
        """Détermine s'il faut réentraîner le modèle"""
        # Vérifier le nombre d'enregistrements avec feedback
        records_with_feedback = [r for r in self.training_records if r.actual_feedback is not None]
        
        if len(records_with_feedback) < self.min_records_for_training:
            return False
        
        # Vérifier la date du dernier entraînement
        last_training = self.model_metadata.get('last_training')
        if last_training:
            last_training_date = datetime.fromisoformat(last_training)
            if (datetime.now() - last_training_date).days < self.retrain_threshold_days:
                return False
        
        # Vérifier les performances actuelles
        if self.model:
            current_performance = self._evaluate_current_performance()
            if current_performance > self.performance_threshold:
                return False
        
        return True
    
    def retrain_models(self):
        """Réentraîne le modèle avec les nouvelles données"""
        try:
            logger.info("Début du réentraînement du modèle")
            
            # Préparer les données d'entraînement
            records_with_feedback = [r for r in self.training_records if r.actual_feedback is not None]
            
            if len(records_with_feedback) < self.min_records_for_training:
                logger.warning(f"Pas assez de données pour l'entraînement: {len(records_with_feedback)}")
                return
            
            X = []
            y = []
            
            for record in records_with_feedback:
                features = self._create_feature_vector(
                    record.cv_features,
                    record.job_features,
                    record.questionnaire_features
                )
                X.append(features)
                y.append(record.actual_feedback)
            
            X = np.array(X)
            y = np.array(y)
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Entraînement du modèle
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Évaluation
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Mise à jour des métadonnées
            self.model_metadata = {
                'version': datetime.now().isoformat(),
                'last_training': datetime.now().isoformat(),
                'training_samples': len(records_with_feedback),
                'mse': float(mse),
                'r2_score': float(r2),
                'feature_count': len(self.feature_names)
            }
            
            # Sauvegarde
            self._save_model()
            
            logger.info(f"Modèle réentraîné - MSE: {mse:.3f}, R²: {r2:.3f}")
            
        except Exception as e:
            logger.error(f"Erreur réentraînement: {e}")
    
    def _evaluate_current_performance(self) -> float:
        """Évalue les performances actuelles du modèle"""
        if not self.model:
            return 0.0
        
        try:
            # Utiliser les derniers enregistrements avec feedback
            recent_records = [r for r in self.training_records[-50:] if r.actual_feedback is not None]
            
            if len(recent_records) < 10:
                return 0.5  # Performance neutre si pas assez de données
            
            predictions = []
            actuals = []
            
            for record in recent_records:
                features = self._create_feature_vector(
                    record.cv_features,
                    record.job_features,
                    record.questionnaire_features
                )
                
                pred = self.model.predict([features])[0]
                predictions.append(pred)
                actuals.append(record.actual_feedback)
            
            # Calculer R²
            r2 = r2_score(actuals, predictions)
            return max(r2, 0.0)  # R² peut être négatif
            
        except Exception as e:
            logger.error(f"Erreur évaluation performance: {e}")
            return 0.0
    
    def predict_score_improvement(self, cv_features: Dict, job_features: Dict, questionnaire_features: Dict) -> Optional[float]:
        """Prédit l'amélioration du score avec le modèle ML"""
        if not self.model:
            return None
        
        try:
            features = self._create_feature_vector(cv_features, job_features, questionnaire_features)
            prediction = self.model.predict([features])[0]
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            return None
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retourne l'importance des features"""
        if not self.model or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        try:
            importances = self.model.feature_importances_
            return dict(zip(self.feature_names, importances))
            
        except Exception as e:
            logger.error(f"Erreur importance des features: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Statistiques du système d'apprentissage"""
        records_with_feedback = [r for r in self.training_records if r.actual_feedback is not None]
        
        avg_feedback = 0
        if records_with_feedback:
            avg_feedback = sum(r.actual_feedback for r in records_with_feedback) / len(records_with_feedback)
        
        return {
            'total_records': len(self.training_records),
            'records_with_feedback': len(records_with_feedback),
            'average_feedback': avg_feedback,
            'model_trained': self.model is not None,
            'model_metadata': self.model_metadata,
            'feature_importance': self.get_feature_importance(),
            'last_record': self.training_records[-1].timestamp.isoformat() if self.training_records else None
        }
    
    def get_confidence(self) -> float:
        """Retourne la confiance du système d'apprentissage"""
        if not self.model:
            return 0.5  # Confiance neutre sans modèle
        
        performance = self._evaluate_current_performance()
        training_samples = len([r for r in self.training_records if r.actual_feedback is not None])
        
        # Confiance basée sur les performances et le nombre d'échantillons
        sample_confidence = min(training_samples / 100, 1.0)
        performance_confidence = max(performance, 0.0)
        
        return (sample_confidence * 0.4 + performance_confidence * 0.6)
    
    def get_suggestions(self) -> List[str]:
        """Suggestions d'amélioration basées sur l'apprentissage"""
        suggestions = []
        
        records_with_feedback = [r for r in self.training_records if r.actual_feedback is not None]
        
        if len(records_with_feedback) < self.min_records_for_training:
            suggestions.append(f"Collecte de plus de feedback nécessaire ({len(records_with_feedback)}/{self.min_records_for_training})")
        
        if self.model:
            feature_importance = self.get_feature_importance()
            if feature_importance:
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
                suggestions.append(f"Facteurs les plus importants: {', '.join([f[0] for f in top_features])}")
        
        performance = self._evaluate_current_performance()
        if performance < 0.6:
            suggestions.append("Performances du modèle à améliorer - Plus de données nécessaires")
        
        return suggestions
