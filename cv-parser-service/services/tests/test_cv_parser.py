import unittest
import os
import io
from unittest.mock import patch, MagicMock
import json
from services.cv_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_cv_with_openai,
    parse_cv,
    calculate_file_hash
)
from app.models.cv_model import CVModel

class TestCVParser(unittest.TestCase):
    
    def setUp(self):
        # Mock de la réponse OpenAI
        self.mock_openai_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "nom": "Dupont",
                            "prenom": "Jean",
                            "poste": "Développeur Full Stack",
                            "competences": ["Python", "JavaScript", "FastAPI"],
                            "logiciels": ["Docker", "Git", "VS Code"],
                            "soft_skills": ["Travail en équipe", "Communication"],
                            "email": "jean.dupont@example.com",
                            "telephone": "0123456789",
                            "adresse": "123 Rue de la Paix, 75000 Paris"
                        })
                    }
                }
            ]
        }
        
        # Sample PDF content
        self.sample_pdf_content = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 68 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Jean Dupont - Développeur Full Stack) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000198 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n316\n%%EOF"
        
    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        # Mock de PyPDF2.PdfReader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Jean Dupont - Développeur Full Stack\n"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Test avec un fichier PDF simulé
        file = io.BytesIO(self.sample_pdf_content)
        result = extract_text_from_pdf(file)
        
        # Vérifications
        self.assertIn("Jean Dupont", result)
        self.assertIn("Développeur Full Stack", result)
        
    @patch('docx.Document')
    def test_extract_text_from_docx(self, mock_document):
        # Mock de docx.Document
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Jean Dupont - Développeur Full Stack"
        mock_document.return_value.paragraphs = [mock_paragraph]
        mock_document.return_value.tables = []
        
        # Test avec un fichier DOCX simulé
        file = io.BytesIO(b"mock docx content")
        result = extract_text_from_docx(file)
        
        # Vérifications
        self.assertIn("Jean Dupont", result)
        self.assertIn("Développeur Full Stack", result)
        
    @patch('openai.ChatCompletion.create')
    def test_parse_cv_with_openai(self, mock_openai):
        # Mock de l'API OpenAI
        mock_openai.return_value = self.mock_openai_response
        
        # Test de la fonction
        result = parse_cv_with_openai("Jean Dupont - Développeur Full Stack")
        
        # Vérifications
        self.assertEqual(result["nom"], "Dupont")
        self.assertEqual(result["prenom"], "Jean")
        self.assertEqual(result["poste"], "Développeur Full Stack")
        self.assertIn("Python", result["competences"])
        self.assertEqual(result["adresse"], "123 Rue de la Paix, 75000 Paris")
        
    @patch('services.cv_parser.extract_text')
    @patch('services.cv_parser.parse_cv_with_openai')
    @patch('services.cv_parser.redis_client.get')
    @patch('services.cv_parser.redis_client.set')
    def test_parse_cv_no_cache(self, mock_redis_set, mock_redis_get, mock_parse_cv, mock_extract_text):
        # Configuration des mocks
        mock_redis_get.return_value = None  # Pas de cache
        mock_extract_text.return_value = "Jean Dupont - Développeur Full Stack"
        mock_parse_cv.return_value = {
            "nom": "Dupont",
            "prenom": "Jean",
            "poste": "Développeur Full Stack",
            "competences": ["Python", "JavaScript"],
            "logiciels": ["Docker", "Git"],
            "soft_skills": ["Travail en équipe"],
            "email": "jean.dupont@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue de la Paix, 75000 Paris"
        }
        
        # Test avec un fichier simulé
        file = io.BytesIO(b"mock content")
        result = parse_cv(file, "cv.pdf")
        
        # Vérifications
        self.assertEqual(result.nom, "Dupont")
        self.assertEqual(result.prenom, "Jean")
        self.assertEqual(result.adresse, "123 Rue de la Paix, 75000 Paris")
        mock_redis_set.assert_called_once()  # Vérifier que le résultat a été mis en cache
        
    @patch('services.cv_parser.redis_client.get')
    def test_parse_cv_with_cache(self, mock_redis_get):
        # Configuration du mock pour simuler un cache hit
        mock_redis_get.return_value = json.dumps({
            "nom": "Dupont",
            "prenom": "Jean",
            "poste": "Développeur Full Stack",
            "competences": ["Python", "JavaScript"],
            "logiciels": ["Docker", "Git"],
            "soft_skills": ["Travail en équipe"],
            "email": "jean.dupont@example.com",
            "telephone": "0123456789",
            "adresse": "123 Rue de la Paix, 75000 Paris"
        })
        
        # Test avec un fichier simulé
        file = io.BytesIO(b"mock content")
        result = parse_cv(file, "cv.pdf")
        
        # Vérifications
        self.assertEqual(result.nom, "Dupont")
        self.assertEqual(result.prenom, "Jean")
        self.assertEqual(result.adresse, "123 Rue de la Paix, 75000 Paris")
        # Pas besoin de vérifier mock_redis_set car le résultat provient du cache
        
    def test_calculate_file_hash(self):
        # Test du calcul de hash
        file = io.BytesIO(b"test content")
        hash1 = calculate_file_hash(file)
        
        # Réinitialiser le fichier et recalculer le hash
        file.seek(0)
        hash2 = calculate_file_hash(file)
        
        # Vérifier que les hash sont identiques
        self.assertEqual(hash1, hash2)
        
        # Vérifier que le hash change avec un contenu différent
        file2 = io.BytesIO(b"different content")
        hash3 = calculate_file_hash(file2)
        self.assertNotEqual(hash1, hash3)

if __name__ == '__main__':
    unittest.main()
