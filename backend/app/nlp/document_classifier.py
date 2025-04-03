import re
import spacy
from typing import Dict, Any, Tuple

def detect_document_type(text: str) -> str:
    """
    Détermine si le document est un CV ou une fiche de poste.
    
    Args:
        text: Le texte du document à analyser
        
    Returns:
        str: 'cv' ou 'job_posting'
    """
    # Conversion en minuscules pour faciliter la recherche
    text_lower = text.lower()
    
    # Indicateurs de CV
    cv_indicators = [
        r'\bcurriculum\s?vitae\b',
        r'\bcv\b',
        r'\brésumé\b',
        r'\bformation(s)?\b',
        r'\bcompétences?\b.*\bexpériences?\b',
        r'\bcoordonnées\b.*\bpersonnelles\b',
        r'\blangues?\s(parlée|maternelle)s?\b',
        r'\bcentres\s+d\'intérêts?\b',
        r'\bloisirs\b'
    ]
    
    # Indicateurs de fiche de poste
    job_indicators = [
        r'\brecherch[eo]ns\b',
        r'\boffre\s+d\'emploi\b',
        r'\bposte\s+à\s+pourvoir\b',
        r'\bnotre\s+entreprise\b',
        r'\bdescription\s+du\s+poste\b',
        r'\bmissions?\b',
        r'\bprofil\s+recherché\b',
        r'\btype\s+de\s+contrat\b',
        r'\brémunération\b'
    ]
    
    # Compter les occurrences d'indicateurs
    cv_score = sum(1 for pattern in cv_indicators if re.search(pattern, text_lower))
    job_score = sum(1 for pattern in job_indicators if re.search(pattern, text_lower))
    
    # Structure typique de CV: sections clairement définies avec peu de texte dans chaque section
    cv_structure_score = len(re.findall(r'\n[A-Z\s]{3,30}\s*:?\n', text)) * 1.5
    
    # Les fiches de poste ont généralement des paragraphes plus longs
    avg_line_length = sum(len(line) for line in text.split('\n') if line.strip()) / max(1, len([line for line in text.split('\n') if line.strip()]))
    job_structure_score = 0
    if avg_line_length > 50:  # Les lignes dans les fiches de poste sont généralement plus longues
        job_structure_score += 2
    
    # Ajustement des scores
    cv_score += cv_structure_score
    job_score += job_structure_score
    
    # Décision
    if cv_score > job_score:
        return 'cv'
    else:
        return 'job_posting'

def preprocess_document(text: str) -> Dict[str, Any]:
    """
    Prétraite le document et détermine son type.
    
    Args:
        text: Le texte du document à analyser
        
    Returns:
        Dict: Contient le texte prétraité, le type de document et d'autres informations
    """
    # Déterminer le type de document
    doc_type = detect_document_type(text)
    
    # Charger spaCy si nécessaire
    try:
        nlp = spacy.load("fr_core_news_lg")
    except OSError:
        spacy.cli.download("fr_core_news_lg")
        nlp = spacy.load("fr_core_news_lg")
    
    # Normalisation du texte
    text = text.replace('\xa0', ' ')  # Remplace les espaces insécables
    text = re.sub(r'\s+', ' ', text)  # Remplace espaces multiples
    
    # Analyser avec spaCy
    doc = nlp(text)
    
    return {
        "text": text,
        "doc_type": doc_type,
        "spacy_doc": doc,
        # Découpage en sections à faire en fonction du type de document
    }