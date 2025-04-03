from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any

router = APIRouter()

@router.get("/")
def get_users():
    return {"message": "Liste des utilisateurs"}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": "Exemple d'utilisateur"}