from abc import ABC, abstractmethod
from typing import Dict, List, Any

class MatchingAlgorithm(ABC):
    @abstractmethod
    async def find_matches(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        pass

class DefaultMatchingAlgorithm(MatchingAlgorithm):
    async def find_matches(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        # Implémentation de l'algorithme par défaut
        # À adapter selon votre logique actuelle
        pass

class MatchingAlgorithmFactory:
    def __init__(self):
        self._algorithms: Dict[str, MatchingAlgorithm] = {}
        self.register_algorithm('default', DefaultMatchingAlgorithm())
    
    def register_algorithm(self, name: str, algorithm: MatchingAlgorithm) -> None:
        """Enregistrer un nouvel algorithme"""
        self._algorithms[name] = algorithm
    
    def get_algorithm(self, name: str) -> MatchingAlgorithm:
        """Récupérer un algorithme par son nom"""
        if name not in self._algorithms:
            raise ValueError(f"Algorithm '{name}' not found")
        return self._algorithms[name]