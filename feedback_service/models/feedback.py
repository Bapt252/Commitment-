"""Module contenant les modèles pour le service de feedback."""

from enum import Enum
import logging
import json
import random
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)

class FeedbackSource(Enum):
    """Source d'où provient le feedback."""
    WEB_APP = 'web_app'
    MOBILE_APP = 'mobile_app'
    EMAIL = 'email'
    SURVEY = 'survey'
    CHATBOT = 'chatbot'
    SOCIAL_MEDIA = 'social_media'
    INTERACTION = 'interaction'

class FeedbackType(Enum):
    """Type de feedback."""
    EXPLICIT = 'explicit'  # Feedback donné explicitement par l'utilisateur
    IMPLICIT = 'implicit'  # Feedback déduit du comportement de l'utilisateur

class FeedbackCollector:
    """Service de collecte de feedback depuis différentes sources."""
    
    def __init__(self, repository):
        """Initialise le collecteur de feedback."""
        self.repository = repository
        logger.info("FeedbackCollector initialisé")
    
    def collect(self, feedback_data):
        """Collecte un nouveau feedback et le stocke."""
        # Validation des données
        if not feedback_data.get('content'):
            logger.error("Tentative de collecte de feedback sans contenu")
            raise ValueError("Le contenu du feedback est requis")
        
        # Enrichissement des données
        if 'created_at' not in feedback_data:
            feedback_data['created_at'] = datetime.now().isoformat()
        
        # Stockage du feedback
        feedback_id = self.repository.save(feedback_data)
        logger.info(f"Feedback collecté avec ID: {feedback_id}")
        
        return feedback_id

class FeedbackAnalyzer:
    """Service d'analyse du feedback pour extraire des insights."""
    
    def __init__(self, repository):
        """Initialise l'analyseur de feedback."""
        self.repository = repository
        self.vectorizer = TfidfVectorizer(stop_words='english')
        logger.info("FeedbackAnalyzer initialisé")
    
    def analyze_sentiment(self, text):
        """Analyse le sentiment d'un texte et retourne un score."""
        # Utilisation de TextBlob pour l'analyse de sentiment
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Normaliser le score entre -1 et 1
        return {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'label': 'positive' if sentiment.polarity > 0 else 'negative' if sentiment.polarity < 0 else 'neutral'
        }
    
    def extract_topics(self, text):
        """Extrait les sujets principaux d'un texte."""
        # Simulation d'extraction de sujets (dans un système réel, utiliser LDA ou autre)
        # Pour simuler, on extrait les mots les plus importants
        blob = TextBlob(text)
        words = blob.noun_phrases
        
        # Retourner les sujets identifiés
        return list(set(words))[:5] if words else []
    
    def analyze_sentiment_trends(self, filters=None):
        """Analyse les tendances de sentiment dans le temps."""
        # Récupérer les feedbacks filtrés
        feedbacks = self.repository.find_all(filters or {})
        
        # Grouper par période (jour, semaine, mois)
        by_day = {}
        by_week = {}
        by_month = {}
        
        for feedback in feedbacks:
            if 'sentiment' not in feedback:
                continue
                
            date = datetime.fromisoformat(feedback['created_at'])
            day_key = date.strftime('%Y-%m-%d')
            week_key = f"{date.year}-W{date.isocalendar()[1]}"
            month_key = date.strftime('%Y-%m')
            
            sentiment = feedback['sentiment']['polarity']
            
            # Agréger par jour
            if day_key not in by_day:
                by_day[day_key] = []
            by_day[day_key].append(sentiment)
            
            # Agréger par semaine
            if week_key not in by_week:
                by_week[week_key] = []
            by_week[week_key].append(sentiment)
            
            # Agréger par mois
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(sentiment)
        
        # Calculer les moyennes
        daily_avg = {day: sum(scores)/len(scores) for day, scores in by_day.items()}
        weekly_avg = {week: sum(scores)/len(scores) for week, scores in by_week.items()}
        monthly_avg = {month: sum(scores)/len(scores) for month, scores in by_month.items()}
        
        return {
            'daily': [{'date': day, 'sentiment': score} for day, score in daily_avg.items()],
            'weekly': [{'week': week, 'sentiment': score} for week, score in weekly_avg.items()],
            'monthly': [{'month': month, 'sentiment': score} for month, score in monthly_avg.items()],
            'overall': sum(sum(scores) for scores in by_day.values()) / sum(len(scores) for scores in by_day.values()) if by_day else 0
        }
    
    def analyze_topic_trends(self, filters=None):
        """Analyse les tendances des sujets mentionnés dans le temps."""
        # Récupérer les feedbacks filtrés
        feedbacks = self.repository.find_all(filters or {})
        
        # Compter les occurrences de chaque sujet
        topic_counts = {}
        topic_by_sentiment = {'positive': {}, 'neutral': {}, 'negative': {}}
        
        for feedback in feedbacks:
            if 'topics' not in feedback or 'sentiment' not in feedback:
                continue
                
            topics = feedback['topics']
            sentiment = feedback['sentiment']['label']
            
            for topic in topics:
                # Comptage global
                if topic not in topic_counts:
                    topic_counts[topic] = 0
                topic_counts[topic] += 1
                
                # Comptage par sentiment
                if topic not in topic_by_sentiment[sentiment]:
                    topic_by_sentiment[sentiment][topic] = 0
                topic_by_sentiment[sentiment][topic] += 1
        
        # Trier par fréquence
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_topics': [{'topic': topic, 'count': count} for topic, count in top_topics],
            'by_sentiment': {
                'positive': [{'topic': topic, 'count': count} 
                            for topic, count in sorted(topic_by_sentiment['positive'].items(), 
                                                      key=lambda x: x[1], reverse=True)[:5]],
                'neutral': [{'topic': topic, 'count': count} 
                           for topic, count in sorted(topic_by_sentiment['neutral'].items(), 
                                                     key=lambda x: x[1], reverse=True)[:5]],
                'negative': [{'topic': topic, 'count': count} 
                            for topic, count in sorted(topic_by_sentiment['negative'].items(), 
                                                      key=lambda x: x[1], reverse=True)[:5]]
            }
        }

