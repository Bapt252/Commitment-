"""
Utilitaires de base de données pour l'API Gateway
Gestion des utilisateurs et authentification
"""

import asyncio
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import asyncpg
import bcrypt
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Pool de connexions global
connection_pool = None

async def init_db_pool():
    """Initialiser le pool de connexions à la base de données"""
    global connection_pool
    
    try:
        connection_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        logger.info("Pool de connexions DB initialisé")
        
        # Créer les tables si elles n'existent pas
        await create_tables()
        
    except Exception as e:
        logger.error(f"Erreur initialisation DB pool: {e}")
        raise

async def close_db_pool():
    """Fermer le pool de connexions"""
    global connection_pool
    if connection_pool:
        await connection_pool.close()
        logger.info("Pool de connexions DB fermé")

async def create_tables():
    """Créer les tables nécessaires pour l'authentification"""
    
    if not connection_pool:
        await init_db_pool()
    
    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'candidat',
        is_active BOOLEAN DEFAULT true,
        is_verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        profile_data JSONB DEFAULT '{}',
        settings JSONB DEFAULT '{}'
    );
    """
    
    create_user_sessions_table_sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        refresh_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address INET,
        user_agent TEXT,
        is_active BOOLEAN DEFAULT true
    );
    """
    
    create_api_keys_table_sql = """
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        key_name VARCHAR(255) NOT NULL,
        api_key VARCHAR(255) UNIQUE NOT NULL,
        permissions JSONB DEFAULT '[]',
        is_active BOOLEAN DEFAULT true,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used TIMESTAMP
    );
    """
    
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key);",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);"
    ]
    
    try:
        async with connection_pool.acquire() as conn:
            await conn.execute(create_users_table_sql)
            await conn.execute(create_user_sessions_table_sql)
            await conn.execute(create_api_keys_table_sql)
            
            for index_sql in create_indexes_sql:
                await conn.execute(index_sql)
                
            logger.info("Tables de base de données créées/vérifiées")
            
    except Exception as e:
        logger.error(f"Erreur création tables: {e}")
        raise

# Fonctions utilitaires de hachage
def hash_password(password: str) -> str:
    """Hacher un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Vérifier un mot de passe contre son hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erreur vérification mot de passe: {e}")
        return False

def generate_api_key() -> str:
    """Générer une clé API sécurisée"""
    return f"ssm_{secrets.token_urlsafe(32)}"

# Fonctions de gestion des utilisateurs
async def create_user(email: str, password: str, full_name: str, role: str = "candidat") -> Dict[str, Any]:
    """Créer un nouvel utilisateur"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        password_hash = hash_password(password)
        
        async with connection_pool.acquire() as conn:
            user_id = await conn.fetchval(
                """
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                email, password_hash, full_name, role
            )
            
            # Récupérer l'utilisateur créé
            user = await conn.fetchrow(
                """
                SELECT id, email, full_name, role, is_active, is_verified, created_at
                FROM users WHERE id = $1
                """,
                user_id
            )
            
            logger.info(f"Utilisateur créé: {email} ({role})")
            return dict(user)
            
    except asyncpg.UniqueViolationError:
        raise ValueError("Email déjà utilisé")
    except Exception as e:
        logger.error(f"Erreur création utilisateur: {e}")
        raise

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Récupérer un utilisateur par email"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT id, email, password_hash, full_name, role, is_active, 
                       is_verified, created_at, updated_at, last_login, 
                       profile_data, settings
                FROM users WHERE email = $1
                """,
                email
            )
            
            return dict(user) if user else None
            
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Récupérer un utilisateur par ID"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT id, email, password_hash, full_name, role, is_active, 
                       is_verified, created_at, updated_at, last_login, 
                       profile_data, settings
                FROM users WHERE id = $1
                """,
                user_id
            )
            
            return dict(user) if user else None
            
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur par ID: {e}")
        return None

async def update_user_last_login(user_id: int, ip_address: str = None):
    """Mettre à jour la dernière connexion d'un utilisateur"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                """,
                user_id
            )
            
    except Exception as e:
        logger.error(f"Erreur MAJ dernière connexion: {e}")

