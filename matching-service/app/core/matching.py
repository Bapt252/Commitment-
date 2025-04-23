from typing import List, Dict, Any, Optional, Tuple
import json

def calculate_match(conn, candidate_id: int, job_id: int, algorithm_id: Optional[int] = None) -> Dict[str, Any]:
    """Calcule un score de matching entre un candidat et une offre d'emploi."""
    query = """
    SELECT m.total_score, m.score_breakdown, m.match_quality
    FROM calculate_match_score(%s, %s, %s) m
    """
    
    result = conn.execute(query, (candidate_id, job_id, algorithm_id)).fetchone()
    
    if not result:
        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "score": 0.0,
            "breakdown": {},
            "quality": "poor"
        }
    
    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "score": float(result[0]),
        "breakdown": result[1],
        "quality": result[2]
    }

def get_matches_for_job(conn, job_id: int, algorithm_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Récupère les meilleurs candidats pour une offre d'emploi."""
    query = """
    SELECT c.id AS candidate_id, 
           c.first_name, 
           c.last_name, 
           m.total_score, 
           m.match_quality
    FROM matching.candidate_profiles c
    CROSS JOIN LATERAL calculate_match_score(c.id, %s, %s) m
    WHERE m.total_score > 50
    ORDER BY m.total_score DESC
    LIMIT %s
    """
    
    results = conn.execute(query, (job_id, algorithm_id, limit)).fetchall()
    
    matches = [
        {
            "candidate_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "score": float(row[3]),
            "quality": row[4]
        }
        for row in results
    ]
    
    return matches

def get_matches_for_candidate(conn, candidate_id: int, algorithm_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Récupère les meilleures offres d'emploi pour un candidat."""
    query = """
    SELECT j.id AS job_id, 
           j.title, 
           c.name AS company_name,
           m.total_score, 
           m.match_quality
    FROM matching.job_listings j
    JOIN profiles.companies c ON j.company_id = c.id
    CROSS JOIN LATERAL calculate_match_score(%s, j.id, %s) m
    WHERE m.total_score > 50
    ORDER BY m.total_score DESC
    LIMIT %s
    """
    
    results = conn.execute(query, (candidate_id, algorithm_id, limit)).fetchall()
    
    matches = [
        {
            "job_id": row[0],
            "job_title": row[1],
            "company_name": row[2],
            "score": float(row[3]),
            "quality": row[4]
        }
        for row in results
    ]
    
    return matches

def get_algorithms(conn) -> List[Dict[str, Any]]:
    """Récupère la liste des algorithmes de matching disponibles."""
    query = """
    SELECT id, name, description, parameters, is_active, created_at, updated_at
    FROM matching.matching_algorithms
    ORDER BY id
    """
    
    results = conn.execute(query).fetchall()
    
    algorithms = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "parameters": row[3],
            "is_active": row[4],
            "created_at": row[5].isoformat() if row[5] else None,
            "updated_at": row[6].isoformat() if row[6] else None
        }
        for row in results
    ]
    
    return algorithms

def get_algorithm_by_id(conn, algorithm_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un algorithme spécifique par son ID."""
    query = """
    SELECT id, name, description, parameters, is_active, created_at, updated_at
    FROM matching.matching_algorithms
    WHERE id = %s
    """
    
    row = conn.execute(query, (algorithm_id,)).fetchone()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "parameters": row[3],
        "is_active": row[4],
        "created_at": row[5].isoformat() if row[5] else None,
        "updated_at": row[6].isoformat() if row[6] else None
    }

def create_algorithm(conn, algorithm_data: Dict[str, Any]) -> int:
    """Crée un nouvel algorithme de matching."""
    query = """
    INSERT INTO matching.matching_algorithms (name, description, parameters, is_active, created_at, updated_at)
    VALUES (%s, %s, %s, %s, NOW(), NOW())
    RETURNING id
    """
    
    result = conn.execute(
        query, 
        (
            algorithm_data['name'],
            algorithm_data.get('description'),
            algorithm_data['parameters'],
            algorithm_data.get('is_active', False)
        )
    ).fetchone()
    
    conn.commit()
    return result[0]

def update_algorithm(conn, algorithm_id: int, update_data: Dict[str, Any]) -> bool:
    """Met à jour un algorithme existant."""
    # Construire la requête dynamiquement en fonction des champs à mettre à jour
    fields = []
    values = []
    
    if 'name' in update_data:
        fields.append("name = %s")
        values.append(update_data['name'])
        
    if 'description' in update_data:
        fields.append("description = %s")
        values.append(update_data['description'])
        
    if 'parameters' in update_data:
        fields.append("parameters = %s")
        values.append(update_data['parameters'])
        
    if 'is_active' in update_data:
        fields.append("is_active = %s")
        values.append(update_data['is_active'])
        
    # Si l'algorithme est activé, désactiver tous les autres
    if update_data.get('is_active', False):
        conn.execute(
            "UPDATE matching.matching_algorithms SET is_active = FALSE WHERE id != %s",
            (algorithm_id,)
        )
    
    # Ajouter updated_at
    fields.append("updated_at = NOW()")
    
    # Si aucun champ à mettre à jour, retourner False
    if not fields:
        return False
    
    # Construire et exécuter la requête
    query = f"""
    UPDATE matching.matching_algorithms
    SET {', '.join(fields)}
    WHERE id = %s
    """
    
    values.append(algorithm_id)
    
    conn.execute(query, values)
    conn.commit()
    
    return True