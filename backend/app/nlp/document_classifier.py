import re
import spacy
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import os

# Importations optionnelles pour ML
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from joblib import dump, load
    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False


class DocumentClassifier:
    def __init__(self, model_path="models/doc_classifier.joblib"):
        """
        Classificateur de documents utilisant ML avec repli sur règles heuristiques
        """
        # Initialiser SpaCy
        try:
            self.nlp = spacy.load("fr_core_news_lg")
        except OSError:
            spacy.cli.download("fr_core_news_lg")
            self.nlp = spacy.load("fr_core_news_lg")
        
        # Charger le modèle s'il existe et si les dépendances sont installées
        self.model_path = model_path
        self.vectorizer = None
        self.classifier = None
        self.use_ml = False
        
        if HAS_ML_DEPS and os.path.exists(model_path):
            try:
                self.classifier, self.vectorizer = load(model_path)
                self.use_ml = True
            except:
                print("Impossible de charger le modèle ML, utilisation des règles")
        
        # Indicateurs pour les règles heuristiques (repli)
        self.cv_indicators = [
            r'\bcurriculum\s?vitae\b', r'\bcv\b', r'\brésumé\b',
            r'\bformation(s)?\b', r'\bcompétences?\b.*\bexpériences?\b',
            r'\bcoordonnées\b.*\bpersonnelles\b', r'\blangues?\s(parlée|maternelle)s?\b',
            r'\bcentres\s+d\'intérêts?\b', r'\bloisirs\b'
        ]
        
        self.job_indicators = [
            r'\brecherch[eo]ns\b', r'\boffre\s+d\'emploi\b', r'\bposte\s+à\s+pourvoir\b',
            r'\bnotre\s+entreprise\b', r'\bdescription\s+du\s+poste\b', r'\bmissions?\b',
            r'\bprofil\s+recherché\b', r'\btype\s+de\s+contrat\b', r'\brémunération\b'
        ]
    
    def detect_document_type(self, text: str) -> str:
        """
        Détermine si le document est un CV ou une fiche de poste
        en utilisant ML avec repli sur règles
        
        Args:
            text: Le texte du document à analyser
            
        Returns:
            str: 'cv' ou 'job_posting'
        """
        # Tentative de classification ML si disponible
        if self.use_ml and self.classifier and self.vectorizer:
            try:
                # Prétraitement similaire à l'entraînement
                text_features = self.vectorizer.transform([text])
                prediction = self.classifier.predict(text_features)[0]
                confidence = np.max(self.classifier.predict_proba(text_features)[0])
                
                # Utiliser la prédiction ML uniquement si confiance suffisante
                if confidence > 0.7:
                    return prediction
            except Exception as e:
                print(f"Erreur de classification ML: {e}")
        
        # Repli sur les règles si ML non disponible ou peu confiant
        return self._rule_based_classification(text)
    
    def _rule_based_classification(self, text: str) -> str:
        """
        Classification basée sur des règles (utilisée comme repli)
        """
        text_lower = text.lower()
        
        # Compter les occurrences d'indicateurs
        cv_score = sum(1 for pattern in self.cv_indicators if re.search(pattern, text_lower))
        job_score = sum(1 for pattern in self.job_indicators if re.search(pattern, text_lower))
        
        # Structure typique de CV: sections clairement définies
        cv_structure_score = len(re.findall(r'\n[A-Z\s]{3,30}\s*:?\n', text)) * 1.5
        
        # Paragraphes dans les fiches de poste
        text_lines = [line for line in text.split('\n') if line.strip()]
        avg_line_length = sum(len(line) for line in text_lines) / max(1, len(text_lines))
        job_structure_score = 0
        if avg_line_length > 50:
            job_structure_score += 2
        
        # Autres indicateurs structurels
        bullet_points = len(re.findall(r'[\•\-\*]\s+\w+', text))
        if bullet_points > 10:  # Beaucoup de points dans un CV
            cv_score += 2
            
        # Recherche d'une chronologie inversée (typique des CV)
        years = re.findall(r'\b20[0-2]\d\b', text)
        if len(years) > 3 and any(years[i] > years[i+1] for i in range(len(years)-1)):
            cv_score += 2
        
        # Ajustement des scores
        cv_score += cv_structure_score
        job_score += job_structure_score
        
        # Décision
        return 'cv' if cv_score > job_score else 'job_posting'
    
    def train(self, texts: List[str], labels: List[str]) -> None:
        """
        Entraîne le classificateur avec des exemples fournis
        
        Note: Cette fonction nécessite scikit-learn et joblib installés.
        """
        if not HAS_ML_DEPS:
            raise ImportError("L'entraînement nécessite scikit-learn et joblib")
            
        if not texts or not labels or len(texts) != len(labels):
            raise ValueError("Données d'entraînement invalides")
        
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        features = self.vectorizer.fit_transform(texts)
        
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.classifier.fit(features, labels)
        
        # Sauvegarder le modèle
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        dump((self.classifier, self.vectorizer), self.model_path)
        self.use_ml = True
    
    def preprocess_document(self, text: str) -> Dict[str, Any]:
        """
        Prétraite le document pour l'analyse
        
        Args:
            text: Le texte du document à analyser
            
        Returns:
            Dict: Contient le texte prétraité, le type de document et d'autres informations
        """
        # Normalisation du texte
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        # Détecter la langue (si possible)
        lang = "fr"  # Par défaut
        try:
            sample = text[:1000]  # Échantillon pour efficacité
            lang_doc = self.nlp(sample)
            lang = lang_doc.lang_
        except:
            pass
        
        # Nettoyage avancé
        text = self._clean_text(text)
        
        # Détecter le type
        doc_type = self.detect_document_type(text)
        
        # Analyser avec spaCy (limiter la taille pour performance)
        doc = None
        try:
            doc = self.nlp(text[:100000])
        except Exception as e:
            print(f"Erreur lors de l'analyse spaCy: {e}")
        
        return {
            "text": text,
            "doc_type": doc_type,
            "language": lang,
            "spacy_doc": doc
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoyage avancé du texte
        """
        # Supprimer les caractères non imprimables
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
        
        # Normaliser les sauts de ligne
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Supprimer les lignes vides multiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text


# Pour maintenir la compatibilité avec le code existant
def detect_document_type(text: str) -> str:
    """
    Détecter le type de document (interface compatible avec le code existant)
    """
    classifier = DocumentClassifier()
    return classifier.detect_document_type(text)

def preprocess_document(text: str) -> Dict[str, Any]:
    """
    Prétraite le document et détermine son type (interface compatible)
    """
    classifier = DocumentClassifier()
    return classifier.preprocess_document(text)
