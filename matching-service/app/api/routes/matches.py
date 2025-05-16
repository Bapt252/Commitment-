from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.matching import calculate_match, get_matches_for_job, get_matches_for_candidate
from app.models.match import Match
from app.utils.db import get_db_connection, setup_audit_context

# Blueprint pour les matchs
matches_bp = Blueprint('matches', __name__, url_prefix='/matches')

# Modèles Pydantic pour la validation
class CalculateMatchRequest(BaseModel):
    job_id: Optional[int] = Field(None, description="ID de l'offre d'emploi")
    candidate_id: Optional[int] = Field(None, description="ID du candidat")
    algorithm_id: Optional[int] = Field(None, description="ID de l'algorithme à utiliser")
    store_results: Optional[bool] = Field(False, description="Stocker les résultats en base de données")

class MatchStatusUpdate(BaseModel):
    status: str = Field(..., description="Nouveau statut du match", pattern='^(pending|viewed|interested|not_interested)$')

@matches_bp.route('/calculate', methods=['POST'])
@jwt_required()
@validate()
def calculate_match_score(body: CalculateMatchRequest):
    """Calcule les scores de matching pour un job ou un candidat"""
    job_id = body.job_id
    candidate_id = body.candidate_id
    algorithm_id = body.algorithm_id
    store_results = body.store_results
    
    if not job_id and not candidate_id:
        return jsonify({"error": "Either job_id or candidate_id is required"}), 400
    
    current_user = get_jwt_identity()
    user_id = current_user["id"]
    
    conn = get_db_connection()
    try:
        # Configuration du contexte d'audit
        setup_audit_context(conn, user_id, request.remote_addr)
        
        if job_id and not candidate_id:
            # Calculer le matching pour tous les candidats éligibles pour ce job
            matches = get_matches_for_job(conn, job_id, algorithm_id, limit=50)
            
            # Optionnel: stocker ces matches en base
            if store_results:
                for match in matches:
                    Match.create_or_update(
                        conn, 
                        candidate_id=match["candidate_id"],
                        job_id=job_id,
                        match_score=match["score"],
                        status="pending"
                    )
                
            return jsonify({
                "job_id": job_id,
                "matches": matches,
                "count": len(matches)
            })
            
        elif candidate_id and not job_id:
            # Calculer le matching pour ce candidat avec tous les jobs ouverts
            matches = get_matches_for_candidate(conn, candidate_id, algorithm_id, limit=50)
            
            # Optionnel: stocker ces matches en base
            if store_results:
                for match in matches:
                    Match.create_or_update(
                        conn, 
                        candidate_id=candidate_id,
                        job_id=match["job_id"],
                        match_score=match["score"],
                        status="pending"
                    )
            
            return jsonify({
                "candidate_id": candidate_id,
                "matches": matches,
                "count": len(matches)
            })
            
        else:
            # Calculer un seul match spécifique
            match_result = calculate_match(conn, candidate_id, job_id, algorithm_id)
            
            # Stocker le résultat si demandé
            if store_results:
                Match.create_or_update(
                    conn, 
                    candidate_id=candidate_id,
                    job_id=job_id,
                    match_score=match_result["score"],
                    match_details=match_result["breakdown"],
                    status="pending"
                )
            
            return jsonify(match_result)
    finally:
        conn.close()

