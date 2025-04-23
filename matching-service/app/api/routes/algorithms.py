from flask import Blueprint, jsonify, request, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json

from app.core.matching import get_algorithms, get_algorithm_by_id, create_algorithm, update_algorithm
from app.utils.db import get_db_connection

# Blueprint pour les algorithmes
algorithms_bp = Blueprint('algorithms', __name__, url_prefix='/algorithms')

# Modèles Pydantic pour la validation
class AlgorithmParameters(BaseModel):
    skills_weight: float = Field(..., ge=0.0, le=1.0, description="Poids pour les compétences")
    experience_weight: float = Field(..., ge=0.0, le=1.0, description="Poids pour l'expérience")
    location_weight: float = Field(..., ge=0.0, le=1.0, description="Poids pour la localisation")
    skills_params: Optional[Dict[str, Any]] = Field(None, description="Paramètres spécifiques pour l'évaluation des compétences")
    experience_params: Optional[Dict[str, Any]] = Field(None, description="Paramètres spécifiques pour l'évaluation de l'expérience")
    location_params: Optional[Dict[str, Any]] = Field(None, description="Paramètres spécifiques pour l'évaluation de la localisation")

class AlgorithmCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Nom de l'algorithme")
    description: Optional[str] = Field(None, description="Description de l'algorithme")
    parameters: AlgorithmParameters = Field(..., description="Paramètres de l'algorithme")
    is_active: Optional[bool] = Field(False, description="Si l'algorithme est actif")

class AlgorithmUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Nom de l'algorithme")
    description: Optional[str] = Field(None, description="Description de l'algorithme")
    parameters: Optional[AlgorithmParameters] = Field(None, description="Paramètres de l'algorithme")
    is_active: Optional[bool] = Field(None, description="Si l'algorithme est actif")

@algorithms_bp.route('', methods=['GET'])
@jwt_required()
def list_algorithms():
    """Liste tous les algorithmes de matching disponibles."""
    conn = get_db_connection()
    try:
        algorithms = get_algorithms(conn)
        return jsonify({
            'algorithms': algorithms,
            'count': len(algorithms)
        })
    finally:
        conn.close()

@algorithms_bp.route('/<int:algorithm_id>', methods=['GET'])
@jwt_required()
def get_algorithm(algorithm_id):
    """Récupère les détails d'un algorithme spécifique."""
    conn = get_db_connection()
    try:
        algorithm = get_algorithm_by_id(conn, algorithm_id)
        
        if not algorithm:
            return jsonify({
                'error': 'Algorithme non trouvé'
            }), 404
            
        return jsonify(algorithm)
    finally:
        conn.close()

@algorithms_bp.route('', methods=['POST'])
@jwt_required()
@validate()
def create_new_algorithm(body: AlgorithmCreate):
    """Crée un nouvel algorithme de matching."""
    user_identity = get_jwt_identity()
    
    # Vérifier si l'utilisateur est administrateur
    if user_identity['user_type'] != 'admin':
        return jsonify({
            'error': 'Permission refusée. Seuls les administrateurs peuvent créer des algorithmes'
        }), 403
    
    conn = get_db_connection()
    try:
        # Conversion du modèle Pydantic en dictionnaire
        algorithm_data = body.dict()
        parameters = algorithm_data['parameters']
        
        # Vérifier que les poids totalisent 1.0
        weights_sum = parameters['skills_weight'] + parameters['experience_weight'] + parameters['location_weight']
        if not 0.99 <= weights_sum <= 1.01:  # Permettre une petite marge d'erreur
            return jsonify({
                'error': 'La somme des poids doit être égale à 1.0'
            }), 400
        
        # Convertir les paramètres en JSON
        algorithm_data['parameters'] = json.dumps(parameters)
        
        # Créer l'algorithme
        algorithm_id = create_algorithm(conn, algorithm_data)
        
        # Récupérer l'algorithme créé pour le retourner
        algorithm = get_algorithm_by_id(conn, algorithm_id)
        
        return jsonify(algorithm), 201
    finally:
        conn.close()

@algorithms_bp.route('/<int:algorithm_id>', methods=['PUT'])
@jwt_required()
@validate()
def update_existing_algorithm(algorithm_id: int, body: AlgorithmUpdate):
    """Met à jour un algorithme existant."""
    user_identity = get_jwt_identity()
    
    # Vérifier si l'utilisateur est administrateur
    if user_identity['user_type'] != 'admin':
        return jsonify({
            'error': 'Permission refusée. Seuls les administrateurs peuvent modifier des algorithmes'
        }), 403
    
    conn = get_db_connection()
    try:
        # Vérifier si l'algorithme existe
        existing_algorithm = get_algorithm_by_id(conn, algorithm_id)
        if not existing_algorithm:
            return jsonify({
                'error': 'Algorithme non trouvé'
            }), 404
        
        # Conversion du modèle Pydantic en dictionnaire
        update_data = {k: v for k, v in body.dict().items() if v is not None}
        
        # Traitement des paramètres si fournis
        if 'parameters' in update_data:
            parameters = update_data['parameters']
            
            # Vérifier que les poids totalisent 1.0
            weights_sum = parameters.get('skills_weight', 0) + \
                         parameters.get('experience_weight', 0) + \
                         parameters.get('location_weight', 0)
                         
            if weights_sum > 0 and not 0.99 <= weights_sum <= 1.01:  # Permettre une petite marge d'erreur
                return jsonify({
                    'error': 'La somme des poids doit être égale à 1.0'
                }), 400
            
            # Convertir les paramètres en JSON
            update_data['parameters'] = json.dumps(parameters)
        
        # Mettre à jour l'algorithme
        update_algorithm(conn, algorithm_id, update_data)
        
        # Récupérer l'algorithme mis à jour pour le retourner
        updated_algorithm = get_algorithm_by_id(conn, algorithm_id)
        
        return jsonify(updated_algorithm)
    finally:
        conn.close()