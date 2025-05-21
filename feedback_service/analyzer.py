"""
Module d'analyse de feedback pour extraire des insights à partir des feedbacks utilisateurs.
Inclut l'analyse de sentiment, l'extraction de sujets et la détection de tendances.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob

from feedback_service.models import (
    Feedback, FeedbackAnalysis, FeedbackTrend, 
    Sentiment, FeedbackType, FeedbackChannel
)

# Configuration du logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class FeedbackAnalyzer:
    """Classe pour analyser les feedbacks utilisateurs."""
    
    def __init__(self, db_session: Session):
        """
        Initialise l'analyseur de feedback.
        
        Args:
            db_session: Session de base de données SQLAlchemy
        """
        self.db_session = db_session
        self.vectorizer = TfidfVectorizer(
            max_features=100, 
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def analyze_new_feedback(self) -> int:
        """
        Analyse tous les feedbacks non traités.
        
        Returns:
            Nombre de feedbacks analysés
        """
        # Récupérer les feedbacks non traités
        unprocessed_feedback = self.db_session.query(Feedback).filter_by(processed=False).all()
        count = 0
        
        for feedback in unprocessed_feedback:
            # Analyser le sentiment
            if feedback.content:
                sentiment_result = self.analyze_sentiment(feedback.content)
                self._save_analysis(feedback.id, "sentiment", sentiment_result)
                feedback.sentiment = sentiment_result["sentiment"]
            
            # Analyser les sujets si c'est un commentaire textuel
            if feedback.channel == FeedbackChannel.COMMENT and feedback.content:
                topic_result = self.extract_topics(feedback.content)
                self._save_analysis(feedback.id, "topic", {"topics": topic_result})
            
            # Marquer comme traité
            feedback.processed = True
            count += 1
        
        # Commiter les changements
        self.db_session.commit()
        logger.info(f"Analysé {count} nouveaux feedbacks")
        
        # Mettre à jour les tendances si des feedbacks ont été analysés
        if count > 0:
            self.update_trends()
            
        return count
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec le sentiment, le score et la confiance
        """
        # Utiliser TextBlob pour l'analyse de sentiment
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        # Déterminer le sentiment basé sur la polarité
        if polarity > 0.2:
            sentiment = Sentiment.POSITIVE
        elif polarity < -0.2:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL
            
        # Calculer le score de confiance
        # (distance par rapport à 0, normalisée entre 0 et 1)
        confidence = min(abs(polarity) * 1.5, 1.0)
        
        return {
            "sentiment": sentiment,
            "score": polarity,
            "confidence": confidence
        }
    
    def extract_topics(self, text: str, num_topics: int = 3) -> List[str]:
        """
        Extrait les principaux sujets d'un texte.
        
        Args:
            text: Texte à analyser
            num_topics: Nombre de sujets à extraire
            
        Returns:
            Liste des sujets principaux
        """
        # Méthode simple basée sur la fréquence des mots
        # Nettoyer le texte
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        # Filtrer les mots courts
        words = [word for word in words if len(word) > 3]
        
        # Compter les occurrences
        word_counts = {}
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        
        # Trier par fréquence
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les N premiers mots comme "sujets"
        topics = [word for word, count in sorted_words[:num_topics]]
        
        return topics
    
    def cluster_feedback(self, min_samples: int = 20) -> Dict[str, Any]:
        """
        Groupe les feedbacks textuels en clusters thématiques.
        
        Args:
            min_samples: Nombre minimum d'échantillons pour effectuer le clustering
            
        Returns:
            Résultats du clustering avec les clusters et leurs mots clés
        """
        # Récupérer les commentaires textuels
        text_feedbacks = self.db_session.query(Feedback).filter(
            Feedback.content.isnot(None),
            Feedback.channel == FeedbackChannel.COMMENT
        ).all()
        
        if len(text_feedbacks) < min_samples:
            logger.info(f"Pas assez de feedbacks pour le clustering ({len(text_feedbacks)})")
            return {"clusters": [], "success": False, "reason": "not_enough_samples"}
        
        # Préparer les données
        texts = [f.content for f in text_feedbacks]
        ids = [f.id for f in text_feedbacks]
        
        # Vectoriser les textes
        try:
            X = self.vectorizer.fit_transform(texts)
        except Exception as e:
            logger.error(f"Erreur lors de la vectorisation: {str(e)}")
            return {"clusters": [], "success": False, "reason": "vectorization_error"}
        
        # Déterminer le nombre de clusters (méthode simple)
        k = min(5, len(texts) // 10 + 1)  # Maximum 5 clusters ou 1/10 des échantillons
        
        # Appliquer K-means
        kmeans = KMeans(n_clusters=k, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # Extraire les mots importants par cluster
        feature_names = self.vectorizer.get_feature_names_out()
        cluster_centers = kmeans.cluster_centers_
        
        # Résultats par cluster
        cluster_results = []
        for i in range(k):
            # Indices des feedbacks dans ce cluster
            cluster_indices = [idx for idx, label in enumerate(clusters) if label == i]
            cluster_feedback_ids = [ids[idx] for idx in cluster_indices]
            
            # Mots les plus importants dans ce cluster
            sorted_indices = np.argsort(cluster_centers[i])[::-1]
            top_keywords = [feature_names[idx] for idx in sorted_indices[:5]]
            
            cluster_results.append({
                "cluster_id": i,
                "size": len(cluster_indices),
                "keywords": top_keywords,
                "feedback_ids": cluster_feedback_ids
            })
        
        return {
            "clusters": cluster_results,
            "total_samples": len(texts),
            "success": True
        }
    
    def update_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Met à jour les tendances de feedback.
        
        Args:
            days: Nombre de jours à inclure dans les tendances
            
        Returns:
            Résultats de la mise à jour des tendances
        """
        # Définir la période
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Récupérer les feedbacks de la période
        feedbacks = self.db_session.query(Feedback).filter(
            Feedback.created_at >= start_date,
            Feedback.created_at <= end_date
        ).all()
        
        if not feedbacks:
            logger.info(f"Pas de feedback sur la période de {days} jours")
            return {"trends": [], "success": False, "reason": "no_data"}
        
        # Convertir en DataFrame pour faciliter l'analyse
        df = pd.DataFrame([{
            'id': f.id,
            'user_id': f.user_id,
            'feedback_type': f.feedback_type,
            'channel': f.channel,
            'sentiment': f.sentiment,
            'rating': f.rating,
            'created_at': f.created_at,
            'has_content': f.content is not None and len(f.content) > 0
        } for f in feedbacks])
        
        trends = []
        
        # Tendance par sentiment
        sentiment_trend = self._create_trend_by_dimension(
            df, 'sentiment', 'sentiment', start_date, end_date
        )
        trends.append(sentiment_trend)
        
        # Tendance par canal
        channel_trend = self._create_trend_by_dimension(
            df, 'channel', 'channel', start_date, end_date
        )
        trends.append(channel_trend)
        
        # Tendance par type de feedback
        type_trend = self._create_trend_by_dimension(
            df, 'feedback_type', 'type', start_date, end_date
        )
        trends.append(type_trend)
        
        # Tendance temporelle (par semaine)
        df['week'] = df['created_at'].dt.isocalendar().week
        weekly_trend = self._create_time_trend(df, 'week', 'weekly', start_date, end_date)
        trends.append(weekly_trend)
        
        # Enregistrer les tendances en base de données
        self._save_trends(trends)
        
        return {
            "trends": trends,
            "success": True,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }
    
    def _create_trend_by_dimension(
        self, df: pd.DataFrame, dimension: str, trend_type: str, 
        start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Crée une tendance par dimension donnée.
        
        Args:
            df: DataFrame des feedbacks
            dimension: Dimension à analyser
            trend_type: Type de tendance
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tendance générée
        """
        # Grouper par dimension
        grouped = df.groupby(dimension).agg({
            'id': 'count',
            'rating': lambda x: x.mean() if x.count() > 0 else None
        }).reset_index()
        
        # Renommer les colonnes
        grouped.columns = [dimension, 'count', 'average_rating']
        
        # Convertir en dictionnaire de résultats
        trend_data = []
        for _, row in grouped.iterrows():
            trend_data.append({
                'value': str(row[dimension]),
                'count': int(row['count']),
                'average_rating': float(row['average_rating']) if not pd.isna(row['average_rating']) else None
            })
            
        return {
            'trend_type': trend_type,
            'dimension': dimension,
            'data': trend_data,
            'period_start': start_date,
            'period_end': end_date
        }
    
    def _create_time_trend(
        self, df: pd.DataFrame, time_column: str, trend_type: str, 
        start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Crée une tendance temporelle.
        
        Args:
            df: DataFrame des feedbacks
            time_column: Colonne de temps
            trend_type: Type de tendance
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Tendance générée
        """
        # Grouper par période de temps
        grouped = df.groupby(time_column).agg({
            'id': 'count',
            'rating': lambda x: x.mean() if x.count() > 0 else None,
            'sentiment': lambda x: x.value_counts().to_dict()
        }).reset_index()
        
        # Convertir en dictionnaire de résultats
        trend_data = []
        for _, row in grouped.iterrows():
            sentiment_counts = row['sentiment'] if isinstance(row['sentiment'], dict) else {}
            
            trend_data.append({
                'value': str(row[time_column]),
                'count': int(row['id']),
                'average_rating': float(row['rating']) if not pd.isna(row['rating']) else None,
                'sentiment_counts': sentiment_counts
            })
            
        return {
            'trend_type': trend_type,
            'dimension': 'time',
            'data': trend_data,
            'period_start': start_date,
            'period_end': end_date
        }
    
    def _save_analysis(self, feedback_id: int, analysis_type: str, result: Dict[str, Any]) -> None:
        """
        Enregistre les résultats d'analyse en base de données.
        
        Args:
            feedback_id: ID du feedback
            analysis_type: Type d'analyse
            result: Résultats de l'analyse
        """
        analysis = FeedbackAnalysis(
            feedback_id=feedback_id,
            analysis_type=analysis_type,
            result=result,
            confidence=result.get('confidence', 0.8)  # Valeur par défaut
        )
        self.db_session.add(analysis)
    
    def _save_trends(self, trends: List[Dict[str, Any]]) -> None:
        """
        Enregistre les tendances en base de données.
        
        Args:
            trends: Liste des tendances à enregistrer
        """
        # Supprimer les anciennes tendances
        self.db_session.query(FeedbackTrend).delete()
        
        # Ajouter les nouvelles tendances
        for trend in trends:
            trend_type = trend['trend_type']
            dimension = trend['dimension']
            
            for item in trend['data']:
                db_trend = FeedbackTrend(
                    trend_type=trend_type,
                    dimension=dimension,
                    value=item['value'],
                    count=item['count'],
                    average_rating=item.get('average_rating'),
                    period_start=trend['period_start'],
                    period_end=trend['period_end']
                )
                self.db_session.add(db_trend)
        
        self.db_session.commit()
