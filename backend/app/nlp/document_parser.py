from typing import Dict, Any
from app.nlp.document_classifier import detect_document_type
from app.nlp.job_parser import parse_job_description
from app.nlp.cv_parser import parse_cv

def parse_document(text: str) -> Dict[str, Any]:
    """
    Parse automatiquement un document en détectant son type
    (CV ou fiche de poste) et en l'analysant en conséquence.
    
    Args:
        text: Le texte du document à analyser
        
    Returns:
        Dict: Contient les informations extraites, le type de document et les scores de confiance
    """
    # Détecter le type de document
    doc_type = detect_document_type(text)
    
    # Parser selon le type de document
    if doc_type == "cv":
        results = parse_cv(text)
        parsing_results = {
            "doc_type": "cv",
            **results
        }
    else:  # job_posting
        results = parse_job_description(text)
        parsing_results = {
            "doc_type": "job_posting",
            **results
        }
    
    return parsing_results