async def update_user_profile(user_id: int, profile_data: Dict[str, Any]):
    """Mettre à jour le profil d'un utilisateur"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users 
                SET profile_data = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
                """,
                profile_data, user_id
            )
            
            logger.info(f"Profil utilisateur {user_id} mis à jour")
            
    except Exception as e:
        logger.error(f"Erreur MAJ profil utilisateur: {e}")
        raise

async def deactivate_user(user_id: int):
    """Désactiver un utilisateur"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users 
                SET is_active = false, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                """,
                user_id
            )
            
            logger.info(f"Utilisateur {user_id} désactivé")
            
    except Exception as e:
        logger.error(f"Erreur désactivation utilisateur: {e}")
        raise

# Gestion des clés API
async def create_api_key(user_id: int, key_name: str, permissions: list = None) -> str:
    """Créer une nouvelle clé API pour un utilisateur"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        api_key = generate_api_key()
        permissions = permissions or []
        
        async with connection_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO api_keys (user_id, key_name, api_key, permissions)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, key_name, api_key, permissions
            )
            
            logger.info(f"Clé API créée pour utilisateur {user_id}: {key_name}")
            return api_key
            
    except Exception as e:
        logger.error(f"Erreur création clé API: {e}")
        raise

async def get_user_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Récupérer un utilisateur par sa clé API"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT u.id, u.email, u.full_name, u.role, u.is_active,
                       ak.permissions, ak.expires_at
                FROM users u
                JOIN api_keys ak ON u.id = ak.user_id
                WHERE ak.api_key = $1 AND ak.is_active = true AND u.is_active = true
                AND (ak.expires_at IS NULL OR ak.expires_at > CURRENT_TIMESTAMP)
                """,
                api_key
            )
            
            if result:
                # Mettre à jour la dernière utilisation
                await conn.execute(
                    "UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE api_key = $1",
                    api_key
                )
                
                return dict(result)
            
            return None
            
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur par API key: {e}")
        return None

# Fonctions de statistiques et monitoring
async def get_user_stats() -> Dict[str, Any]:
    """Obtenir des statistiques sur les utilisateurs"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            active_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active = true")
            verified_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_verified = true")
            
            users_by_role = await conn.fetch(
                "SELECT role, COUNT(*) as count FROM users GROUP BY role"
            )
            
            recent_registrations = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'"
            )
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "users_by_role": {row["role"]: row["count"] for row in users_by_role},
                "recent_registrations": recent_registrations
            }
            
    except Exception as e:
        logger.error(f"Erreur statistiques utilisateurs: {e}")
        return {}

# Fonction de nettoyage
async def cleanup_expired_sessions():
    """Nettoyer les sessions expirées"""
    
    if not connection_pool:
        await init_db_pool()
    
    try:
        async with connection_pool.acquire() as conn:
            deleted_count = await conn.fetchval(
                """
                DELETE FROM user_sessions 
                WHERE expires_at < CURRENT_TIMESTAMP
                RETURNING COUNT(*)
                """
            )
            
            if deleted_count > 0:
                logger.info(f"Sessions expirées nettoyées: {deleted_count}")
                
    except Exception as e:
        logger.error(f"Erreur nettoyage sessions: {e}")

# Initialisation au démarrage
async def initialize_database():
    """Initialiser la base de données au démarrage de l'application"""
    try:
        await init_db_pool()
        await create_tables()
        
        # Créer un utilisateur admin par défaut si aucun n'existe
        admin_exists = await get_user_by_email("admin@supersmartmatch.com")
        if not admin_exists:
            await create_user(
                email="admin@supersmartmatch.com",
                password="SuperSecureAdminPassword123!",
                full_name="Administrateur SuperSmartMatch",
                role="admin"
            )
            logger.info("Utilisateur admin par défaut créé")
        
        logger.info("Base de données initialisée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur initialisation base de données: {e}")
        raise
