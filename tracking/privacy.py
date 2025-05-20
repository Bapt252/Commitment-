import uuid
import hashlib
import logging
from typing import Dict, Set, Any, Optional, List
from datetime import datetime, timedelta
import json
import asyncpg
import os
import ipaddress
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PrivacyManager:
    """
    Gestionnaire de confidentialité pour le système de tracking
    
    Gère les consentements utilisateur, l'anonymisation des données
    et la conformité GDPR de manière générale.
    """
    
    def __init__(self, db_dsn: Optional[str] = None, schema: str = "tracking"):
        """
        Initialise le gestionnaire de confidentialité
        
        Args:
            db_dsn: Chaîne de connexion à la base de données
            schema: Schéma contenant les tables de tracking
        """
        self.db_dsn = db_dsn or os.environ.get(
            "POSTGRES_DSN", 
            f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
            f"{os.environ.get('POSTGRES_PASSWORD', '')}@"
            f"{os.environ.get('POSTGRES_HOST', 'localhost')}:"
            f"{os.environ.get('POSTGRES_PORT', '5432')}/"
            f"{os.environ.get('POSTGRES_DB', 'commitment')}"
        )
        self.schema = schema
        self.pool = None
        self.consent_cache = {}  # Cache simple {user_id: {consent_type: expiration}}
        self.consent_version = os.environ.get("CONSENT_VERSION", "1.0")
        
    async def initialize(self):
        """Initialise la connexion à la base de données"""
        if self.pool is not None:
            return
            
        try:
            self.pool = await asyncpg.create_pool(dsn=self.db_dsn)
            logger.info("PrivacyManager database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PrivacyManager database connection: {str(e)}")
            # Si la connexion BD échoue, on peut fonctionner en mode dégradé
            # en supposant que tous les consentements sont valides
            
    async def close(self):
        """Ferme la connexion à la base de données"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PrivacyManager database connection closed")
    
    @asynccontextmanager
    async def connection(self):
        """Contexte asynchrone pour obtenir une connexion du pool"""
        if not self.pool:
            await self.initialize()
            
        if self.pool:
            async with self.pool.acquire() as conn:
                yield conn
        else:
            # Si pas de pool disponible, on utilise un mode dégradé
            yield None
    
    def anonymize_user_id(self, user_id: str) -> str:
        """
        Anonymise un identifiant utilisateur en utilisant un hachage
        
        Args:
            user_id: Identifiant utilisateur original
            
        Returns:
            Identifiant anonymisé
        """
        # Pour les IDs déjà anonymisés, on les retourne tels quels
        if user_id.startswith("anon_"):
            return user_id
            
        # On utilise SHA-256 pour l'anonymisation avec un sel statique
        # Dans une implémentation réelle, on utiliserait un sel secret configuré
        hasher = hashlib.sha256()
        hasher.update(f"{user_id}:PRIVACY_SALT".encode('utf-8'))
        return f"anon_{hasher.hexdigest()}"
    
    def anonymize_ip(self, ip_address: str) -> str:
        """
        Anonymise une adresse IP en masquant les derniers octets
        
        Args:
            ip_address: Adresse IP à anonymiser
            
        Returns:
            Adresse IP anonymisée
        """
        if not ip_address:
            return None
            
        try:
            ip = ipaddress.ip_address(ip_address)
            if ip.version == 4:
                # Pour IPv4, on masque le dernier octet (x.x.x.0)
                ip_bytes = ip.packed
                anonymized_bytes = ip_bytes[:3] + b'\x00'
                return str(ipaddress.ip_address(anonymized_bytes))
            else:
                # Pour IPv6, on masque les 80 derniers bits
                ip_bytes = ip.packed
                anonymized_bytes = ip_bytes[:6] + b'\x00' * 10
                return str(ipaddress.ip_address(anonymized_bytes))
        except ValueError:
            # En cas d'IP invalide, on retourne None
            logger.warning(f"Invalid IP address: {ip_address}")
            return None
    
    def sanitize_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nettoie un événement de toute donnée personnelle sensible
        
        Args:
            event: Dictionnaire contenant les données de l'événement
            
        Returns:
            Événement nettoyé
        """
        if not event:
            return {}
            
        sanitized = event.copy()
        
        # Anonymiser l'ID utilisateur si demandé (mode privacy renforcé)
        if os.environ.get("PRIVACY_MODE", "standard") == "enhanced":
            sanitized["user_id"] = self.anonymize_user_id(event["user_id"])
            
        # Anonymiser l'adresse IP
        if "ip_address" in sanitized and sanitized["ip_address"]:
            sanitized["ip_address"] = self.anonymize_ip(sanitized["ip_address"])
            
        # Nettoyer le User-Agent
        if "user_agent" in sanitized and sanitized["user_agent"]:
            # Garder uniquement les informations de base du User-Agent
            # Dans une implémentation réelle, on utiliserait une bibliothèque
            # de parsing pour extraire uniquement les informations pertinentes
            pass
            
        # Nettoyer les métadonnées si présentes
        if "metadata" in sanitized and sanitized["metadata"]:
            metadata = sanitized["metadata"]
            
            # Supprimer toute donnée potentiellement sensible
            fields_to_remove = [
                "email", "phone", "address", "full_name", "password",
                "credit_card", "social_security", "personal_data"
            ]
            for field in fields_to_remove:
                if isinstance(metadata, dict) and field in metadata:
                    del metadata[field]
                    
            sanitized["metadata"] = metadata
            
        return sanitized
    
    async def get_user_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Vérifie si l'utilisateur a donné son consentement pour un type spécifique
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_type: Type de consentement (analytics, marketing, etc.)
            
        Returns:
            True si le consentement est valide, False sinon
        """
        # Vérifier d'abord dans le cache
        if user_id in self.consent_cache and consent_type in self.consent_cache[user_id]:
            expiration = self.consent_cache[user_id][consent_type]
            if expiration > datetime.now():
                return True
                
        # Pas dans le cache ou expiré, vérifier en base de données
        try:
            async with self.connection() as conn:
                if conn is None:  # Mode dégradé
                    logger.warning("Database unavailable, assuming consent is granted")
                    return True
                    
                row = await conn.fetchrow(
                    f"""
                    SELECT is_granted, expires_at
                    FROM {self.schema}.user_consents
                    WHERE user_id = $1 AND consent_type = $2
                    """,
                    user_id, consent_type
                )
                
                if row and row["is_granted"]:
                    # Vérifier si le consentement n'est pas expiré
                    if row["expires_at"] is None or row["expires_at"] > datetime.now():
                        # Mettre à jour le cache
                        if user_id not in self.consent_cache:
                            self.consent_cache[user_id] = {}
                        self.consent_cache[user_id][consent_type] = row["expires_at"] or (datetime.now() + timedelta(days=365))
                        return True
                        
            return False
        except Exception as e:
            logger.error(f"Error checking user consent: {str(e)}")
            # En cas d'erreur, par défaut on suppose que le consentement n'est pas donné
            return False
    
    async def set_user_consent(self, user_id: str, consent_type: str, 
                              is_granted: bool, ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> bool:
        """
        Enregistre le consentement d'un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_type: Type de consentement (analytics, marketing, etc.)
            is_granted: Si le consentement est accordé ou révoqué
            ip_address: Adresse IP utilisée lors de l'octroi du consentement
            user_agent: User-Agent du navigateur utilisé
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        try:
            # Définir la durée de validité du consentement (par défaut 1 an)
            expires_at = datetime.now() + timedelta(days=365) if is_granted else None
            
            async with self.connection() as conn:
                if conn is None:  # Mode dégradé
                    logger.warning("Database unavailable, consent not saved")
                    # Mise à jour du cache malgré tout
                    if user_id not in self.consent_cache:
                        self.consent_cache[user_id] = {}
                    self.consent_cache[user_id][consent_type] = expires_at
                    return True
                    
                # Anonymiser l'IP pour le stockage
                if ip_address:
                    ip_address = self.anonymize_ip(ip_address)
                    
                await conn.execute(
                    f"""
                    INSERT INTO {self.schema}.user_consents (
                        user_id, consent_type, is_granted, granted_at, expires_at,
                        consent_version, ip_address, user_agent
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (user_id, consent_type) DO UPDATE
                    SET is_granted = $3, granted_at = $4, expires_at = $5,
                        consent_version = $6, ip_address = $7, user_agent = $8,
                        updated_at = NOW()
                    """,
                    user_id, consent_type, is_granted, 
                    datetime.now() if is_granted else None,
                    expires_at, self.consent_version, ip_address, user_agent
                )
                
                # Mise à jour du cache
                if user_id not in self.consent_cache:
                    self.consent_cache[user_id] = {}
                    
                if is_granted:
                    self.consent_cache[user_id][consent_type] = expires_at
                elif consent_type in self.consent_cache[user_id]:
                    del self.consent_cache[user_id][consent_type]
                    
                return True
        except Exception as e:
            logger.error(f"Error setting user consent: {str(e)}")
            return False
    
    def has_valid_consent(self, user_id: str, consent_types: Set[str]) -> bool:
        """
        Vérifie si l'utilisateur a donné son consentement pour tous les types spécifiés
        
        Cette version synchrone est utilisée pour les vérifications rapides dans le flux
        de collecte d'événements. Elle utilise uniquement le cache et retourne False
        si le consentement n'est pas dans le cache, ce qui déclenchera une vérification 
        asynchrone ultérieure.
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_types: Ensemble des types de consentement requis
            
        Returns:
            True si tous les consentements sont valides, False sinon
        """
        # Mode développement: consentement toujours accordé
        if os.environ.get("ENVIRONMENT", "development") == "development":
            logger.debug(f"Development mode: assuming consent for user {user_id}")
            return True
            
        # Vérification basée uniquement sur le cache
        if user_id in self.consent_cache:
            now = datetime.now()
            return all(
                consent_type in self.consent_cache[user_id] and 
                self.consent_cache[user_id][consent_type] > now
                for consent_type in consent_types
            )
        
        return False
    
    async def check_and_update_consents(self, user_id: str, consent_types: Set[str]) -> bool:
        """
        Vérifie de manière asynchrone les consentements et met à jour le cache
        
        Args:
            user_id: Identifiant de l'utilisateur
            consent_types: Ensemble des types de consentement requis
            
        Returns:
            True si tous les consentements sont valides, False sinon
        """
        all_valid = True
        
        for consent_type in consent_types:
            is_valid = await self.get_user_consent(user_id, consent_type)
            all_valid = all_valid and is_valid
            
        return all_valid
    
    async def delete_user_data(self, user_id: str) -> bool:
        """
        Supprime toutes les données d'un utilisateur (droit à l'oubli GDPR)
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        try:
            async with self.connection() as conn:
                if conn is None:  # Mode dégradé
                    logger.error("Database unavailable, cannot delete user data")
                    return False
                    
                # Utiliser la fonction SQL de suppression
                result = await conn.fetchval(
                    f"SELECT {self.schema}.delete_user_data($1)",
                    user_id
                )
                
                # Supprimer du cache
                if user_id in self.consent_cache:
                    del self.consent_cache[user_id]
                    
                logger.info(f"Deleted {result} records for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False
    
    async def anonymize_user_data(self, user_id: str) -> bool:
        """
        Anonymise toutes les données d'un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        try:
            async with self.connection() as conn:
                if conn is None:  # Mode dégradé
                    logger.error("Database unavailable, cannot anonymize user data")
                    return False
                    
                # Utiliser la fonction SQL d'anonymisation
                result = await conn.fetchval(
                    f"SELECT {self.schema}.anonymize_user_data($1)",
                    user_id
                )
                
                # Supprimer du cache
                if user_id in self.consent_cache:
                    del self.consent_cache[user_id]
                    
                logger.info(f"Anonymized {result} records for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"Error anonymizing user data: {str(e)}")
            return False
