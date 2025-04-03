from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Schéma de base pour un utilisateur
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

# Schéma pour la création d'un utilisateur
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Schéma pour la mise à jour d'un utilisateur
class UserUpdate(UserBase):
    password: Optional[str] = None

# Schéma pour afficher un utilisateur
class User(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Schéma stocké en DB (contient le mot de passe hashé)
class UserInDB(User):
    hashed_password: str