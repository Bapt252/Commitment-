"""
Module de détection de patterns comportementaux pour la Session 8
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import json
from sqlalchemy import create_engine, text
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PatternDetector:
    """Classe pour détecter des patterns dans les comportements utilisateur."""
    
    def __init__(self, db_url=None):
        """
        Initialise le détecteur de patterns.
        
        Args:
            db_url (str, optional): URL de connexion à la base de données.
                Si non spécifié, utilise la variable d'environnement DATABASE_URL.
        """
        self.db_url = db_url or os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
        try:
            self.engine = create_engine(self.db_url)
            logger.info("Connexion à la base de données établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            # Créer un moteur factice pour la démo
            self.engine = None
    
    def get_user_sequences(self, min_date=None, max_date=None, min_events=2):
        """
        Récupère les séquences d'événements par utilisateur.
        
        Args:
            min_date (datetime, optional): Date minimum des événements.
            max_date (datetime, optional): Date maximum des événements.
            min_events (int, optional): Nombre minimum d'événements par séquence.
            
        Returns:
            dict: Dictionnaire des séquences par utilisateur.
        """
        try:
            if self.engine is None:
                # Mode démo: retourner des séquences simulées
                return self._get_demo_sequences()
                
            # Construction de la requête
            query = """
            SELECT 
                t.user_id,
                t.session_id,
                t.event_type,
                t.timestamp
            FROM 
                tracking_events t
            WHERE 1=1
            """
            
            params = {}
            
            # Ajouter les filtres si spécifiés
            if min_date:
                query += " AND t.timestamp >= :min_date"
                params['min_date'] = min_date
                
            if max_date:
                query += " AND t.timestamp <= :max_date"
                params['max_date'] = max_date
                
            query += " ORDER BY t.user_id, t.session_id, t.timestamp"
            
            # Exécuter la requête
            df = pd.read_sql(query, self.engine, params=params)
            
            if df.empty:
                return {}
                
            # Organiser les événements en séquences
            sequences = defaultdict(list)
            
            for user_id, user_group in df.groupby('user_id'):
                # Grouper par session
                for session_id, session_group in user_group.groupby('session_id'):
                    if len(session_group) >= min_events:
                        # Créer une séquence d'événements
                        events = session_group.sort_values('timestamp')['event_type'].tolist()
                        sequences[user_id].append(events)
                        
            return dict(sequences)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des séquences utilisateur: {e}")
            # En cas d'erreur, retourner des séquences simulées
            return self._get_demo_sequences()
    
    def _get_demo_sequences(self):
        """
        Crée des séquences simulées pour la démo.
        
        Returns:
            dict: Dictionnaire des séquences simulées par utilisateur.
        """
        # Séquences simulées
        return {
            1: [['view', 'like', 'message'], ['view', 'share']],
            2: [['view', 'message', 'like'], ['view', 'view', 'save']],
            3: [['view', 'view', 'view']]
        }
    
    def find_sequential_patterns(self, user_sequences, min_support=0.3, min_length=2, max_length=5):
        """
        Trouve des patterns séquentiels dans les séquences utilisateur.
        
        Args:
            user_sequences (dict): Dictionnaire des séquences par utilisateur.
            min_support (float, optional): Support minimum pour qu'un pattern soit considéré comme valide.
            min_length (int, optional): Longueur minimum d'un pattern.
            max_length (int, optional): Longueur maximum d'un pattern.
            
        Returns:
            list: Liste des patterns détectés.
        """
        if not user_sequences:
            return []
            
        # Compter le nombre total de séquences
        total_sequences = sum(len(sequences) for sequences in user_sequences.values())
        
        if total_sequences == 0:
            return []
            
        # Extraire toutes les séquences dans une liste plate
        all_sequences = []
        for user_id, sequences in user_sequences.items():
            all_sequences.extend(sequences)
            
        # Trouver les patterns fréquents
        patterns = []
        
        # Générer tous les candidats de longueur 1
        candidates = set()
        for sequence in all_sequences:
            for event in sequence:
                candidates.add(event)
                
        # Pour chaque longueur de pattern
        for length in range(min_length, max_length + 1):
            if length == 1:
                # Comptage des événements uniques
                pattern_counts = defaultdict(int)
                for sequence in all_sequences:
                    for event in set(sequence):  # On compte une seule fois par séquence
                        pattern_counts[event] += 1
                        
                # Filtrer par support
                for event, count in pattern_counts.items():
                    support = count / total_sequences
                    if support >= min_support:
                        patterns.append({
                            'name': f"Pattern: {event}",
                            'sequence': [event],
                            'support': support,
                            'count': count
                        })
            else:
                # Pour les patterns plus longs, on cherche des séquences contiguës
                for sequence in all_sequences:
                    if len(sequence) < length:
                        continue
                        
                    # Générer toutes les sous-séquences contiguës de longueur 'length'
                    for i in range(len(sequence) - length + 1):
                        sub_sequence = sequence[i:i+length]
                        sub_sequence_tuple = tuple(sub_sequence)
                        
                        # Compter combien de séquences contiennent cette sous-séquence
                        count = sum(1 for seq in all_sequences if any(
                            seq[j:j+length] == sub_sequence 
                            for j in range(len(seq) - length + 1)
                        ))
                        
                        support = count / total_sequences
                        if support >= min_support:
                            # Vérifier si ce pattern n'existe pas déjà
                            pattern_exists = False
                            for pattern in patterns:
                                if pattern['sequence'] == sub_sequence:
                                    pattern_exists = True
                                    break
                                    
                            if not pattern_exists:
                                pattern_name = f"Pattern: {' → '.join(sub_sequence)}"
                                patterns.append({
                                    'name': pattern_name,
                                    'sequence': sub_sequence,
                                    'support': support,
                                    'count': count
                                })
        
        # Trier par support et longueur
        patterns.sort(key=lambda x: (x['support'], len(x['sequence'])), reverse=True)
        
        return patterns
    
    def save_behavioral_patterns(self, patterns):
        """
        Sauvegarde les patterns comportementaux dans la base de données.
        
        Args:
            patterns (list): Liste des patterns détectés.
            
        Returns:
            dict: Dictionnaire des IDs de patterns par nom.
        """
        if not patterns:
            return {}
            
        try:
            pattern_ids = {}
            
            if self.engine is None:
                # Mode démo: simuler la sauvegarde
                for i, pattern in enumerate(patterns):
                    pattern_ids[pattern['name']] = i + 1
                
                logger.info(f"Simulation: {len(patterns)} patterns comportementaux sauvegardés")
                return pattern_ids
                
            # Pour chaque pattern
            for pattern in patterns:
                # Créer une description
                description = f"Séquence: {' → '.join(pattern['sequence'])}. Support: {pattern['support']:.2f}"
                
                # Vérifier si le pattern existe déjà
                query = "SELECT pattern_id FROM behavioral_patterns WHERE name = :name"
                
                with self.engine.connect() as conn:
                    result = conn.execute(text(query), {'name': pattern['name']})
                    existing_pattern = result.fetchone()
                    
                    if existing_pattern:
                        # Récupérer l'ID existant
                        pattern_ids[pattern['name']] = existing_pattern[0]
                    else:
                        # Créer un nouveau pattern
                        insert_query = """
                        INSERT INTO behavioral_patterns (
                            name, description, pattern_type
                        ) VALUES (
                            :name, :description, :pattern_type
                        ) RETURNING pattern_id
                        """
                        
                        result = conn.execute(text(insert_query), {
                            'name': pattern['name'],
                            'description': description,
                            'pattern_type': 'sequence'
                        })
                        
                        new_id = result.fetchone()[0]
                        pattern_ids[pattern['name']] = new_id
                        
            logger.info(f"{len(patterns)} patterns comportementaux sauvegardés")
            return pattern_ids
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des patterns comportementaux: {e}")
            # Retourner des IDs simulés
            return {pattern['name']: i + 1 for i, pattern in enumerate(patterns)}
    
    def find_user_patterns(self, user_sequences, patterns):
        """
        Trouve les patterns pour chaque utilisateur.
        
        Args:
            user_sequences (dict): Dictionnaire des séquences par utilisateur.
            patterns (list): Liste des patterns détectés.
            
        Returns:
            dict: Dictionnaire des patterns détectés par utilisateur.
        """
        if not user_sequences or not patterns:
            return {}
            
        user_patterns = defaultdict(list)
        
        for user_id, sequences in user_sequences.items():
            if not sequences:
                continue
                
            # Pour chaque pattern
            for pattern in patterns:
                pattern_sequence = pattern['sequence']
                pattern_name = pattern['name']
                
                # Compter combien de fois ce pattern apparaît dans les séquences de l'utilisateur
                matches = 0
                total_sequences = len(sequences)
                
                for sequence in sequences:
                    # Vérifier si le pattern est dans cette séquence
                    for i in range(len(sequence) - len(pattern_sequence) + 1):
                        if sequence[i:i+len(pattern_sequence)] == pattern_sequence:
                            matches += 1
                            break
                
                # Calculer la force du pattern pour cet utilisateur
                if total_sequences > 0:
                    strength = matches / total_sequences
                    
                    # Ajouter si la force est suffisante
                    if strength > 0:
                        user_patterns[user_id].append({
                            'pattern_name': pattern_name,
                            'strength': strength,
                            'observation_count': matches
                        })
        
        return dict(user_patterns)
    
    def save_user_patterns(self, user_patterns, pattern_ids):
        """
        Sauvegarde les patterns par utilisateur dans la base de données.
        
        Args:
            user_patterns (dict): Dictionnaire des patterns par utilisateur.
            pattern_ids (dict): Dictionnaire des IDs de patterns par nom.
            
        Returns:
            bool: True si succès, False sinon.
        """
        if not user_patterns:
            return False
            
        try:
            if self.engine is None:
                # Mode démo: simuler la sauvegarde
                logger.info(f"Simulation: Patterns sauvegardés pour {len(user_patterns)} utilisateurs")
                return True
                
            # Pour chaque utilisateur
            for user_id, patterns in user_patterns.items():
                # Pour chaque pattern
                for pattern_data in patterns:
                    pattern_name = pattern_data['pattern_name']
                    
                    if pattern_name not in pattern_ids:
                        logger.warning(f"Pattern ID manquant pour {pattern_name}")
                        continue
                        
                    pattern_id = pattern_ids[pattern_name]
                    
                    # Vérifier si l'association existe déjà
                    query = """
                    SELECT user_id FROM user_patterns 
                    WHERE user_id = :user_id AND pattern_id = :pattern_id
                    """
                    
                    with self.engine.connect() as conn:
                        result = conn.execute(text(query), {
                            'user_id': user_id,
                            'pattern_id': pattern_id
                        })
                        existing = result.fetchone()
                        
                        if existing:
                            # Mettre à jour
                            update_query = """
                            UPDATE user_patterns
                            SET strength = :strength,
                                observation_count = :observation_count,
                                last_observed = CURRENT_TIMESTAMP,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = :user_id AND pattern_id = :pattern_id
                            """
                            
                            conn.execute(text(update_query), {
                                'user_id': user_id,
                                'pattern_id': pattern_id,
                                'strength': pattern_data['strength'],
                                'observation_count': pattern_data['observation_count']
                            })
                        else:
                            # Insérer
                            insert_query = """
                            INSERT INTO user_patterns (
                                user_id, pattern_id, strength, observation_count,
                                first_observed, last_observed
                            ) VALUES (
                                :user_id, :pattern_id, :strength, :observation_count,
                                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            )
                            """
                            
                            conn.execute(text(insert_query), {
                                'user_id': user_id,
                                'pattern_id': pattern_id,
                                'strength': pattern_data['strength'],
                                'observation_count': pattern_data['observation_count']
                            })
            
            logger.info(f"Patterns sauvegardés pour {len(user_patterns)} utilisateurs")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des patterns utilisateur: {e}")
            return False
    
    def run_detection(self):
        """
        Exécute une détection de patterns complète.
        
        Returns:
            dict: Résultats de la détection.
        """
        try:
            # Récupérer les séquences utilisateur
            user_sequences = self.get_user_sequences()
            
            if not user_sequences:
                return {
                    'status': 'warning',
                    'message': 'Aucune séquence utilisateur disponible',
                    'patterns_detected': 0,
                    'users_analyzed': 0
                }
                
            # Trouver les patterns
            patterns = self.find_sequential_patterns(user_sequences)
            
            if not patterns:
                return {
                    'status': 'warning',
                    'message': 'Aucun pattern détecté',
                    'patterns_detected': 0,
                    'users_analyzed': len(user_sequences)
                }
                
            # Sauvegarder les patterns
            pattern_ids = self.save_behavioral_patterns(patterns)
            
            # Trouver les patterns par utilisateur
            user_patterns = self.find_user_patterns(user_sequences, patterns)
            
            # Sauvegarder les patterns par utilisateur
            save_success = self.save_user_patterns(user_patterns, pattern_ids)
            
            return {
                'status': 'success' if save_success else 'partial',
                'message': 'Détection de patterns terminée',
                'patterns_detected': len(patterns),
                'users_analyzed': len(user_sequences),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la détection de patterns: {e}")
            return {
                'status': 'error',
                'message': f"Erreur lors de la détection: {str(e)}",
                'patterns_detected': 0,
                'users_analyzed': 0
            }
