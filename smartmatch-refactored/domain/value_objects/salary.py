"""
Salary Value Object

Représente les informations salariales.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class SalaryCurrency(Enum):
    """
    Devises supportées pour les salaires.
    """
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
    CAD = "CAD"


class SalaryPeriod(Enum):
    """
    Périodes pour les salaires.
    """
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass(frozen=True)
class SalaryRange:
    """
    Représente une fourchette salariale.
    """
    
    min_amount: int
    max_amount: Optional[int] = None
    currency: SalaryCurrency = SalaryCurrency.EUR
    period: SalaryPeriod = SalaryPeriod.YEARLY
    
    def __post_init__(self):
        if self.min_amount < 0:
            raise ValueError("Minimum salary cannot be negative")
        
        if self.max_amount is not None and self.max_amount < self.min_amount:
            raise ValueError("Maximum salary cannot be less than minimum salary")
    
    @classmethod
    def exact(cls, amount: int, currency: SalaryCurrency = SalaryCurrency.EUR, 
              period: SalaryPeriod = SalaryPeriod.YEARLY) -> 'SalaryRange':
        """
        Crée une fourchette pour un salaire exact.
        
        Args:
            amount: Montant exact
            currency: Devise
            period: Période
            
        Returns:
            Fourchette salariale pour ce montant exact
        """
        return cls(min_amount=amount, max_amount=amount, currency=currency, period=period)
    
    @classmethod
    def minimum_only(cls, amount: int, currency: SalaryCurrency = SalaryCurrency.EUR,
                    period: SalaryPeriod = SalaryPeriod.YEARLY) -> 'SalaryRange':
        """
        Crée une fourchette avec un minimum seulement.
        
        Args:
            amount: Montant minimum
            currency: Devise
            period: Période
            
        Returns:
            Fourchette salariale avec minimum seulement
        """
        return cls(min_amount=amount, max_amount=None, currency=currency, period=period)
    
    @classmethod
    def between(cls, min_amount: int, max_amount: int, 
               currency: SalaryCurrency = SalaryCurrency.EUR,
               period: SalaryPeriod = SalaryPeriod.YEARLY) -> 'SalaryRange':
        """
        Crée une fourchette entre deux montants.
        
        Args:
            min_amount: Montant minimum
            max_amount: Montant maximum
            currency: Devise
            period: Période
            
        Returns:
            Fourchette salariale entre les deux montants
        """
        return cls(min_amount=min_amount, max_amount=max_amount, 
                  currency=currency, period=period)
    
    def contains(self, amount: int) -> bool:
        """
        Vérifie si un montant se trouve dans cette fourchette.
        
        Args:
            amount: Montant à vérifier
            
        Returns:
            True si le montant est dans la fourchette
        """
        if amount < self.min_amount:
            return False
        
        if self.max_amount is not None and amount > self.max_amount:
            return False
        
        return True
    
    def get_midpoint(self) -> Optional[int]:
        """
        Retourne le point moyen de la fourchette.
        
        Returns:
            Point moyen ou None si pas de maximum défini
        """
        if self.max_amount is not None:
            return (self.min_amount + self.max_amount) // 2
        return None
    
    def overlaps_with(self, other: 'SalaryRange') -> bool:
        """
        Vérifie si cette fourchette chevauche avec une autre.
        
        Args:
            other: Autre fourchette salariale
            
        Returns:
            True si les fourchettes se chevauchent
            
        Note:
            Pour comparer, les salaires doivent être dans la même devise et période
        """
        if self.currency != other.currency or self.period != other.period:
            return False
        
        # Si l'une des fourchettes n'a pas de maximum
        if self.max_amount is None or other.max_amount is None:
            return self.min_amount <= (other.max_amount or float('inf')) and \
                   other.min_amount <= (self.max_amount or float('inf'))
        
        # Fourchettes avec bornes définies
        return self.min_amount <= other.max_amount and other.min_amount <= self.max_amount
    
    def compatibility_score(self, expected_salary: int) -> float:
        """
        Calcule un score de compatibilité avec un salaire attendu.
        
        Args:
            expected_salary: Salaire attendu
            
        Returns:
            Score entre 0 et 1 (1 = parfaite compatibilité)
        """
        if self.contains(expected_salary):
            return 1.0
        
        if expected_salary < self.min_amount:
            # Le candidat demande moins que le minimum offert
            if self.min_amount > 0:
                ratio = expected_salary / self.min_amount
                return min(1.0, 0.7 + ratio * 0.3)
            else:
                return 0.5
        else:
            # Le candidat demande plus que le maximum offert
            if self.max_amount is not None:
                if expected_salary > self.max_amount * 1.5:
                    return 0.1  # Beaucoup trop élevé
                else:
                    ratio = self.max_amount / expected_salary
                    return max(0.1, ratio * 0.9)
            else:
                # Pas de maximum défini, score neutre
                return 0.5
    
    def to_yearly(self) -> 'SalaryRange':
        """
        Convertit cette fourchette en salaire annuel.
        
        Returns:
            Nouvelle fourchette en salaire annuel
            
        Note:
            Utilise des approximations standard pour la conversion
        """
        if self.period == SalaryPeriod.YEARLY:
            return self
        
        conversion_factors = {
            SalaryPeriod.HOURLY: 2080,  # 40h/semaine * 52 semaines
            SalaryPeriod.DAILY: 260,    # 5 jours/semaine * 52 semaines  
            SalaryPeriod.MONTHLY: 12    # 12 mois/an
        }
        
        factor = conversion_factors.get(self.period, 1)
        
        min_yearly = self.min_amount * factor
        max_yearly = self.max_amount * factor if self.max_amount is not None else None
        
        return SalaryRange(
            min_amount=min_yearly,
            max_amount=max_yearly,
            currency=self.currency,
            period=SalaryPeriod.YEARLY
        )
    
    def format(self) -> str:
        """
        Formate la fourchette salariale pour l'affichage.
        
        Returns:
            Chaîne formatée
        """
        currency_symbol = {
            SalaryCurrency.EUR: "€",
            SalaryCurrency.USD: "$",
            SalaryCurrency.GBP: "£",
            SalaryCurrency.CHF: "CHF",
            SalaryCurrency.CAD: "CAD$"
        }.get(self.currency, self.currency.value)
        
        period_suffix = {
            SalaryPeriod.HOURLY: "/h",
            SalaryPeriod.DAILY: "/day",
            SalaryPeriod.MONTHLY: "/month",
            SalaryPeriod.YEARLY: "/year"
        }.get(self.period, "")
        
        if self.max_amount is not None:
            if self.min_amount == self.max_amount:
                return f"{currency_symbol}{self.min_amount:,}{period_suffix}"
            else:
                return f"{currency_symbol}{self.min_amount:,} - {currency_symbol}{self.max_amount:,}{period_suffix}"
        else:
            return f"{currency_symbol}{self.min_amount:,}+{period_suffix}"
    
    def __str__(self) -> str:
        return self.format()
    
    def __repr__(self) -> str:
        return f"SalaryRange({self.min_amount}, {self.max_amount}, {self.currency}, {self.period})"
