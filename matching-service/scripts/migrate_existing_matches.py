"""Script pour ajouter la version de l'algorithme aux matchings existants."""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

def migrate_existing_matches():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Ajouter la colonne algorithm_version si elle n'existe pas
        session.execute(text("""
            ALTER TABLE match_results 
            ADD COLUMN IF NOT EXISTS algorithm_version VARCHAR(50) 
            DEFAULT 'v1.0.0-legacy'
        """))
        
        # Mettre à jour les matchings existants
        session.execute(text("""
            UPDATE match_results 
            SET algorithm_version = 'v1.0.0-legacy'
            WHERE algorithm_version IS NULL
        """))
        
        session.commit()
        print("Migration completed successfully")
    except Exception as e:
        session.rollback()
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    migrate_existing_matches()