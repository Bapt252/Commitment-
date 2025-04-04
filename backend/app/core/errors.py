from fastapi import HTTPException, status
import logging
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)

class CommitmentAPIError(Exception):
    """
    Exception personnalisée pour l'API Commitment.
    Permet de définir un code d'erreur HTTP et un message détaillé.
    """
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

def handle_exceptions(exc: Exception) -> Union[Dict[str, Any], HTTPException]:
    """
    Fonction centrale pour la gestion des erreurs.
    Peut être utilisée comme décorateur ou appelée explicitement.
    """
    if isinstance(exc, CommitmentAPIError):
        # Si c'est déjà une exception formatée, la renvoyer telle quelle
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail
        )
    elif isinstance(exc, HTTPException):
        # Si c'est déjà une HTTPException, la renvoyer telle quelle
        raise exc
    else:
        # Pour les autres exceptions, logger et renvoyer une erreur 500
        logger.error(f"Exception non gérée: {str(exc)}", exc_info=True)
        
        # En production, ne pas exposer les détails de l'erreur
        # En développement, on pourrait inclure str(exc) dans le message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite. Notre équipe a été notifiée."
        )

def validation_error(detail: str) -> HTTPException:
    """
    Crée une erreur de validation (400 Bad Request)
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )

def not_found_error(entity_type: str, entity_id: Any) -> HTTPException:
    """
    Crée une erreur pour une ressource non trouvée (404 Not Found)
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity_type} avec l'id {entity_id} non trouvé"
    )

def unauthorized_error(detail: str = "Non autorisé") -> HTTPException:
    """
    Crée une erreur pour une accès non autorisé (401 Unauthorized)
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def forbidden_error(detail: str = "Accès interdit") -> HTTPException:
    """
    Crée une erreur pour un accès interdit (403 Forbidden)
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )

def conflict_error(detail: str) -> HTTPException:
    """
    Crée une erreur pour un conflit (409 Conflict), par exemple quand une ressource existe déjà
    """
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail
    )

def too_many_requests_error(detail: str = "Trop de requêtes, veuillez réessayer plus tard") -> HTTPException:
    """
    Crée une erreur pour limite de taux dépassée (429 Too Many Requests)
    """
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail
    )