class SatisfactionPredictor:
    """Service de prédiction de la satisfaction utilisateur."""
    
    def __init__(self):
        """Initialise le prédicteur de satisfaction."""
        self.model = RandomForestClassifier()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.model_trained = False
        self.model_version = datetime.now().strftime('%Y%m%d%H%M%S')
        logger.info("SatisfactionPredictor initialisé")
    
    def predict(self, data):
        """Prédit le score de satisfaction d'un utilisateur à partir d'un feedback."""
        # Dans un système réel, utiliser le modèle entraîné
        # Pour cette implémentation, on simule un score basé sur le sentiment
        if not self.model_trained:
            # Si le modèle n'est pas entraîné, utiliser une heuristique simple
            sentiment = data.get('sentiment', {}).get('polarity', 0)
            # Transformer le sentiment en score de satisfaction (0-100)
            return min(100, max(0, int((sentiment + 1) * 50)))
        else:
            # Utiliser le modèle entraîné (simulation)
            return random.randint(0, 100)
    
    def predict_from_interactions(self, data):
        """Prédit le score de satisfaction à partir des interactions."""
        # Simuler une prédiction basée sur les interactions
        interactions = data.get('interactions', [])
        
        if not interactions:
            return 50  # Score neutre par défaut
        
        # Calculer un score basé sur les types d'actions (simulation)
        positive_actions = ['view_job', 'apply_job', 'save_job', 'share_job']
        negative_actions = ['close_job', 'report_job']
        
        # Compter les actions positives et négatives
        positive_count = sum(1 for interaction in interactions 
                             if interaction.get('action_type') in positive_actions)
        negative_count = sum(1 for interaction in interactions 
                             if interaction.get('action_type') in negative_actions)
        
        # Calculer un ratio de satisfaction
        total = positive_count + negative_count
        if total == 0:
            return 50
        
        satisfaction_ratio = positive_count / total
        # Transformer en score (0-100)
        return min(100, max(0, int(satisfaction_ratio * 100)))
    
    def predict_overall(self, data):
        """Prédit le score global de satisfaction d'un utilisateur."""
        # Combiner les différentes sources de données pour une prédiction globale
        feedbacks = data.get('feedbacks', [])
        
        if not feedbacks:
            return 50  # Score neutre par défaut
        
        # Calculer une moyenne pondérée des scores de sentiment
        total_weight = 0
        weighted_sum = 0
        
        for feedback in feedbacks:
            if 'sentiment' not in feedback:
                continue
                
            sentiment = feedback['sentiment'].get('polarity', 0)
            weight = 1  # Poids par défaut
            
            # Donner plus de poids aux feedbacks récents
            created_at = datetime.fromisoformat(feedback['created_at'])
            days_old = (datetime.now() - created_at).days
            recency_weight = max(0.1, 1 - (days_old / 30))  # Diminue avec l'âge (30 jours)
            
            # Donner plus de poids aux feedbacks explicites
            type_weight = 2 if feedback.get('type') == FeedbackType.EXPLICIT.value else 1
            
            combined_weight = weight * recency_weight * type_weight
            weighted_sum += sentiment * combined_weight
            total_weight += combined_weight
        
        if total_weight == 0:
            return 50
            
        # Calculer la moyenne pondérée et convertir en score (0-100)
        avg_sentiment = weighted_sum / total_weight
        return min(100, max(0, int((avg_sentiment + 1) * 50)))
    
    def retrain(self, full_retrain=False):
        """Réentraîne le modèle de prédiction avec les dernières données."""
        # Simulation de réentraînement
        self.model_trained = True
        self.model_version = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Simuler des métriques d'entraînement
        metrics = {
            'accuracy': random.uniform(0.8, 0.95),
            'f1_score': random.uniform(0.75, 0.9),
            'precision': random.uniform(0.7, 0.95),
            'recall': random.uniform(0.7, 0.95)
        }
        
        logger.info(f"Modèle réentraîné, version: {self.model_version}")
        
        return {
            'model_version': self.model_version,
            'metrics': metrics,
            'full_retrain': full_retrain
        }
    
    def update_with_behavior_profiles(self, profiles):
        """Met à jour le modèle avec les données de profils comportementaux."""
        # Simulation d'intégration des données comportementales
        improvement = random.uniform(0.01, 0.05)
        
        logger.info(f"Modèle mis à jour avec {len(profiles)} profils comportementaux")
        
        return {
            'improvement': improvement,
            'profiles_count': len(profiles)
        }
