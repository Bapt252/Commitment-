"""Module pour l'accès aux données de feedback."""

import logging
import json
from datetime import datetime
import uuid
import os
from sqlalchemy import create_engine, Column, String, JSON, Integer, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/nexten')
Base = declarative_base()

class FeedbackModel(Base):
    """Modèle ORM pour la table de feedback."""
    __tablename__ = 'feedbacks'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True, index=True)
    content = Column(String, nullable=False)
    source = Column(String, nullable=False)
    type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    sentiment = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    satisfaction_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class FeedbackRepository:
    """Repository pour accéder et manipuler les données de feedback."""
    
    def __init__(self):
        """Initialise le repository avec une connexion à la base de données."""
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self._ensure_table_exists()
        logger.info("FeedbackRepository initialisé")
    
    def _ensure_table_exists(self):
        """Crée la table si elle n'existe pas déjà."""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Tables créées ou déjà existantes")
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la création des tables: {str(e)}")
    
    def save(self, feedback_data):
        """Sauvegarde un nouveau feedback dans la base de données."""
        session = self.Session()
        try:
            # S'assurer que l'ID est présent
            if 'id' not in feedback_data:
                feedback_data['id'] = str(uuid.uuid4())
            
            # Convertir les types complexes en JSON
            for field in ['context', 'sentiment', 'topics']:
                if field in feedback_data and feedback_data[field] is not None:
                    if isinstance(feedback_data[field], (dict, list)):
                        feedback_data[field] = json.dumps(feedback_data[field])
            
            # Convertir les dates ISO en objets datetime
            if 'created_at' in feedback_data and isinstance(feedback_data['created_at'], str):
                feedback_data['created_at'] = datetime.fromisoformat(feedback_data['created_at'])
            
            # Créer le modèle
            feedback = FeedbackModel(**feedback_data)
            
            # Sauvegarder
            session.add(feedback)
            session.commit()
            
            logger.info(f"Feedback sauvegardé avec ID: {feedback.id}")
            return feedback.id
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la sauvegarde du feedback: {str(e)}")
            raise
        finally:
            session.close()
    
    def update(self, feedback_id, data):
        """Met à jour un feedback existant."""
        session = self.Session()
        try:
            # Récupérer le feedback
            feedback = session.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
            
            if not feedback:
                logger.warning(f"Tentative de mise à jour d'un feedback inexistant: {feedback_id}")
                return False
            
            # Mettre à jour les champs
            for key, value in data.items():
                if key in ['sentiment', 'topics', 'context'] and value is not None:
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                setattr(feedback, key, value)
            
            # Mettre à jour la date de modification
            feedback.updated_at = datetime.now()
            
            # Sauvegarder
            session.commit()
            
            logger.info(f"Feedback mis à jour avec ID: {feedback_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la mise à jour du feedback: {str(e)}")
            return False
        finally:
            session.close()
    
    def find_by_id(self, feedback_id):
        """Récupère un feedback par son ID."""
        session = self.Session()
        try:
            feedback = session.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
            
            if not feedback:
                return None
            
            # Convertir en dictionnaire
            feedback_dict = self._model_to_dict(feedback)
            
            return feedback_dict
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du feedback: {str(e)}")
            return None
        finally:
            session.close()
    
    def find_all(self, filters=None):
        """Récupère tous les feedbacks correspondant aux filtres."""
        session = self.Session()
        try:
            query = session.query(FeedbackModel)
            
            # Appliquer les filtres
            if filters:
                if 'user_id' in filters:
                    query = query.filter(FeedbackModel.user_id == filters['user_id'])
                if 'source' in filters:
                    query = query.filter(FeedbackModel.source == filters['source'])
                if 'type' in filters:
                    query = query.filter(FeedbackModel.type == filters['type'])
                if 'category' in filters:
                    query = query.filter(FeedbackModel.category == filters['category'])
                if 'start_date' in filters:
                    start_date = datetime.fromisoformat(filters['start_date'])
                    query = query.filter(FeedbackModel.created_at >= start_date)
                if 'end_date' in filters:
                    end_date = datetime.fromisoformat(filters['end_date'])
                    query = query.filter(FeedbackModel.created_at <= end_date)
            
            # Exécuter la requête
            feedbacks = query.all()
            
            # Convertir en liste de dictionnaires
            feedback_list = [self._model_to_dict(feedback) for feedback in feedbacks]
            
            return feedback_list
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des feedbacks: {str(e)}")
            return []
        finally:
            session.close()
    
    def _model_to_dict(self, model):
        """Convertit un modèle SQLAlchemy en dictionnaire."""
        # Obtenir tous les attributs du modèle
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            
            # Traiter les types spéciaux
            if isinstance(value, datetime):
                value = value.isoformat()
            elif column.name in ['sentiment', 'topics', 'context'] and value is not None:
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            
            result[column.name] = value
        
        return result
    
    def delete(self, feedback_id):
        """Supprime un feedback par son ID."""
        session = self.Session()
        try:
            feedback = session.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
            
            if not feedback:
                logger.warning(f"Tentative de suppression d'un feedback inexistant: {feedback_id}")
                return False
            
            session.delete(feedback)
            session.commit()
            
            logger.info(f"Feedback supprimé avec ID: {feedback_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Erreur lors de la suppression du feedback: {str(e)}")
            return False
        finally:
            session.close()
