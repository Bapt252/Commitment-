from backend.app.utils.document_converter import DocumentConverter
from backend.app.nlp.document_parser import process_document
import json

# 🔁 Remplace ici par le nom exact de ton fichier glissé dans le dossier
file_path = "backend/documents_a_analyser/cv_john_doe.pdf"

# Lire le contenu du fichier
with open(file_path, "rb") as f:
    content = f.read()

# Détection du format
format_type, mime_type = DocumentConverter.detect_format(content, file_path)
print(f"📄 Format détecté : {format_type} ({mime_type})")

# 🔄 Convertir le contenu en texte
from backend.app.utils.file_extractor import extract_text_from_bytes
text = extract_text_from_bytes(content, format_type)

# 🧠 Lancer l'analyse du texte
structured_data = process_document(text, document_type="cv")

# 🖨️ Afficher le résultat formaté
print(json.dumps(structured_data, indent=2, ensure_ascii=False))