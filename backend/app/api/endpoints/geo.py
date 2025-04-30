from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, List

from app.services.geo_service import geo_service

router = APIRouter()

class GeocodingRequest(BaseModel):
    """Requête pour le géocodage d'une adresse"""
    address: str = Field(..., description="Adresse à géocoder")

class ReverseGeocodingRequest(BaseModel):
    """Requête pour le géocodage inversé de coordonnées"""
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lng: float = Field(..., description="Longitude", ge=-180, le=180)
    
    @validator('lat')
    def validate_latitude(cls, v):
        if v < -90 or v > 90:
            raise ValueError("La latitude doit être comprise entre -90 et 90")
        return v
        
    @validator('lng')
    def validate_longitude(cls, v):
        if v < -180 or v > 180:
            raise ValueError("La longitude doit être comprise entre -180 et 180")
        return v

class PlacesNearbyRequest(BaseModel):
    """Requête pour rechercher des lieux à proximité"""
    lat: float = Field(..., description="Latitude du centre de recherche", ge=-90, le=90)
    lng: float = Field(..., description="Longitude du centre de recherche", ge=-180, le=180)
    radius: int = Field(5000, description="Rayon de recherche en mètres (max 50000)", ge=1, le=50000)
    keyword: Optional[str] = Field(None, description="Mot-clé de recherche")
    place_type: Optional[str] = Field(None, description="Type de lieu (ex: restaurant, school, etc.)")

class DistanceRequest(BaseModel):
    """Requête pour calculer la distance entre deux points"""
    origin: str = Field(..., description="Adresse ou coordonnées d'origine")
    destination: str = Field(..., description="Adresse ou coordonnées de destination")
    mode: str = Field("driving", description="Mode de transport")
    
    @validator('mode')
    def validate_mode(cls, v):
        allowed_modes = ["driving", "walking", "bicycling", "transit"]
        if v not in allowed_modes:
            raise ValueError(f"Le mode doit être l'un de : {', '.join(allowed_modes)}")
        return v

@router.post("/geocode", summary="Géocoder une adresse")
async def geocode_address(request: GeocodingRequest):
    """
    Convertit une adresse en coordonnées géographiques.
    
    - **address**: Adresse à géocoder (ex: "15 rue de Rivoli, Paris, France")
    
    Retourne les coordonnées (lat, lng) et l'adresse formatée.
    """
    result = geo_service.geocode_address(request.address)
    if not result:
        raise HTTPException(status_code=404, detail="Adresse non trouvée ou erreur de géocodage")
    return result

@router.post("/reverse-geocode", summary="Géocodage inversé")
async def reverse_geocode(request: ReverseGeocodingRequest):
    """
    Convertit des coordonnées en adresse.
    
    - **lat**: Latitude (-90 à 90)
    - **lng**: Longitude (-180 à 180)
    
    Retourne l'adresse formatée et des informations sur le lieu.
    """
    result = geo_service.reverse_geocode(request.lat, request.lng)
    if not result:
        raise HTTPException(status_code=404, detail="Lieu non trouvé ou erreur de géocodage inversé")
    return result

@router.post("/places-nearby", summary="Rechercher des lieux à proximité")
async def places_nearby(request: PlacesNearbyRequest):
    """
    Recherche des lieux à proximité d'un point.
    
    - **lat**: Latitude du centre de recherche
    - **lng**: Longitude du centre de recherche
    - **radius**: Rayon de recherche en mètres (max 50000)
    - **keyword**: Mot-clé de recherche (optionnel)
    - **place_type**: Type de lieu (optionnel: restaurant, school, etc.)
    
    Retourne une liste de lieux avec leurs informations.
    """
    results = geo_service.get_places_nearby(
        request.lat, 
        request.lng, 
        request.radius, 
        request.keyword, 
        request.place_type
    )
    return {"results": results}

@router.post("/distance", summary="Calculer la distance entre deux points")
async def calculate_distance(request: DistanceRequest):
    """
    Calcule la distance et le temps de trajet entre deux points.
    
    - **origin**: Adresse ou coordonnées d'origine
    - **destination**: Adresse ou coordonnées de destination
    - **mode**: Mode de transport (driving, walking, bicycling, transit)
    
    Retourne la distance et le temps de trajet.
    """
    result = geo_service.calculate_distance(
        request.origin,
        request.destination,
        request.mode
    )
    if not result:
        raise HTTPException(status_code=404, detail="Impossible de calculer la distance ou le temps de trajet")
    return result
