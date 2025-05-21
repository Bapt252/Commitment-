#!/usr/bin/env python
"""
Script d'initialisation de la base de données pour la personnalisation.
Crée les tables et initialise les données de base.
"""

import os
import sys
import logging
import argparse
import psycopg2
from psycopg2.extras import RealDictCursor

# Ajouter le répertoire parent au chemin Python pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """
    Parse les arguments de la ligne de commande
    """
    parser = argparse.ArgumentParser(description='Initialize personalization database')
    parser.add_argument('--db-host', default=os.getenv('DB_HOST', 'localhost'),
                        help='Database host')
    parser.add_argument('--db-port', type=int, default=int(os.getenv('DB_PORT', 5432)),
                        help='Database port')
    parser.add_argument('--db-name', default=os.getenv('DB_NAME', 'commitment'),
                        help='Database name')
    parser.add_argument('--db-user', default=os.getenv('DB_USER', 'postgres'),
                        help='Database user')
    parser.add_argument('--db-password', default=os.getenv('DB_PASSWORD', 'postgres'),
                        help='Database password')
    parser.add_argument('--schema-file', default=os.path.abspath(
                            os.path.join(os.path.dirname(__file__), 
                                       '../database/16_personalization_schema.sql')),
                        help='Path to schema SQL file')
    parser.add_argument('--seed-data', action='store_true',
                        help='Seed the database with initial data')
    
    return parser.parse_args()

def connect_to_db(args):
    """
    Se connecte à la base de données
    """
    try:
        connection = psycopg2.connect(
            host=args.db_host,
            port=args.db_port,
            database=args.db_name,
            user=args.db_user,
            password=args.db_password,
            cursor_factory=RealDictCursor
        )
        connection.autocommit = True
        logger.info(f"Connected to database {args.db_name} on {args.db_host}")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

def execute_schema_file(connection, schema_file):
    """
    Exécute le fichier de schéma SQL
    """
    try:
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cursor = connection.cursor()
        cursor.execute(schema_sql)
        logger.info(f"Schema file {schema_file} executed successfully")
    except Exception as e:
        logger.error(f"Failed to execute schema file: {e}")
        sys.exit(1)

def seed_default_data(connection):
    """
    Remplit la base de données avec des données initiales
    """
    try:
        cursor = connection.cursor()
        
        # Seed des attributs de base pour la personnalisation
        cursor.execute("""
        INSERT INTO personalization_attributes 
            (attribute_name, default_weight, description) 
        VALUES 
            ('age', 0.3, 'Age difference weight'),
            ('location', 0.4, 'Geographic proximity weight'),
            ('interests', 0.5, 'Shared interests weight'),
            ('activity', 0.2, 'User activity level weight'),
            ('popularity', 0.1, 'Candidate popularity weight')
        ON CONFLICT (attribute_name) DO NOTHING;
        """)
        
        # Seed des catégories
        cursor.execute("""
        INSERT INTO personalization_categories
            (category_name, default_modifier, description)
        VALUES
            ('new_user', 1.2, 'New users get a boost'),
            ('inactive', 0.8, 'Inactive users get lower priority'),
            ('premium', 1.3, 'Premium users get a boost'),
            ('verified', 1.1, 'Verified profiles get a small boost')
        ON CONFLICT (category_name) DO NOTHING;
        """)
        
        # Seed des tests A/B
        cursor.execute("""
        INSERT INTO ab_tests
            (test_name, description, start_date, end_date, active)
        VALUES
            ('weight_balance', 'Testing different weight balances', CURRENT_DATE, 
             CURRENT_DATE + INTERVAL '30 days', TRUE),
            ('cold_start_strategy', 'Testing different cold start strategies', CURRENT_DATE,
             CURRENT_DATE + INTERVAL '30 days', TRUE)
        ON CONFLICT (test_name) DO NOTHING;
        """)
        
        # Seed des variantes de tests A/B
        cursor.execute("""
        INSERT INTO ab_test_variants
            (test_id, variant_name, description, distribution_weight)
        VALUES
            ((SELECT id FROM ab_tests WHERE test_name = 'weight_balance'), 
             'control', 'Standard weights', 0.33),
            ((SELECT id FROM ab_tests WHERE test_name = 'weight_balance'),
             'collaborative_heavy', 'Emphasize collaborative filtering', 0.33),
            ((SELECT id FROM ab_tests WHERE test_name = 'weight_balance'),
             'time_sensitive', 'Emphasize temporal factors', 0.34),
            ((SELECT id FROM ab_tests WHERE test_name = 'cold_start_strategy'),
             'control', 'Basic cold start', 0.5),
            ((SELECT id FROM ab_tests WHERE test_name = 'cold_start_strategy'),
             'demographic', 'Demographic-based cold start', 0.5)
        ON CONFLICT DO NOTHING;
        """)
        
        logger.info("Database seeded with default data")
    except Exception as e:
        logger.error(f"Failed to seed default data: {e}")
        sys.exit(1)

def main():
    args = parse_args()
    connection = connect_to_db(args)
    
    # Exécuter le fichier de schéma
    execute_schema_file(connection, args.schema_file)
    
    # Seed des données si demandé
    if args.seed_data:
        seed_default_data(connection)
    
    logger.info("Database initialization completed successfully")

if __name__ == "__main__":
    main()
