from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models import DocumentPermission
import httpx
from pydantic import UUID4

# OAuth2 scheme pour l'authentification par token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crée un JWT token avec les données fournies et une date d'expiration
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt, expire


def verify_token(token: str) -> dict:
    """
    Vérifie un token JWT et retourne les données contenues
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Récupère l'utilisateur courant à partir du token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Vérifier si l'utilisateur existe toujours (appel à l'API principale)
        # Cette vérification peut être désactivée dans certains cas pour des raisons de performance
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.API_BASE_URL}/users/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                user_data = response.json()
        except Exception as e:
            # Si l'API principale n'est pas disponible, on continue avec les données du token
            # mais on pourrait aussi lever une exception selon les besoins de sécurité
            user_data = {
                "id": user_id,
                "email": payload.get("email", ""),
                "is_active": True,
                "roles": payload.get("roles", [])
            }
        
        return user_data
        
    except JWTError:
        raise credentials_exception


def get_user_roles(user):
    """
    Extrait les rôles de l'utilisateur depuis les données utilisateur
    """
    return user.get("roles", [])


def check_document_permission(
    db: Session, 
    document_id: UUID4, 
    user_id: UUID4, 
    permission_type: str
) -> bool:
    """
    Vérifie si un utilisateur a une permission spécifique sur un document
    """
    # Vérifier les permissions directes
    direct_permission = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id,
        DocumentPermission.entity_type == "user",
        DocumentPermission.entity_id == user_id,
        DocumentPermission.permission_type == permission_type
    ).first()
    
    if direct_permission:
        # Vérifier si la permission n'est pas expirée
        if direct_permission.expires_at and direct_permission.expires_at < datetime.utcnow():
            return False
        return True
    
    # Vérifier les permissions via les rôles
    # Généralement, on obtiendrait les rôles utilisateur via un service AUTH
    # Ici, on utilise une fonction factice pour l'illustration
    user_roles = ["user_role_1", "user_role_2"]  # À remplacer par get_user_roles(user_id)
    
    role_permission = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id,
        DocumentPermission.entity_type == "role",
        DocumentPermission.entity_id.in_(user_roles),
        DocumentPermission.permission_type == permission_type
    ).first()
    
    if role_permission:
        # Vérifier si la permission n'est pas expirée
        if role_permission.expires_at and role_permission.expires_at < datetime.utcnow():
            return False
        return True
    
    return False


def log_access_attempt(
    db: Session, 
    document_id: UUID4, 
    user_id: UUID4, 
    access_type: str, 
    success: bool,
    request: Request
):
    """
    Enregistre une tentative d'accès pour audit
    """
    from models import DocumentAccessLog
    
    log_entry = DocumentAccessLog(
        document_id=document_id,
        user_id=user_id,
        access_type=access_type,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        request_id=uuid.uuid4(),  # Ou récupérer d'un middleware de traçage
        success=success
    )
    db.add(log_entry)
    db.commit()


def get_accessible_documents(db: Session, user_id: UUID4) -> List[UUID4]:
    """
    Récupère la liste des documents accessibles par l'utilisateur
    """
    # Récupérer les documents avec permission directe
    direct_permissions = db.query(DocumentPermission.document_id).filter(
        DocumentPermission.entity_type == "user",
        DocumentPermission.entity_id == user_id,
        DocumentPermission.expires_at.is_(None) | (DocumentPermission.expires_at > datetime.utcnow())
    ).all()
    
    # Récupérer les rôles de l'utilisateur
    user_roles = ["user_role_1", "user_role_2"]  # À remplacer par get_user_roles(user_id)
    
    # Récupérer les documents avec permission via rôle
    role_permissions = db.query(DocumentPermission.document_id).filter(
        DocumentPermission.entity_type == "role",
        DocumentPermission.entity_id.in_(user_roles),
        DocumentPermission.expires_at.is_(None) | (DocumentPermission.expires_at > datetime.utcnow())
    ).all()
    
    # Combiner les deux ensembles de résultats
    document_ids = set()
    for permission in direct_permissions:
        document_ids.add(permission.document_id)
    
    for permission in role_permissions:
        document_ids.add(permission.document_id)
    
    return list(document_ids)
