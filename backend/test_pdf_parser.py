"""
Script de test pour l'extraction de texte des fichiers PDF
Usage: python test_pdf_parser.py chemin/vers/fichier.pdf
"""
import PyPDF2
import io
import sys
import os

def extract_text_from_pdf(file_path):
    """Test de l'extraction de texte d'un PDF"""
    try:
        print(f"Ouverture du fichier: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"ERREUR: Le fichier {file_path} n'existe pas")
            return None
            
        file_size = os.path.getsize(file_path)
        print(f"Taille du fichier: {file_size} octets")
        
        with open(file_path, 'rb') as file:
            file_content = file.read()
            
        print(f"Analyse du PDF avec PyPDF2 {PyPDF2.__version__}")
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        print(f"Nombre de pages détectées: {len(pdf_reader.pages)}")
        
        content = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                content += page_text + "\n"
                print(f"Page {i+1}: {len(page_text)} caractères extraits")
            else:
                print(f"Page {i+1}: Aucun texte extractible")
        
        print("\n--- CONTENU EXTRAIT ---")
        preview = content[:500] + "..." if len(content) > 500 else content
        print(preview)
        print("--- FIN DU CONTENU ---")
        
        return content
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return None

# Test avec pdfminer.six (méthode alternative) si disponible
def extract_text_with_pdfminer(file_path):
    try:
        import importlib.util
        if importlib.util.find_spec("pdfminer"):
            from pdfminer.high_level import extract_text
            print("\n--- TEST AVEC PDFMINER.SIX ---")
            
            text = extract_text(file_path)
            print(f"Caractères extraits: {len(text)}")
            preview = text[:500] + "..." if len(text) > 500 else text
            print(preview)
            print("--- FIN DU TEST PDFMINER ---")
        else:
            print("\nPDFMiner.six n'est pas installé. Pour tester cette alternative:")
            print("pip install pdfminer.six")
    except Exception as e:
        print(f"Erreur avec PDFMiner.six: {str(e)}")

# Test avec PyMuPDF (méthode alternative) si disponible
def extract_text_with_pymupdf(file_path):
    try:
        import importlib.util
        if importlib.util.find_spec("fitz"):
            import fitz  # PyMuPDF
            print("\n--- TEST AVEC PYMUPDF ---")
            
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            print(f"Caractères extraits: {len(text)}")
            preview = text[:500] + "..." if len(text) > 500 else text
            print(preview)
            print("--- FIN DU TEST PYMUPDF ---")
        else:
            print("\nPyMuPDF n'est pas installé. Pour tester cette alternative:")
            print("pip install pymupdf")
    except Exception as e:
        print(f"Erreur avec PyMuPDF: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_parser.py chemin/vers/fichier.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    extract_text_from_pdf(file_path)
    
    # Tester les méthodes alternatives si disponibles
    extract_text_with_pdfminer(file_path)
    extract_text_with_pymupdf(file_path)
    
    print("\nSi PyPDF2 ne fonctionne pas correctement avec votre fichier,")
    print("essayez d'installer une des bibliothèques alternatives:")
    print("pip install pdfminer.six  # Pour utiliser PDFMiner")
    print("pip install pymupdf       # Pour utiliser PyMuPDF (généralement plus performant)")
