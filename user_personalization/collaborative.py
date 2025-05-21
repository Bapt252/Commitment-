"""
Module de recommandation collaborative pour la personnalisation utilisateur
"""

import json
import logging
import pickle
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

try:
    import implicit
    IMPLICIT_AVAILABLE = True
except ImportError:
    IMPLICIT_AVAILABLE = False

try:
    from lightfm import LightFM
    LIGHTFM_AVAILABLE = True
except ImportError:
    LIGHTFM_AVAILABLE = False
    
from user_personalization import (
    DEFAULT_DATABASE_URL, 
    COLLABORATIVE_PARAMS,
    logger
)

class CollaborativeRecommender:
    """
    Système de recommandation collaborative.
    
    Implémente différentes méthodes de filtrage collaboratif :
    - Filtrage basé sur les utilisateurs (user-based)
    - Filtrage basé sur les items (item-based)
    - Factorisation matricielle
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialise le système de recommandation collaborative.
        
        Args:
            db_url: URL de connexion à la base de données.
                Si non spécifié, utilise la variable d'environnement DATABASE_URL.
        """
        self.db_url = db_url or DEFAULT_DATABASE_URL
        try:
            self.engine = create_engine(self.db_url)
            logger.info("Connexion à la base de données établie")
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données: {e}")
            self.engine = None
        
        # Paramètres de filtrage collaboratif
        self.min_interactions = COLLABORATIVE_PARAMS.get('min_interactions', 5)
        self.num_similar_users = COLLABORATIVE_PARAMS.get('num_similar_users', 10)
        self.num_factors = COLLABORATIVE_PARAMS.get('num_factors', 50)
        self.similarity_threshold = COLLABORATIVE_PARAMS.get('similarity_threshold', 0.3)
        
        # Matrices pour le filtrage collaboratif
        self.user_item_matrix = None
        self.item_user_matrix = None
        self.user_similarity_matrix = None
        self.item_similarity_matrix = None
        self.user_factors = None
        self.item_factors = None
        
        # Mappings id vers index dans les matrices
        self.user_id_to_index = {}
        self.item_id_to_index = {}
        self.index_to_user_id = {}
        self.index_to_item_id = {}
        
        # Modèles
        self.user_model = None
        self.item_model = None
        
    def find_similar_users(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Trouve des utilisateurs similaires au utilisateur donné.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum d'utilisateurs similaires à renvoyer
            
        Returns:
            Liste des utilisateurs similaires avec leur score de similarité
        """
        # Vérifier si les similarités sont déjà calculées en base
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return []
                
            # Requête pour récupérer les similarités
            query = """
            SELECT user_id_2, similarity_score, last_computed
            FROM user_similarities
            WHERE user_id_1 = :user_id
            ORDER BY similarity_score DESC
            LIMIT :limit
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {
                    "user_id": user_id,
                    "limit": limit
                })
                
                similar_users = []
                needs_computation = True
                
                for row in result:
                    similar_users.append({
                        'user_id': row[0],
                        'similarity': float(row[1]),
                        'computed_at': row[2].isoformat() if row[2] else None
                    })
                    
                    # Si on a des similarités récentes, pas besoin de recalculer
                    if row[2] and (datetime.now() - row[2]).days < 7:
                        needs_computation = False
                
                if similar_users and not needs_computation:
                    logger.debug(f"Similarités pour l'utilisateur {user_id} récupérées depuis la base de données")
                    return similar_users
                    
                # Si on n'a pas de similarités ou qu'elles sont trop anciennes,
                # recalculer et mettre à jour la base de données
                computed_similarities = self._compute_user_similarities(user_id, limit)
                
                if computed_similarities:
                    # Sauvegarder les similarités
                    self._save_user_similarities(user_id, computed_similarities)
                    
                    # Formater les résultats
                    similar_users = []
                    for similar_id, score in computed_similarities:
                        similar_users.append({
                            'user_id': similar_id,
                            'similarity': float(score),
                            'computed_at': datetime.now().isoformat()
                        })
                    
                    return similar_users
                
                return similar_users
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'utilisateurs similaires: {e}")
            return []
    
    def get_collaborative_weights(self, user_id: int) -> Dict[str, float]:
        """
        Calcule des poids de critères personnalisés basés sur le filtrage collaboratif.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Poids de critères recommandés
        """
        # Trouver les utilisateurs similaires
        similar_users = self.find_similar_users(user_id, limit=self.num_similar_users)
        
        if not similar_users:
            logger.warning(f"Aucun utilisateur similaire trouvé pour l'utilisateur {user_id}")
            return {}
            
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return {}
                
            # Récupérer les poids des utilisateurs similaires
            user_ids = [u['user_id'] for u in similar_users]
            similarities = {u['user_id']: u['similarity'] for u in similar_users}
            
            # Construire la liste des paramètres pour la clause IN
            placeholders = ', '.join([f':user_id_{i}' for i in range(len(user_ids))])
            params = {f'user_id_{i}': user_id for i, user_id in enumerate(user_ids)}
            
            # Requête pour récupérer les poids
            query = f"""
            SELECT 
                user_id, skills_weight, contract_weight, location_weight, 
                date_weight, salary_weight, experience_weight,
                soft_skills_weight, culture_weight
            FROM user_matching_weights
            WHERE user_id IN ({placeholders})
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                
                # Initialiser les poids moyens pondérés
                weighted_sum = {
                    'skills': 0.0,
                    'contract': 0.0,
                    'location': 0.0,
                    'date': 0.0,
                    'salary': 0.0,
                    'experience': 0.0,
                    'soft_skills': 0.0,
                    'culture': 0.0
                }
                total_similarity = 0.0
                
                # Calculer la moyenne pondérée des poids
                for row in result:
                    uid = row[0]
                    if uid in similarities:
                        sim = similarities[uid]
                        if sim >= self.similarity_threshold:
                            weighted_sum['skills'] += float(row[1]) * sim
                            weighted_sum['contract'] += float(row[2]) * sim
                            weighted_sum['location'] += float(row[3]) * sim
                            weighted_sum['date'] += float(row[4]) * sim
                            weighted_sum['salary'] += float(row[5]) * sim
                            weighted_sum['experience'] += float(row[6]) * sim
                            weighted_sum['soft_skills'] += float(row[7]) * sim
                            weighted_sum['culture'] += float(row[8]) * sim
                            total_similarity += sim
                
                # Normaliser les poids
                if total_similarity > 0:
                    for key in weighted_sum:
                        weighted_sum[key] /= total_similarity
                        
                    return weighted_sum
                else:
                    logger.warning(f"Pas assez de données pour calculer des poids collaboratifs pour l'utilisateur {user_id}")
                    return {}
        except Exception as e:
            logger.error(f"Erreur lors du calcul des poids collaboratifs: {e}")
            return {}
    
    def update_similarity_matrices(self):
        """
        Met à jour les matrices de similarité entre utilisateurs et entre items.
        
        Cette méthode devrait être exécutée périodiquement (par exemple, quotidiennement)
        pour maintenir les recommandations à jour.
        """
        try:
            # Charger les données d'interaction
            interactions_df = self._load_interaction_data()
            
            if interactions_df.empty:
                logger.warning("Pas de données d'interaction disponibles")
                return False
                
            # Créer les matrices d'interaction
            self._create_interaction_matrices(interactions_df)
            
            # Calculer les similarités
            self._compute_similarity_matrices()
            
            # Entraîner les modèles de factorisation matricielle
            self._train_matrix_factorization()
            
            # Sauvegarder les matrices
            self._save_matrices()
            
            logger.info("Matrices de similarité mises à jour avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des matrices de similarité: {e}")
            return False
    
    def _load_interaction_data(self) -> pd.DataFrame:
        """
        Charge les données d'interaction utilisateur-item.
        
        Returns:
            DataFrame avec les interactions
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return pd.DataFrame()
                
            # Requête pour récupérer les événements d'interaction
            # (feedback, clics, matches acceptés, etc.)
            query = """
            SELECT 
                f.user_id,
                f.job_id,
                f.user_rating,
                f.created_at
            FROM personalization_feedback f
            WHERE f.job_id IS NOT NULL
            
            UNION ALL
            
            SELECT 
                t.user_id,
                CAST(t.event_data->>'job_id' AS INTEGER) AS job_id,
                CASE 
                    WHEN t.event_type = 'like' THEN 1.0
                    WHEN t.event_type = 'view' THEN 0.5
                    WHEN t.event_type = 'apply' THEN 2.0
                    ELSE 0.3
                END AS rating,
                t.timestamp AS created_at
            FROM tracking_events t
            WHERE t.event_data->>'job_id' IS NOT NULL
            """
            
            # Exécuter la requête
            df = pd.read_sql(query, self.engine)
            
            # Filtrer les utilisateurs et items avec trop peu d'interactions
            user_counts = df['user_id'].value_counts()
            item_counts = df['job_id'].value_counts()
            
            active_users = user_counts[user_counts >= self.min_interactions].index
            active_items = item_counts[item_counts >= self.min_interactions].index
            
            filtered_df = df[
                df['user_id'].isin(active_users) & 
                df['job_id'].isin(active_items)
            ]
            
            if filtered_df.empty:
                logger.warning("Pas assez de données d'interaction après filtrage")
                return pd.DataFrame()
                
            # Agréger les interactions multiples
            aggregated_df = filtered_df.groupby(['user_id', 'job_id']).agg({
                'user_rating': 'mean',
                'created_at': 'max'
            }).reset_index()
            
            logger.info(f"Données d'interaction chargées: {len(aggregated_df)} interactions, {len(active_users)} utilisateurs, {len(active_items)} items")
            
            return aggregated_df
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données d'interaction: {e}")
            return pd.DataFrame()
    
    def _create_interaction_matrices(self, interactions_df: pd.DataFrame):
        """
        Crée les matrices d'interaction utilisateur-item.
        
        Args:
            interactions_df: DataFrame avec les interactions
        """
        if interactions_df.empty:
            return
            
        # Créer les mappings d'ID vers index
        unique_users = interactions_df['user_id'].unique()
        unique_items = interactions_df['job_id'].unique()
        
        self.user_id_to_index = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_id_to_index = {item_id: idx for idx, item_id in enumerate(unique_items)}
        self.index_to_user_id = {idx: user_id for user_id, idx in self.user_id_to_index.items()}
        self.index_to_item_id = {idx: item_id for item_id, idx in self.item_id_to_index.items()}
        
        # Créer la matrice utilisateur-item
        user_indices = [self.user_id_to_index[user_id] for user_id in interactions_df['user_id']]
        item_indices = [self.item_id_to_index[item_id] for item_id in interactions_df['job_id']]
        
        # Utiliser les ratings comme poids
        ratings = interactions_df['user_rating'].values
        
        # Créer la matrice sparse
        self.user_item_matrix = csr_matrix(
            (ratings, (user_indices, item_indices)),
            shape=(len(unique_users), len(unique_items))
        )
        
        # Matrice item-user (transposée)
        self.item_user_matrix = self.user_item_matrix.transpose()
        
        logger.debug(f"Matrices d'interaction créées: {self.user_item_matrix.shape}")
    
    def _compute_similarity_matrices(self):
        """
        Calcule les matrices de similarité entre utilisateurs et entre items.
        """
        if self.user_item_matrix is None or self.item_user_matrix is None:
            logger.warning("Matrices d'interaction non initialisées")
            return
            
        # Calculer la similarité entre utilisateurs
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
        
        # Calculer la similarité entre items
        self.item_similarity_matrix = cosine_similarity(self.item_user_matrix)
        
        logger.debug(f"Matrices de similarité calculées: {self.user_similarity_matrix.shape}, {self.item_similarity_matrix.shape}")
    
    def _train_matrix_factorization(self):
        """
        Entraîne les modèles de factorisation matricielle.
        """
        if self.user_item_matrix is None:
            logger.warning("Matrice d'interaction non initialisée")
            return
            
        # Entraîner le modèle de factorisation matricielle pour les utilisateurs
        if IMPLICIT_AVAILABLE:
            try:
                # Modèle ALS pour le filtrage collaboratif
                self.user_model = implicit.als.AlternatingLeastSquares(
                    factors=self.num_factors,
                    regularization=0.1,
                    iterations=20
                )
                self.user_model.fit(self.user_item_matrix)
                
                # Extraire les facteurs utilisateur et item
                self.user_factors = self.user_model.user_factors
                self.item_factors = self.user_model.item_factors
                
                logger.info(f"Modèle de factorisation matricielle entraîné: {self.num_factors} facteurs")
            except Exception as e:
                logger.error(f"Erreur lors de l'entraînement du modèle ALS: {e}")
        else:
            logger.warning("Package 'implicit' non disponible, factorisation matricielle désactivée")
    
    def _save_matrices(self):
        """
        Sauvegarde les matrices de factorisation pour une utilisation future.
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return
                
            if self.user_factors is not None and self.item_factors is not None:
                # Sérialiser les matrices
                user_factors_bytes = pickle.dumps(self.user_factors)
                item_factors_bytes = pickle.dumps(self.item_factors)
                
                # Sauvegarder les matrices en base de données
                query_user = """
                INSERT INTO collaborative_matrices 
                (matrix_type, dimensions, data, created_at, last_updated)
                VALUES ('user_factors', :dimensions, :data, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (matrix_type) DO UPDATE
                SET data = :data, dimensions = :dimensions, last_updated = CURRENT_TIMESTAMP
                """
                
                query_item = """
                INSERT INTO collaborative_matrices 
                (matrix_type, dimensions, data, created_at, last_updated)
                VALUES ('item_factors', :dimensions, :data, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (matrix_type) DO UPDATE
                SET data = :data, dimensions = :dimensions, last_updated = CURRENT_TIMESTAMP
                """
                
                with self.engine.connect() as conn:
                    # Sauvegarder les facteurs utilisateur
                    conn.execute(text(query_user), {
                        "dimensions": self.num_factors,
                        "data": user_factors_bytes
                    })
                    
                    # Sauvegarder les facteurs item
                    conn.execute(text(query_item), {
                        "dimensions": self.num_factors,
                        "data": item_factors_bytes
                    })
                    
                    conn.commit()
                    
                logger.info("Matrices de factorisation sauvegardées en base de données")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des matrices: {e}")
    
    def _compute_user_similarities(self, user_id: int, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Calcule les similarités entre un utilisateur et les autres utilisateurs.
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum d'utilisateurs similaires à renvoyer
            
        Returns:
            Liste de tuples (user_id, similarité)
        """
        # Si les matrices de similarité ne sont pas disponibles, les charger
        if self.user_similarity_matrix is None:
            # Charger les données d'interaction
            interactions_df = self._load_interaction_data()
            
            if interactions_df.empty:
                logger.warning("Pas de données d'interaction disponibles")
                return []
                
            # Créer les matrices d'interaction
            self._create_interaction_matrices(interactions_df)
            
            # Calculer les similarités
            self._compute_similarity_matrices()
        
        # Vérifier si l'utilisateur est dans la matrice
        if user_id not in self.user_id_to_index:
            logger.warning(f"Utilisateur {user_id} non trouvé dans la matrice")
            return []
            
        # Récupérer l'index de l'utilisateur
        user_idx = self.user_id_to_index[user_id]
        
        # Récupérer les similarités
        similarities = self.user_similarity_matrix[user_idx]
        
        # Trier les similarités
        similar_indices = np.argsort(-similarities)
        
        # Filtrer l'utilisateur lui-même et limiter le nombre de résultats
        similar_users = []
        count = 0
        
        for idx in similar_indices:
            if idx != user_idx:  # Exclure l'utilisateur lui-même
                similar_id = self.index_to_user_id[idx]
                similarity = float(similarities[idx])
                
                if similarity >= self.similarity_threshold:
                    similar_users.append((similar_id, similarity))
                    count += 1
                    
                    if count >= limit:
                        break
        
        return similar_users
    
    def _save_user_similarities(self, user_id: int, similarities: List[Tuple[int, float]]):
        """
        Sauvegarde les similarités calculées en base de données.
        
        Args:
            user_id: ID de l'utilisateur
            similarities: Liste de tuples (user_id, similarité)
        """
        try:
            if self.engine is None:
                logger.warning("Connexion à la base de données non disponible")
                return
                
            with self.engine.connect() as conn:
                # Supprimer les similarités existantes
                delete_query = """
                DELETE FROM user_similarities
                WHERE user_id_1 = :user_id
                """
                
                conn.execute(text(delete_query), {"user_id": user_id})
                
                # Insérer les nouvelles similarités
                for similar_id, similarity in similarities:
                    insert_query = """
                    INSERT INTO user_similarities 
                    (user_id_1, user_id_2, similarity_score, last_computed)
                    VALUES (:user_id_1, :user_id_2, :similarity, CURRENT_TIMESTAMP)
                    """
                    
                    conn.execute(text(insert_query), {
                        "user_id_1": user_id,
                        "user_id_2": similar_id,
                        "similarity": similarity
                    })
                
                conn.commit()
                
            logger.debug(f"Similarités pour l'utilisateur {user_id} sauvegardées en base de données")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des similarités: {e}")
