from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)

class FeedbackAnalyzer:
    def __init__(self, data_connector):
        self.data_connector = data_connector
        # Initialiser NLTK (en production, télécharger ces ressources à l'avance)
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            self.stop_words.update(set(stopwords.words('french')))
            self.lemmatizer = WordNetLemmatizer()
        except Exception as e:
            logger.warning(f"Could not initialize NLTK: {str(e)}")
            self.stop_words = set()
            self.lemmatizer = None
    
    async def get_feedback_data(self, period_days: int = 90) -> pd.DataFrame:
        """Récupère les données de feedback pour analyse"""
        since = datetime.utcnow() - timedelta(days=period_days)
        
        # Récupérer les événements de feedback
        feedback_events = await self.data_connector.get_events(
            event_type="match_feedback",
            since=since
        )
        
        # Convertir en DataFrame
        data = []
        for event in feedback_events:
            row = {
                'feedback_id': event.event_id,
                'match_id': event.match_id,
                'user_id': event.user_id,
                'timestamp': event.timestamp,
                'rating': event.rating.value if hasattr(event.rating, 'value') else event.rating,
                'feedback_text': event.feedback_text,
            }
            
            # Ajouter les aspects spécifiques s'ils existent
            if hasattr(event, 'specific_aspects') and event.specific_aspects:
                for aspect, value in event.specific_aspects.items():
                    row[f'aspect_{aspect}'] = value
                    
            data.append(row)
            
        return pd.DataFrame(data)
    
    def preprocess_text(self, text: str) -> List[str]:
        """Prétraite le texte pour analyse"""
        if not text or text.strip() == "":
            return []
            
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les caractères spéciaux
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokeniser
        tokens = word_tokenize(text)
        
        # Supprimer les stopwords
        tokens = [word for word in tokens if word not in self.stop_words]
        
        # Lemmatiser
        if self.lemmatizer:
            tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
            
        return tokens
    
    async def extract_common_themes(self, period_days: int = 90, min_count: int = 2) -> Dict[str, Any]:
        """Extrait les thèmes communs des feedbacks textuels"""
        # Récupérer les données de feedback
        df = await self.get_feedback_data(period_days)
        
        # Filtrer pour ne garder que les feedbacks avec du texte
        df_with_text = df[df['feedback_text'].notna() & (df['feedback_text'] != "")]
        
        if len(df_with_text) == 0:
            return {
                "themes": {},
                "total_feedbacks_analyzed": 0
            }
        
        # Prétraitement des textes
        all_tokens = []
        for text in df_with_text['feedback_text']:
            tokens = self.preprocess_text(text)
            all_tokens.extend(tokens)
        
        # Compter les occurrences
        word_counts = Counter(all_tokens)
        
        # Filtrer les mots qui apparaissent au moins min_count fois
        common_themes = {word: count for word, count in word_counts.items() if count >= min_count}
        
        # Trier par fréquence décroissante
        common_themes = dict(sorted(common_themes.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "themes": common_themes,
            "total_feedbacks_analyzed": len(df_with_text)
        }
    
    async def segment_feedback_by_rating(self, period_days: int = 90) -> Dict[str, Any]:
        """Segmente les feedbacks par niveau de rating pour analyse"""
        # Récupérer les données de feedback
        df = await self.get_feedback_data(period_days)
        
        if len(df) == 0:
            return {
                "segments": {},
                "total_feedbacks": 0
            }
        
        # Grouper par rating
        segments = {}
        for rating in range(1, 6):
            segment_df = df[df['rating'] == rating]
            
            if len(segment_df) == 0:
                segments[rating] = {
                    "count": 0,
                    "percentage": 0,
                    "common_themes": {}
                }
                continue
                
            # Extraire les thèmes communs pour ce segment
            segment_tokens = []
            for text in segment_df['feedback_text'].dropna():
                tokens = self.preprocess_text(text)
                segment_tokens.extend(tokens)
                
            word_counts = Counter(segment_tokens)
            common_themes = dict(sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            segments[rating] = {
                "count": len(segment_df),
                "percentage": len(segment_df) / len(df) * 100,
                "common_themes": common_themes
            }
            
        return {
            "segments": segments,
            "total_feedbacks": len(df)
        }
    
    async def analyze_rating_trends(self, period_days: int = 90, interval_days: int = 7) -> Dict[str, Any]:
        """Analyse les tendances des ratings au fil du temps"""
        # Récupérer les données de feedback
        df = await self.get_feedback_data(period_days)
        
        if len(df) == 0:
            return {
                "trends": [],
                "total_feedbacks": 0
            }
        
        # Convertir timestamp en datetime si nécessaire
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        # Définir les intervalles de temps
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        date_intervals = pd.date_range(start=start_date, end=end_date, freq=f'{interval_days}D')
        
        # Grouper par intervalle et calculer la moyenne des ratings
        trends = []
        for i in range(len(date_intervals)-1):
            interval_start = date_intervals[i]
            interval_end = date_intervals[i+1]
            
            interval_df = df[(df['timestamp'] >= interval_start) & (df['timestamp'] < interval_end)]
            
            if len(interval_df) > 0:
                avg_rating = interval_df['rating'].mean()
                count = len(interval_df)
            else:
                avg_rating = None
                count = 0
                
            trends.append({
                "interval_start": interval_start.isoformat(),
                "interval_end": interval_end.isoformat(),
                "avg_rating": avg_rating,
                "count": count
            })
            
        return {
            "trends": trends,
            "total_feedbacks": len(df)
        }