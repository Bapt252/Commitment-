import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PatternDetector:
    """Détecte des patterns comportementaux dans les séquences d'actions utilisateur."""
    
    def __init__(self, window_size=30, min_occurrences=3):
        """
        Initialise le détecteur de patterns.
        
        Args:
            window_size (int): Taille de la fenêtre en jours pour l'analyse
            min_occurrences (int): Nombre minimum d'occurrences pour considérer un pattern
        """
        self.window_size = window_size
        self.min_occurrences = min_occurrences
        self.patterns = {}
        
    def detect_patterns(self, user_actions):
        """
        Analyse les actions utilisateur pour détecter des patterns récurrents.
        
        Args:
            user_actions (list): Liste de dictionnaires représentant les actions utilisateur
                Chaque action doit contenir: user_id, action_type, timestamp, et d'autres métadonnées
                
        Returns:
            dict: Dictionnaire des patterns détectés par user_id
        """
        # Convertir en DataFrame pour faciliter l'analyse
        df = pd.DataFrame(user_actions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Trier par utilisateur et timestamp
        df = df.sort_values(['user_id', 'timestamp'])
        
        user_patterns = {}
        
        # Analyser chaque utilisateur séparément
        for user_id, user_df in df.groupby('user_id'):
            # Patterns de temps
            time_patterns = self._detect_time_patterns(user_df)
            
            # Patterns de séquence d'actions
            sequence_patterns = self._detect_action_sequences(user_df)
            
            # Patterns d'intervalle régulier
            interval_patterns = self._detect_regular_intervals(user_df)
            
            # Combiner tous les patterns
            user_patterns[user_id] = {
                'time_patterns': time_patterns,
                'sequence_patterns': sequence_patterns,
                'interval_patterns': interval_patterns
            }
            
        self.patterns = user_patterns
        logger.info(f"Patterns détectés pour {len(user_patterns)} utilisateurs")
        
        return user_patterns
    
    def _detect_time_patterns(self, user_df):
        """
        Détecte les moments de la journée où l'utilisateur est le plus actif.
        
        Args:
            user_df (DataFrame): Actions d'un utilisateur spécifique
            
        Returns:
            dict: Patterns de temps détectés
        """
        if user_df.empty:
            return {}
            
        # Extraire l'heure de la journée
        user_df['hour'] = user_df['timestamp'].dt.hour
        
        # Compter les occurrences par heure
        hour_counts = user_df['hour'].value_counts()
        
        # Identifier les heures de pointe (plus de min_occurrences)
        peak_hours = hour_counts[hour_counts >= self.min_occurrences].index.tolist()
        
        # Regrouper les heures en périodes (matin, après-midi, soir, nuit)
        periods = {
            'morning': [6, 7, 8, 9, 10, 11],
            'afternoon': [12, 13, 14, 15, 16, 17],
            'evening': [18, 19, 20, 21, 22, 23],
            'night': [0, 1, 2, 3, 4, 5]
        }
        
        preferred_periods = []
        for period, hours in periods.items():
            if any(hour in peak_hours for hour in hours):
                preferred_periods.append(period)
                
        # Déterminer les jours de la semaine préférés
        user_df['day_of_week'] = user_df['timestamp'].dt.day_name()
        day_counts = user_df['day_of_week'].value_counts()
        preferred_days = day_counts[day_counts >= self.min_occurrences].index.tolist()
        
        return {
            'peak_hours': peak_hours,
            'preferred_periods': preferred_periods,
            'preferred_days': preferred_days
        }
    
    def _detect_action_sequences(self, user_df):
        """
        Détecte les séquences d'actions récurrentes.
        
        Args:
            user_df (DataFrame): Actions d'un utilisateur spécifique
            
        Returns:
            list: Séquences d'actions fréquentes
        """
        if len(user_df) < 3:  # Besoin d'au moins 3 actions pour une séquence
            return []
            
        # Créer des n-grammes d'actions (séquences de 2 et 3 actions)
        action_list = user_df['action_type'].tolist()
        
        bigrams = [' > '.join(action_list[i:i+2]) for i in range(len(action_list)-1)]
        trigrams = [' > '.join(action_list[i:i+3]) for i in range(len(action_list)-2)]
        
        # Compter les occurrences
        bigram_counts = pd.Series(bigrams).value_counts()
        trigram_counts = pd.Series(trigrams).value_counts()
        
        # Identifier les séquences fréquentes
        frequent_bigrams = bigram_counts[bigram_counts >= self.min_occurrences].index.tolist()
        frequent_trigrams = trigram_counts[trigram_counts >= self.min_occurrences].index.tolist()
        
        return {
            'bigrams': frequent_bigrams,
            'trigrams': frequent_trigrams
        }
    
    def _detect_regular_intervals(self, user_df):
        """
        Détecte si l'utilisateur interagit à intervalles réguliers.
        
        Args:
            user_df (DataFrame): Actions d'un utilisateur spécifique
            
        Returns:
            dict: Patterns d'intervalle détectés
        """
        if len(user_df) < 3:  # Besoin d'au moins 3 points pour détecter un intervalle
            return {}
            
        # Calculer les différences de temps entre actions consécutives
        user_df = user_df.sort_values('timestamp')
        time_diffs = user_df['timestamp'].diff().dropna()
        
        # Convertir en heures
        time_diffs_hours = time_diffs.dt.total_seconds() / 3600
        
        # Regrouper par intervalle approximatif (arrondi à l'heure près)
        rounded_diffs = time_diffs_hours.round().value_counts()
        
        # Identifier les intervalles réguliers (plus de min_occurrences)
        regular_intervals = rounded_diffs[rounded_diffs >= self.min_occurrences].index.tolist()
        
        # Vérifier les intervalles quotidiens, hebdomadaires, mensuels
        daily_pattern = 24 in regular_intervals or 23 in regular_intervals or 25 in regular_intervals
        weekly_pattern = any(h in regular_intervals for h in range(167, 169))  # ~168 heures
        
        return {
            'regular_intervals_hours': regular_intervals,
            'daily_pattern': daily_pattern,
            'weekly_pattern': weekly_pattern
        }
    
    def get_user_patterns(self, user_id):
        """
        Retourne les patterns détectés pour un utilisateur spécifique.
        
        Args:
            user_id (str): ID de l'utilisateur
            
        Returns:
            dict: Patterns de l'utilisateur, ou None si non trouvé
        """
        return self.patterns.get(user_id)
        
    def get_common_patterns(self):
        """
        Identifie les patterns communs à plusieurs utilisateurs.
        
        Returns:
            dict: Patterns communs et leur fréquence
        """
        if not self.patterns:
            return {}
            
        common_time_periods = {}
        common_sequences = {}
        
        # Analyser les patterns de temps
        for user_id, patterns in self.patterns.items():
            time_patterns = patterns.get('time_patterns', {})
            for period in time_patterns.get('preferred_periods', []):
                common_time_periods[period] = common_time_periods.get(period, 0) + 1
        
        # Analyser les séquences d'actions
        for user_id, patterns in self.patterns.items():
            sequence_patterns = patterns.get('sequence_patterns', {})
            for bigram in sequence_patterns.get('bigrams', []):
                common_sequences[bigram] = common_sequences.get(bigram, 0) + 1
        
        # Filtrer par fréquence minimale (au moins 3 utilisateurs)
        min_users = 3
        common_time_periods = {k: v for k, v in common_time_periods.items() if v >= min_users}
        common_sequences = {k: v for k, v in common_sequences.items() if v >= min_users}
        
        return {
            'common_time_periods': common_time_periods,
            'common_sequences': common_sequences
        }