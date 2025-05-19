"""
Location Value Object

Représente une localisation géographique.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import re


@dataclass(frozen=True)
class Location:
    """
    Représente une localisation géographique.
    
    Peut être représentée sous forme d'adresse lisible ou de coordonnées GPS.
    """
    
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    def __post_init__(self):
        # Validation : au moins une représentation doit être fournie
        if not self.address and (self.latitude is None or self.longitude is None):
            raise ValueError("Location must have either address or coordinates (lat, lon)")
    
    @classmethod
    def from_address(cls, address: str) -> 'Location':
        """
        Crée une localisation à partir d'une adresse.
        
        Args:
            address: Adresse sous forme de texte
            
        Returns:
            Nouvelle instance de Location
        """
        return cls(address=address.strip())
    
    @classmethod
    def from_coordinates(cls, latitude: float, longitude: float) -> 'Location':
        """
        Crée une localisation à partir de coordonnées GPS.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            
        Returns:
            Nouvelle instance de Location
        """
        return cls(latitude=latitude, longitude=longitude)
    
    @classmethod
    def from_coordinate_string(cls, coord_string: str) -> 'Location':
        """
        Crée une localisation à partir d'une chaîne "lat,lon".
        
        Args:
            coord_string: Chaîne au format "latitude,longitude"
            
        Returns:
            Nouvelle instance de Location
            
        Raises:
            ValueError: Si le format n'est pas valide
        """
        pattern = r'^(-?\d+\.\d+),(-?\d+\.\d+)$'
        match = re.match(pattern, coord_string.strip())
        
        if not match:
            raise ValueError(f"Invalid coordinate format: {coord_string}. Expected 'lat,lon'")
        
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        
        return cls(latitude=latitude, longitude=longitude)
    
    def has_coordinates(self) -> bool:
        """
        Vérifie si la localisation possède des coordonnées GPS.
        
        Returns:
            True si les coordonnées sont disponibles
        """
        return self.latitude is not None and self.longitude is not None
    
    def has_address(self) -> bool:
        """
        Vérifie si la localisation possède une adresse.
        
        Returns:
            True si l'adresse est disponible
        """
        return self.address is not None and self.address.strip() != ""
    
    def get_coordinates(self) -> Optional[Tuple[float, float]]:
        """
        Retourne les coordonnées sous forme de tuple.
        
        Returns:
            Tuple (latitude, longitude) ou None si non disponible
        """
        if self.has_coordinates():
            return (self.latitude, self.longitude)
        return None
    
    def to_coordinate_string(self) -> Optional[str]:
        """
        Convertit les coordonnées en chaîne "lat,lon".
        
        Returns:
            Chaîne de coordonnées ou None si non disponible
        """
        if self.has_coordinates():
            return f"{self.latitude},{self.longitude}"
        return None
    
    def get_display_name(self) -> str:
        """
        Retourne un nom lisible pour cette localisation.
        
        Returns:
            Chaîne représentant la localisation
        """
        if self.address:
            return self.address
        elif self.city:
            return f"{self.city}, {self.country}" if self.country else self.city
        elif self.has_coordinates():
            return f"({self.latitude}, {self.longitude})"
        else:
            return "Unknown location"
    
    @property
    def key(self) -> str:
        """
        Retourne une clé unique pour cette localisation (useful for caching).
        
        Returns:
            Clé unique sous forme de chaîne
        """
        if self.has_coordinates():
            return f"coord:{self.latitude},{self.longitude}"
        elif self.address:
            return f"addr:{self.address.lower().replace(' ', '_')}"
        else:
            return "unknown"
    
    def __str__(self) -> str:
        return f"Location({self.get_display_name()})"
    
    def __repr__(self) -> str:
        return self.__str__()
