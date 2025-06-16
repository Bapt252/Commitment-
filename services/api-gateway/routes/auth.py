"""
Routes d'authentification JWT pour l'API Gateway
Gestion complète des tokens, login, refresh et logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import redis
import hashlib
import logging
from datetime import datetime, timedelta

from config.settings import get_settings
from utils.database import get_user_by_email, verify_password, create_user

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()

# Connection Redis pour blacklist des tokens
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Erreur connexion Redis: {e}")
    redis_client = None

router = APIRouter()

# Modèles Pydantic
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "candidat"  # candidat, recruteur, admin

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    is_active: bool

# Utilitaires JWT
def create_access_token(data: dict) -> str:
    """Créer un token d'accès JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Créer un token de refresh JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Vérifier et décoder un token JWT"""
    try:
        # Vérifier si le token est blacklisté
        if redis_client and redis_client.get(f"blacklist:{token}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token blacklisté"
            )
        
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )

def blacklist_token(token: str):
    """Ajouter un token à la blacklist"""
    if redis_client:
        try:
            # Décoder le token pour obtenir l'expiration
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if exp:
                # TTL = temps restant jusqu'à expiration
                ttl = exp - int(datetime.utcnow().timestamp())
                if ttl > 0:
                    redis_client.setex(f"blacklist:{token}", ttl, "1")
        except Exception as e:
            logger.error(f"Erreur blacklist token: {e}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency pour obtenir l'utilisateur actuel"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Type de token invalide"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    return payload

# Routes d'authentification
@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = await get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
        
        # Créer l'utilisateur
        user = await create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=request.role
        )
        
        # Générer les tokens
        access_token = create_access_token(data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        })
        
        refresh_token = create_refresh_token(data={
            "sub": str(user["id"]),
            "email": user["email"]
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_EXPIRE_HOURS * 3600,
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'inscription"
        )

@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Connexion utilisateur"""
    try:
        # Vérifier les identifiants
        user = await get_user_by_email(request.email)
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect"
            )
        
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Compte désactivé"
            )
        
        # Générer les tokens
        access_token = create_access_token(data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        })
        
        refresh_token = create_refresh_token(data={
            "sub": str(user["id"]),
            "email": user["email"]
        })
        
        logger.info(f"Connexion réussie pour {user['email']}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_EXPIRE_HOURS * 3600,
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur connexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion"
        )

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Renouveler le token d'accès"""
    try:
        payload = verify_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh invalide"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # Récupérer l'utilisateur pour le rôle
        user = await get_user_by_email(email)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé ou inactif"
            )
        
        # Générer un nouveau token d'accès
        access_token = create_access_token(data={
            "sub": user_id,
            "email": email,
            "role": user["role"]
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Même refresh token
            expires_in=settings.JWT_EXPIRE_HOURS * 3600,
            user={
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du renouvellement"
        )

@router.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Déconnexion et blacklist du token"""
    try:
        token = credentials.credentials
        blacklist_token(token)
        
        logger.info("Déconnexion réussie")
        return {"message": "Déconnexion réussie"}
        
    except Exception as e:
        logger.error(f"Erreur déconnexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la déconnexion"
        )

@router.get("/auth/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obtenir le profil de l'utilisateur connecté"""
    try:
        user = await get_user_by_email(current_user["email"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        return UserProfile(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            created_at=user["created_at"],
            is_active=user["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur profil utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du profil"
        )
