from fastapi import APIRouter, HTTPException, Depends, Body, Request
from typing import Dict, Any, Optional, List
from ..tracking.privacy import PrivacyManager, ConsentOptions
import hashlib

router = APIRouter(prefix="/api/consent", tags=["consent"])

# Dépendance pour obtenir le gestionnaire de confidentialité
def get_privacy_manager() -> PrivacyManager:
    return PrivacyManager()  # En pratique, ceci serait un singleton

@router.post("/record", status_code=200)
async def record_user_consent(
    options: ConsentOptions,
    user_id: str,
    request: Request,
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Enregistrer le consentement utilisateur"""
    # Hacher l'IP pour l'audit (mais ne pas la stocker en clair)
    client_ip = request.client.host if request.client else None
    ip_hash = None
    if client_ip:
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    
    consent_id = privacy_manager.record_consent(user_id, options, ip_hash)
    return {"status": "success", "consent_id": consent_id}

@router.get("/status", status_code=200)
async def get_consent_status(
    user_id: str,
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Obtenir le statut actuel du consentement utilisateur"""
    if user_id not in privacy_manager.consent_store:
        raise HTTPException(status_code=404, detail="No consent record found")
    
    consent = privacy_manager.consent_store[user_id]
    return {
        "user_id": user_id,
        "options": consent.options.dict(),
        "timestamp": consent.timestamp,
        "version": consent.version
    }

@router.post("/withdraw", status_code=200)
async def withdraw_consent(
    user_id: str,
    options: Optional[List[str]] = None,  # Options spécifiques à retirer
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    """Retirer le consentement (partiellement ou totalement)"""
    if user_id not in privacy_manager.consent_store:
        raise HTTPException(status_code=404, detail="No consent record found")
    
    consent = privacy_manager.consent_store[user_id]
    
    # Si options est None, retirer tout consentement
    if options is None:
        new_options = ConsentOptions()  # Tous les consentements à False
    else:
        new_options = consent.options.copy()
        for option in options:
            if hasattr(new_options, option):
                setattr(new_options, option, False)
    
    privacy_manager.record_consent(user_id, new_options)
    return {"status": "success", "options": new_options.dict()}