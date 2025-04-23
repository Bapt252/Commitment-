import pytest
from fastapi import UploadFile
from unittest.mock import MagicMock, patch

from app.services.cv_parser import CVParserService


@pytest.fixture
def mock_cv_content():
    return """Jean Dupont
jean.dupont@example.com
+33 6 12 34 56 78
Développeur Python Senior

Compétences:
Python, FastAPI, Docker, PostgreSQL
JavaScript, React, HTML, CSS
Git, CI/CD, AWS
"""


@pytest.fixture
def cv_parser_service():
    return CVParserService()


@patch('app.services.cv_parser.PyPDF2.PdfReader')
async def test_parse_pdf(mock_pdf_reader, cv_parser_service, mock_cv_content):
    # Configuration du mock
    mock_page = MagicMock()
    mock_page.extract_text.return_value = mock_cv_content
    
    mock_pdf_instance = MagicMock()
    mock_pdf_instance.pages = [mock_page]
    mock_pdf_reader.return_value = mock_pdf_instance
    
    # Création du fichier mock
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.read = MagicMock(return_value=b"mock pdf content")
    
    # Test
    result = await cv_parser_service.parse_cv(mock_file)
    
    # Assertions
    assert result.name == "Jean Dupont"
    assert result.email == "jean.dupont@example.com"
    assert "python" in [s.lower() for s in result.softwares]


@patch('app.services.cv_parser.docx.Document')
async def test_parse_docx(mock_docx, cv_parser_service, mock_cv_content):
    # Configuration du mock
    mock_paragraph = MagicMock()
    mock_paragraph.text = mock_cv_content
    
    mock_docx_instance = MagicMock()
    mock_docx_instance.paragraphs = [mock_paragraph]
    mock_docx.return_value = mock_docx_instance
    
    # Création du fichier mock
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.docx"
    mock_file.read = MagicMock(return_value=b"mock docx content")
    
    # Test
    result = await cv_parser_service.parse_cv(mock_file)
    
    # Assertions
    assert result.name == "Jean Dupont"
    assert result.email == "jean.dupont@example.com"
    assert "python" in [s.lower() for s in result.softwares]


@patch('app.services.cv_parser.tempfile.NamedTemporaryFile')
@patch('app.services.cv_parser.os.unlink')
async def test_invalid_file_format(mock_unlink, mock_temp_file, cv_parser_service):
    # Création du fichier mock avec une extension non supportée
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.txt"
    mock_file.read = MagicMock(return_value=b"mock text content")
    
    # Configuration du mock pour le fichier temporaire
    mock_temp_file_instance = MagicMock()
    mock_temp_file_instance.name = "/tmp/mockfile"
    mock_temp_file.return_value.__enter__.return_value = mock_temp_file_instance
    
    # Test
    with pytest.raises(ValueError) as excinfo:
        await cv_parser_service.parse_cv(mock_file)
    
    # Assertions
    assert "Unsupported file format" in str(excinfo.value)
