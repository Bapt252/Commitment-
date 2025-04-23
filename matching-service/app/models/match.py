from typing import Optional, Dict, Any
import json

class Match:
    """Modèle représentant un matching entre un candidat et une offre d'emploi."""
    
    def __init__(self, id: int, candidate_id: int, job_id: int, match_score: float, 
                 status: str, match_details: Optional[Dict] = None):
        self.id = id
        self.candidate_id = candidate_id
        self.job_id = job_id
        self.match_score = match_score
        self.status = status
        self.match_details = match_details
    
    @classmethod
    def get_by_id(cls, conn, match_id: int) -> Optional['Match']:
        """Récupère un match par son ID."""
        query = """
        SELECT id, candidate_id, job_id, match_score, status, match_details
        FROM matching.matches
        WHERE id = %s
        """
        
        row = conn.execute(query, (match_id,)).fetchone()
        
        if not row:
            return None
        
        return cls(
            id=row[0],
            candidate_id=row[1],
            job_id=row[2],
            match_score=row[3],
            status=row[4],
            match_details=row[5]
        )
    
    @classmethod
    def get_by_candidate_and_job(cls, conn, candidate_id: int, job_id: int) -> Optional['Match']:
        """Récupère un match par l'ID du candidat et l'ID du job."""
        query = """
        SELECT id, candidate_id, job_id, match_score, status, match_details
        FROM matching.matches
        WHERE candidate_id = %s AND job_id = %s
        """
        
        row = conn.execute(query, (candidate_id, job_id)).fetchone()
        
        if not row:
            return None
        
        return cls(
            id=row[0],
            candidate_id=row[1],
            job_id=row[2],
            match_score=row[3],
            status=row[4],
            match_details=row[5]
        )
    
    @classmethod
    def create(cls, conn, candidate_id: int, job_id: int, match_score: float, 
              status: str = 'pending', match_details: Optional[Dict] = None) -> int:
        """Crée un nouveau match."""
        query = """
        INSERT INTO matching.matches (candidate_id, job_id, match_score, status, match_details, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
        """
        
        result = conn.execute(
            query, 
            (candidate_id, job_id, match_score, status, match_details)
        ).fetchone()
        
        conn.commit()
        return result[0]
    
    @classmethod
    def update(cls, conn, match_id: int, match_score: Optional[float] = None, 
              status: Optional[str] = None, match_details: Optional[Dict] = None) -> bool:
        """Met à jour un match existant."""
        # Construire la requête dynamiquement en fonction des champs à mettre à jour
        fields = []
        values = []
        
        if match_score is not None:
            fields.append("match_score = %s")
            values.append(match_score)
            
        if status is not None:
            fields.append("status = %s")
            values.append(status)
            
        if match_details is not None:
            fields.append("match_details = %s")
            values.append(match_details)
            
        # Ajouter updated_at
        fields.append("updated_at = NOW()")
        
        # Si aucun champ à mettre à jour, retourner False
        if not fields:
            return False
        
        # Construire et exécuter la requête
        query = f"""
        UPDATE matching.matches
        SET {', '.join(fields)}
        WHERE id = %s
        """
        
        values.append(match_id)
        
        conn.execute(query, values)
        conn.commit()
        
        return True
    
    @classmethod
    def create_or_update(cls, conn, candidate_id: int, job_id: int, match_score: float, 
                      status: str = 'pending', match_details: Optional[Dict] = None) -> int:
        """Crée ou met à jour un match selon qu'il existe déjà ou non."""
        # Vérifier si le match existe déjà
        existing_match = cls.get_by_candidate_and_job(conn, candidate_id, job_id)
        
        if existing_match:
            # Mettre à jour le match existant
            cls.update(conn, existing_match.id, match_score, status, match_details)
            return existing_match.id
        else:
            # Créer un nouveau match
            return cls.create(conn, candidate_id, job_id, match_score, status, match_details)