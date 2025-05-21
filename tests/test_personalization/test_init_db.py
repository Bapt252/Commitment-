"""
Tests unitaires pour le script d'initialisation de la base de données.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importer le script comme un module
import scripts.init_personalization_db as init_db

class TestInitPersonalizationDB(unittest.TestCase):
    
    def setUp(self):
        # Créer un mock pour la connexion à la base de données
        self.connection_mock = MagicMock()
        self.cursor_mock = MagicMock()
        self.connection_mock.cursor.return_value = self.cursor_mock
        
        # Créer un mock pour parse_args
        self.args_mock = MagicMock()
        self.args_mock.db_host = 'localhost'
        self.args_mock.db_port = 5432
        self.args_mock.db_name = 'commitment'
        self.args_mock.db_user = 'postgres'
        self.args_mock.db_password = 'postgres'
        self.args_mock.schema_file = 'test_schema.sql'
        self.args_mock.seed_data = True
    
    @patch('scripts.init_personalization_db.parse_args')
    @patch('scripts.init_personalization_db.connect_to_db')
    @patch('scripts.init_personalization_db.execute_schema_file')
    @patch('scripts.init_personalization_db.seed_default_data')
    def test_main(self, seed_mock, execute_mock, connect_mock, parse_mock):
        # Configurer les mocks
        parse_mock.return_value = self.args_mock
        connect_mock.return_value = self.connection_mock
        
        # Exécuter la fonction main
        init_db.main()
        
        # Vérifier que les fonctions ont été appelées correctement
        parse_mock.assert_called_once()
        connect_mock.assert_called_once_with(self.args_mock)
        execute_mock.assert_called_once_with(self.connection_mock, self.args_mock.schema_file)
        seed_mock.assert_called_once_with(self.connection_mock)

if __name__ == '__main__':
    unittest.main()