@matches_bp.route('/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_matches(job_id):
    """Récupère les matches existants pour une offre d'emploi"""
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    status = request.args.get('status', default=None, type=str)
    min_score = request.args.get('min_score', default=0, type=float)
    
    conn = get_db_connection()
    try:
        # Vérifier les permissions (l'utilisateur doit être lié à l'entreprise du job)
        current_user = get_jwt_identity()
        user_id = current_user["id"]
        user_type = current_user["user_type"]
        
        # Les administrateurs peuvent tout voir
        is_authorized = user_type == 'admin'
        
        # Les recruteurs peuvent voir les matches pour leurs propres jobs
        if user_type == 'company' and not is_authorized:
            query = """
            SELECT 1 FROM jobs.jobs j 
            JOIN profiles.companies c ON j.company_id = c.id 
            WHERE j.id = %s AND c.user_id = %s
            """
            result = conn.execute(query, (job_id, user_id)).fetchone()
            is_authorized = result is not None
        
        if not is_authorized:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Construire la requête avec filtres
        query_filters = ["job_id = %s"]
        query_params = [job_id]
        
        if status:
            query_filters.append("status = %s")
            query_params.append(status)
            
        if min_score > 0:
            query_filters.append("match_score >= %s")
            query_params.append(min_score)
        
        where_clause = " AND ".join(query_filters)
        
        # Récupérer les matches
        query = f"""
        SELECT m.id, m.candidate_id, m.job_id, m.match_score, m.status, 
               m.match_details, m.created_at, m.updated_at,
               c.first_name, c.last_name
        FROM matching.matches m
        JOIN profiles.candidates c ON m.candidate_id = c.id
        WHERE {where_clause}
        ORDER BY m.match_score DESC
        LIMIT %s OFFSET %s
        """
        
        query_params.extend([limit, offset])
        matches = conn.execute(query, query_params).fetchall()
        
        # Compter le nombre total de matches
        count_query = f"SELECT COUNT(*) FROM matching.matches WHERE {where_clause}"
        total_count = conn.execute(count_query, query_params[:-2]).fetchone()[0]
        
        # Formater les résultats
        formatted_matches = [{
            "id": match[0],
            "candidate_id": match[1],
            "job_id": match[2],
            "score": float(match[3]),
            "status": match[4],
            "details": match[5],
            "created_at": match[6].isoformat() if match[6] else None,
            "updated_at": match[7].isoformat() if match[7] else None,
            "candidate_name": f"{match[8]} {match[9]}"
        } for match in matches]
        
        return jsonify({
            "job_id": job_id,
            "matches": formatted_matches,
            "count": len(formatted_matches),
            "total": total_count
        })
    finally:
        conn.close()

@matches_bp.route('/candidate/<int:candidate_id>', methods=['GET'])
@jwt_required()
def get_candidate_matches(candidate_id):
    """Récupère les matches existants pour un candidat"""
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    status = request.args.get('status', default=None, type=str)
    min_score = request.args.get('min_score', default=0, type=float)
    
    conn = get_db_connection()
    try:
        # Vérifier les permissions (l'utilisateur doit être le candidat lui-même ou un admin)
        current_user = get_jwt_identity()
        user_id = current_user["id"]
        user_type = current_user["user_type"]
        
        # Les administrateurs peuvent tout voir
        is_authorized = user_type == 'admin'
        
        # Les candidats peuvent voir leurs propres matches
        if user_type == 'candidate' and not is_authorized:
            query = "SELECT 1 FROM profiles.candidates WHERE id = %s AND user_id = %s"
            result = conn.execute(query, (candidate_id, user_id)).fetchone()
            is_authorized = result is not None
        
        if not is_authorized:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Construire la requête avec filtres
        query_filters = ["candidate_id = %s"]
        query_params = [candidate_id]
        
        if status:
            query_filters.append("status = %s")
            query_params.append(status)
            
        if min_score > 0:
            query_filters.append("match_score >= %s")
            query_params.append(min_score)
        
        where_clause = " AND ".join(query_filters)
        
        # Récupérer les matches
        query = f"""
        SELECT m.id, m.candidate_id, m.job_id, m.match_score, m.status, 
               m.match_details, m.created_at, m.updated_at,
               j.title AS job_title, c.name AS company_name
        FROM matching.matches m
        JOIN jobs.jobs j ON m.job_id = j.id
        JOIN profiles.companies c ON j.company_id = c.id
        WHERE {where_clause}
        ORDER BY m.match_score DESC
        LIMIT %s OFFSET %s
        """
        
        query_params.extend([limit, offset])
        matches = conn.execute(query, query_params).fetchall()
        
        # Compter le nombre total de matches
        count_query = f"SELECT COUNT(*) FROM matching.matches WHERE {where_clause}"
        total_count = conn.execute(count_query, query_params[:-2]).fetchone()[0]
        
        # Formater les résultats
        formatted_matches = [{
            "id": match[0],
            "candidate_id": match[1],
            "job_id": match[2],
            "score": float(match[3]),
            "status": match[4],
            "details": match[5],
            "created_at": match[6].isoformat() if match[6] else None,
            "updated_at": match[7].isoformat() if match[7] else None,
            "job_title": match[8],
            "company_name": match[9]
        } for match in matches]
        
        return jsonify({
            "candidate_id": candidate_id,
            "matches": formatted_matches,
            "count": len(formatted_matches),
            "total": total_count
        })
    finally:
        conn.close()

@matches_bp.route('/<int:match_id>', methods=['GET'])
@jwt_required()
def get_match(match_id):
    """Récupère les détails d'un match spécifique"""
    conn = get_db_connection()
    try:
        query = """
        SELECT m.id, m.candidate_id, m.job_id, m.match_score, m.status, 
               m.match_details, m.created_at, m.updated_at,
               c.first_name, c.last_name,
               j.title AS job_title, comp.name AS company_name
        FROM matching.matches m
        JOIN profiles.candidates c ON m.candidate_id = c.id
        JOIN jobs.jobs j ON m.job_id = j.id
        JOIN profiles.companies comp ON j.company_id = comp.id
        WHERE m.id = %s
        """
        
        match = conn.execute(query, (match_id,)).fetchone()
        
        if not match:
            return jsonify({"error": "Match not found"}), 404
        
        # Vérifier les permissions
        current_user = get_jwt_identity()
        user_id = current_user["id"]
        user_type = current_user["user_type"]
        
        # Les administrateurs peuvent tout voir
        is_authorized = user_type == 'admin'
        
        # Les candidats peuvent voir leurs propres matches
        if user_type == 'candidate' and not is_authorized:
            query = "SELECT 1 FROM profiles.candidates WHERE id = %s AND user_id = %s"
            result = conn.execute(query, (match[1], user_id)).fetchone()
            is_authorized = result is not None
        
        # Les recruteurs peuvent voir les matches pour leurs propres jobs
        if user_type == 'company' and not is_authorized:
            query = """
            SELECT 1 FROM jobs.jobs j 
            JOIN profiles.companies c ON j.company_id = c.id 
            WHERE j.id = %s AND c.user_id = %s
            """
            result = conn.execute(query, (match[2], user_id)).fetchone()
            is_authorized = result is not None
        
        if not is_authorized:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Formater le résultat
        formatted_match = {
            "id": match[0],
            "candidate_id": match[1],
            "job_id": match[2],
            "score": float(match[3]),
            "status": match[4],
            "details": match[5],
            "created_at": match[6].isoformat() if match[6] else None,
            "updated_at": match[7].isoformat() if match[7] else None,
            "candidate": {
                "id": match[1],
                "name": f"{match[8]} {match[9]}"
            },
            "job": {
                "id": match[2],
                "title": match[10],
                "company": match[11]
            }
        }
        
        return jsonify(formatted_match)
    finally:
        conn.close()

@matches_bp.route('/<int:match_id>/status', methods=['PUT'])
@jwt_required()
@validate()
def update_match_status(match_id: int, body: MatchStatusUpdate):
    """Met à jour le statut d'un match"""
    new_status = body.status
    
    conn = get_db_connection()
    try:
        # Récupérer le match actuel
        query = "SELECT candidate_id, job_id, status FROM matching.matches WHERE id = %s"
        match = conn.execute(query, (match_id,)).fetchone()
        
        if not match:
            return jsonify({"error": "Match not found"}), 404
        
        candidate_id, job_id, current_status = match
        
        # Vérifier les permissions
        current_user = get_jwt_identity()
        user_id = current_user["id"]
        user_type = current_user["user_type"]
        
        # Les administrateurs peuvent tout modifier
        is_authorized = user_type == 'admin'
        
        # Les candidats peuvent modifier le statut de leurs propres matches
        if user_type == 'candidate' and not is_authorized:
            query = "SELECT 1 FROM profiles.candidates WHERE id = %s AND user_id = %s"
            result = conn.execute(query, (candidate_id, user_id)).fetchone()
            is_authorized = result is not None
            
            # Les candidats ne peuvent changer que pour 'viewed', 'interested' ou 'not_interested'
            if is_authorized and new_status not in ['viewed', 'interested', 'not_interested']:
                return jsonify({"error": "Candidates can only set status to 'viewed', 'interested' or 'not_interested'"}), 403
        
        # Les recruteurs peuvent modifier le statut pour leurs propres jobs
        if user_type == 'company' and not is_authorized:
            query = """
            SELECT 1 FROM jobs.jobs j 
            JOIN profiles.companies c ON j.company_id = c.id 
            WHERE j.id = %s AND c.user_id = %s
            """
            result = conn.execute(query, (job_id, user_id)).fetchone()
            is_authorized = result is not None
            
            # Les recruteurs ne peuvent changer que pour 'pending' (reset) ou 'viewed'
            if is_authorized and new_status not in ['pending', 'viewed']:
                return jsonify({"error": "Recruiters can only set status to 'pending' or 'viewed'"}), 403
        
        if not is_authorized:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Configuration du contexte d'audit
        setup_audit_context(conn, user_id, request.remote_addr)
        
        # Mettre à jour le statut
        update_query = """
        UPDATE matching.matches 
        SET status = %s, updated_at = NOW() 
        WHERE id = %s
        """
        conn.execute(update_query, (new_status, match_id))
        conn.commit()
        
        return jsonify({
            "id": match_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "previous_status": current_status,
            "status": new_status,
            "updated_at": conn.execute("SELECT NOW()").fetchone()[0].isoformat()
        })
    finally:
        conn.close()