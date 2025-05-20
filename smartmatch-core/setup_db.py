import sqlite3
import os

# Créer le répertoire data s'il n'existe pas
os.makedirs('data', exist_ok=True)

# Créer ou se connecter à la base de données SQLite
conn = sqlite3.connect('data/tracking.db')
cursor = conn.cursor()

# Créer la table des événements
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    match_id TEXT,
    data JSON,
    processed INTEGER DEFAULT 0
)
''')

# Créer la table des consentements
cursor.execute('''
CREATE TABLE IF NOT EXISTS consents (
    consent_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    analytics INTEGER DEFAULT 0,
    preferences INTEGER DEFAULT 0,
    improvement INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_hash TEXT,
    version TEXT DEFAULT '1.0'
)
''')

# Créer les index
cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_match_id ON events(match_id)')

# Valider les changements
conn.commit()
conn.close()

print("Base de données SQLite initialisée avec succès!")