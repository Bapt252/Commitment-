from typing import List, Optional

class CVModel:
    """
    Modèle de données pour les informations extraites d'un CV
    """
    def __init__(
        self,
        nom: str = "",
        prenom: str = "",
        poste: str = "",
        competences: List[str] = None,
        logiciels: List[str] = None,
        soft_skills: List[str] = None,
        email: str = "",
        telephone: str = "",
        adresse: str = ""
    ):
        self.nom = nom
        self.prenom = prenom
        self.poste = poste
        self.competences = competences or []
        self.logiciels = logiciels or []
        self.soft_skills = soft_skills or []
        self.email = email
        self.telephone = telephone
        self.adresse = adresse

    def to_dict(self) -> dict:
        """
        Convertit l'instance en dictionnaire pour la sérialisation JSON
        """
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "poste": self.poste,
            "competences": self.competences,
            "logiciels": self.logiciels,
            "soft_skills": self.soft_skills,
            "email": self.email,
            "telephone": self.telephone,
            "adresse": self.adresse
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CVModel':
        """
        Crée une instance de CVModel à partir d'un dictionnaire
        """
        return cls(
            nom=data.get("nom", ""),
            prenom=data.get("prenom", ""),
            poste=data.get("poste", ""),
            competences=data.get("competences", []),
            logiciels=data.get("logiciels", []),
            soft_skills=data.get("soft_skills", []),
            email=data.get("email", ""),
            telephone=data.get("telephone", ""),
            adresse=data.get("adresse", "")
        )
