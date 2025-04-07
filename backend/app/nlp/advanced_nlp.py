"""
Module d'intégration de techniques NLP avancées
Ce module utilise des modèles comme BERT pour mieux comprendre le contexte
et extraire des informations implicites des documents.
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
import re
import numpy as np
from pathlib import Path

# Initialisation du logging
logger = logging.getLogger(__name__)

# Constante pour le contrôle des imports conditionnels
HAS_TRANSFORMERS = False
HAS_TORCH = False

# Importations conditionnelles pour éviter de casser le code si les bibliothèques ne sont pas installées
try:
    import torch
    HAS_TORCH = True
    
    from transformers import (
        AutoTokenizer, 
        AutoModel, 
        AutoModelForSequenceClassification,
        AutoModelForTokenClassification,
        pipeline
    )
    HAS_TRANSFORMERS = True
except ImportError:
    logger.warning("La bibliothèque transformers ou PyTorch n'est pas installée. Fonctionnalités avancées de NLP limitées.")


class BERTExtractor:
    """
    Classe pour utiliser des modèles BERT et dérivés afin d'extraire des informations
    contextuelles et implicites des documents.
    """
    
    def __init__(self, model_dir=None):
        """
        Initialise l'extracteur BERT avec les modèles nécessaires.
        
        Args:
            model_dir: Répertoire où stocker/charger les modèles (si None, utilise les valeurs par défaut de transformers)
        """
        self.model_dir = model_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        
        # Vérifier si les dépendances sont disponibles
        if not HAS_TRANSFORMERS or not HAS_TORCH:
            logger.warning("BERTExtractor initialisé mais transformers ou PyTorch manquant.")
            self.available = False
            return
        
        self.available = True
        
        # Modèles à initialiser paresseusement
        self._embedder = None
        self._ner_model = None
        self._sentiment_analyzer = None
        self._text_classifier = None
        self._question_answerer = None
        
        # Caches pour les résultats
        self.embedding_cache = {}
        
        logger.info("BERTExtractor initialisé avec succès.")

    def _load_embedder(self, model_name='camembert-base'):
        """
        Charge le modèle d'embedding français si nécessaire
        """
        if self._embedder is None:
            try:
                self.embedder_tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._embedder = AutoModel.from_pretrained(model_name)
                logger.info(f"Modèle d'embedding {model_name} chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle d'embedding: {e}")
                return False
        
        return True

    def _load_ner_model(self, model_name='jean-baptiste/camembert-ner'):
        """
        Charge le modèle de NER (Named Entity Recognition) français si nécessaire
        """
        if self._ner_model is None:
            try:
                self._ner_model = pipeline("ner", model=model_name)
                logger.info(f"Modèle NER {model_name} chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle NER: {e}")
                return False
        
        return True

    def _load_sentiment_analyzer(self, model_name='nlptown/bert-base-multilingual-uncased-sentiment'):
        """
        Charge le modèle d'analyse de sentiment multilingue si nécessaire
        """
        if self._sentiment_analyzer is None:
            try:
                self._sentiment_analyzer = pipeline("sentiment-analysis", model=model_name)
                logger.info(f"Modèle d'analyse de sentiment {model_name} chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle d'analyse de sentiment: {e}")
                return False
        
        return True

    def _load_text_classifier(self, model_name='distilbert-base-uncased'):
        """
        Charge le modèle pour classification de textes si nécessaire
        Note: Ce modèle devrait être fine-tuné sur des données spécifiques à Commitment
        """
        if self._text_classifier is None:
            try:
                # Vérifier si un modèle fine-tuné existe
                classifier_path = os.path.join(self.model_dir, "classifier")
                if os.path.exists(classifier_path):
                    self._text_classifier = AutoModelForSequenceClassification.from_pretrained(classifier_path)
                    logger.info(f"Modèle de classification chargé depuis {classifier_path}.")
                else:
                    # Charger un modèle pré-entraîné par défaut
                    self._text_classifier = pipeline("text-classification", model=model_name)
                    logger.info(f"Modèle de classification {model_name} chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle de classification: {e}")
                return False
        
        return True

    def _load_question_answerer(self, model_name='distilbert-base-cased-distilled-squad'):
        """
        Charge le modèle de question-réponse si nécessaire
        """
        if self._question_answerer is None:
            try:
                self._question_answerer = pipeline("question-answering", model=model_name)
                logger.info(f"Modèle QA {model_name} chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle QA: {e}")
                return False
        
        return True

    def get_document_embeddings(self, text: str) -> np.ndarray:
        """
        Génère un embedding pour le document entier.
        
        Args:
            text: Texte du document
            
        Returns:
            np.ndarray: Vecteur d'embedding du document
        """
        if not self.available:
            logger.warning("get_document_embeddings appelé mais transformers n'est pas disponible.")
            return np.zeros(768)  # Retourner un vecteur de zéros en cas d'erreur
        
        # Utiliser le cache si disponible
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if not self._load_embedder():
            return np.zeros(768)  # Retourner un vecteur de zéros en cas d'erreur
        
        try:
            # Pour les documents longs, découper et moyenner
            max_length = self.embedder_tokenizer.model_max_length - 10
            chunks = []
            
            # Diviser le texte en chunks de tokens
            tokens = self.embedder_tokenizer.tokenize(text)
            
            for i in range(0, len(tokens), max_length):
                chunk = tokens[i:i + max_length]
                chunks.append(self.embedder_tokenizer.convert_tokens_to_string(chunk))
            
            # Si pas de chunks (texte vide), retourner un vecteur de zéros
            if not chunks:
                return np.zeros(768)
            
            # Encoder chaque chunk
            embeddings = []
            
            for chunk in chunks:
                inputs = self.embedder_tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
                
                with torch.no_grad():
                    outputs = self._embedder(**inputs)
                
                # Utiliser la représentation [CLS] comme embedding du document
                embedding = outputs.last_hidden_state[:, 0, :].numpy()
                embeddings.append(embedding)
            
            # Moyenner sur tous les chunks
            avg_embedding = np.mean(embeddings, axis=0).squeeze()
            
            # Mettre en cache
            self.embedding_cache[text] = avg_embedding
            
            return avg_embedding
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding: {e}")
            return np.zeros(768)  # Retourner un vecteur de zéros en cas d'erreur

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrait les entités nommées d'un texte avec leur type.
        
        Args:
            text: Texte à analyser
            
        Returns:
            List[Dict]: Liste des entités trouvées avec leur type et position
        """
        if not self.available:
            logger.warning("extract_entities appelé mais transformers n'est pas disponible.")
            return []
        
        if not self._load_ner_model():
            return []
        
        try:
            # Pour les textes longs, traiter par morceaux
            max_length = 500  # Nombre de caractères max par morceau
            chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            
            all_entities = []
            offset = 0
            
            for chunk in chunks:
                ner_results = self._ner_model(chunk)
                
                # Regrouper les entités multi-token
                entities = []
                current_entity = None
                
                for item in ner_results:
                    # Si c'est une continuation d'entité et que nous avons une entité en cours
                    if item["entity"].startswith("I-") and current_entity and current_entity["entity_type"] == item["entity"][2:]:
                        # Mettre à jour l'entité en cours
                        current_entity["word"] += item["word"].replace("##", "")
                        current_entity["end"] = item["end"] + offset
                    else:
                        # Si nous avions une entité en cours, l'ajouter à la liste
                        if current_entity:
                            entities.append(current_entity)
                        
                        # Commencer une nouvelle entité
                        if item["entity"].startswith("B-") or item["entity"].startswith("I-"):
                            entity_type = item["entity"][2:]  # Enlever B- ou I-
                            current_entity = {
                                "word": item["word"].replace("##", ""),
                                "entity_type": entity_type,
                                "score": item["score"],
                                "start": item["start"] + offset,
                                "end": item["end"] + offset
                            }
                        else:
                            current_entity = None
                
                # Ajouter la dernière entité s'il y en a une
                if current_entity:
                    entities.append(current_entity)
                
                all_entities.extend(entities)
                offset += len(chunk)
            
            return all_entities
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'entités: {e}")
            return []

    def extract_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Score de sentiment et label
        """
        if not self.available:
            logger.warning("extract_sentiment appelé mais transformers n'est pas disponible.")
            return {"label": "NEUTRAL", "score": 0.5}
        
        if not self._load_sentiment_analyzer():
            return {"label": "NEUTRAL", "score": 0.5}
        
        try:
            # Pour les textes longs, analyser par paragraphe et moyenner
            paragraphs = re.split(r'\n{2,}', text)
            
            results = []
            for para in paragraphs:
                if len(para.strip()) > 10:  # Ignorer les paragraphes trop courts
                    result = self._sentiment_analyzer(para[:512])[0]  # Limiter la longueur
                    results.append(result)
            
            if not results:
                return {"label": "NEUTRAL", "score": 0.5}
            
            # Calculer la moyenne pondérée des scores
            # En supposant que les labels sont de la forme 1 STAR (négatif) à 5 STARS (positif)
            scores = []
            for result in results:
                # Convertir le label en score numérique (1-5)
                if "star" in result["label"].lower():
                    try:
                        sentiment_score = int(result["label"].split()[0]) / 5.0  # Normaliser entre 0 et 1
                        scores.append((sentiment_score, result["score"]))
                    except:
                        scores.append((0.5, result["score"]))  # Valeur par défaut
                else:
                    # Si le format est différent, utiliser une logique alternative
                    if "positive" in result["label"].lower():
                        scores.append((0.75, result["score"]))
                    elif "negative" in result["label"].lower():
                        scores.append((0.25, result["score"]))
                    else:
                        scores.append((0.5, result["score"]))
            
            # Calcul de la moyenne pondérée
            weighted_score = sum(score * weight for score, weight in scores) / sum(weight for _, weight in scores)
            
            # Déterminer le label en fonction du score moyen
            if weighted_score > 0.7:
                label = "POSITIVE"
            elif weighted_score < 0.4:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
            
            return {"label": label, "score": weighted_score}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment: {e}")
            return {"label": "NEUTRAL", "score": 0.5}

    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        """
        Utilise un modèle de question-réponse pour extraire des informations spécifiques.
        
        Args:
            context: Texte de contexte
            question: Question à répondre
            
        Returns:
            Dict: Réponse, score et position dans le texte
        """
        if not self.available:
            logger.warning("answer_question appelé mais transformers n'est pas disponible.")
            return {"answer": "", "score": 0.0}
        
        if not self._load_question_answerer():
            return {"answer": "", "score": 0.0}
        
        try:
            # Limiter la taille du contexte si nécessaire
            if len(context) > 1000:
                # Rechercher le meilleur segment de contexte pour la question
                segments = [context[i:i+1000] for i in range(0, len(context), 500)]  # Chevauchement de 500 caractères
                
                best_answer = None
                best_score = -1
                
                for segment in segments:
                    result = self._question_answerer(question=question, context=segment)
                    if result["score"] > best_score:
                        best_score = result["score"]
                        best_answer = result
                
                return best_answer
            else:
                return self._question_answerer(question=question, context=context)
            
        except Exception as e:
            logger.error(f"Erreur lors de la réponse à la question: {e}")
            return {"answer": "", "score": 0.0}

    def classify_text(self, text: str, labels: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Classifie un texte dans des catégories prédéfinies.
        
        Args:
            text: Texte à classifier
            labels: Liste de labels possibles (optionnel)
            
        Returns:
            Dict: Scores pour chaque label
        """
        if not self.available:
            logger.warning("classify_text appelé mais transformers n'est pas disponible.")
            return {}
        
        if not self._load_text_classifier():
            return {}
        
        try:
            # Si le modèle est un pipeline pré-construit
            if isinstance(self._text_classifier, pipeline):
                result = self._text_classifier(text[:512])  # Limiter la longueur
                
                # Convertir le résultat en dictionnaire
                if isinstance(result, list):
                    return {item["label"]: item["score"] for item in result}
                else:
                    return {result["label"]: result["score"]}
            
            # Si c'est un modèle custom (fine-tuné)
            else:
                # À implémenter selon la structure du modèle custom
                pass
            
            return {}
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification du texte: {e}")
            return {}

    def infer_work_environment_preferences(self, cv_text: str) -> Dict[str, float]:
        """
        Déduit les préférences d'environnement de travail à partir d'un CV.
        
        Args:
            cv_text: Texte du CV
            
        Returns:
            Dict: Scores de préférence pour différents environnements
        """
        if not self.available:
            logger.warning("infer_work_environment_preferences appelé mais transformers n'est pas disponible.")
            return {}
        
        preferences = {
            "remote": 0.0,
            "office": 0.0,
            "hybrid": 0.0,
            "startup": 0.0,
            "large_company": 0.0,
            "international": 0.0
        }
        
        try:
            # 1. Utiliser le modèle de question-réponse pour des inférences directes
            questions = [
                ("Quelle expérience a cette personne avec le télétravail?", "remote"),
                ("Quelle expérience a cette personne dans un environnement de bureau?", "office"),
                ("Cette personne a-t-elle travaillé dans des startups?", "startup"),
                ("Cette personne a-t-elle travaillé dans de grandes entreprises?", "large_company"),
                ("Cette personne a-t-elle une expérience internationale?", "international")
            ]
            
            for question, key in questions:
                answer = self.answer_question(cv_text, question)
                if answer["answer"] and answer["score"] > 0.3:
                    # Analyser le sentiment de la réponse
                    sentiment = self.extract_sentiment(answer["answer"])
                    
                    # Calculer un score basé sur la confiance de la réponse et le sentiment
                    score = answer["score"] * (sentiment["score"] if sentiment["label"] != "NEGATIVE" else 0.3)
                    preferences[key] = min(1.0, score)
            
            # 2. Détecter des mots-clés spécifiques et patterns
            keyword_patterns = {
                "remote": [r'\btélétravail\b', r'\bremote\b', r'\bà distance\b', r'\bhome office\b'],
                "office": [r'\bbureau\b', r'\bprésentiel\b', r'\bopen space\b', r'\blocaux\b'],
                "hybrid": [r'\bhybride\b', r'\bmixte\b', r'\bflexible\b'],
                "startup": [r'\bstartup\b', r'\bentrepreneur\b', r'\binnovation\b', r'\bscale-up\b'],
                "large_company": [r'\bmultinationale\b', r'\bgroupe\b', r'\bcorporate\b', r'\bgrande entreprise\b'],
                "international": [r'\binternational\b', r'\bétranger\b', r'\bangla(is|ise)\b', r'\bmondial\b']
            }
            
            for key, patterns in keyword_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, cv_text.lower())
                    if matches:
                        # Augmenter le score selon le nombre de mentions
                        preferences[key] += min(0.5, len(matches) * 0.1)
            
            # 3. Analyse des expériences passées pour déduire les préférences
            # Extraire les entités d'organisation et analyser leur type
            entities = self.extract_entities(cv_text)
            for entity in entities:
                if entity["entity_type"] == "ORG" and entity["score"] > 0.7:
                    org_name = entity["word"].lower()
                    
                    # Indicateurs de startup vs grande entreprise
                    if any(keyword in org_name for keyword in ["startup", "lab", "tech", "digital"]):
                        preferences["startup"] += 0.1
                    elif any(keyword in org_name for keyword in ["group", "corp", "inc", "sa", "international"]):
                        preferences["large_company"] += 0.1
                    
                    # Indiquer international
                    if any(keyword in org_name for keyword in ["global", "world", "international", "eu", "us"]):
                        preferences["international"] += 0.1
            
            # Normaliser les scores entre 0 et 1
            for key in preferences:
                preferences[key] = min(1.0, preferences[key])
            
            # Assurer que la somme des scores remote/office/hybrid est cohérente
            work_mode_sum = preferences["remote"] + preferences["office"] + preferences["hybrid"]
            if work_mode_sum > 1.0:
                scaling_factor = 1.0 / work_mode_sum
                preferences["remote"] *= scaling_factor
                preferences["office"] *= scaling_factor
                preferences["hybrid"] *= scaling_factor
            
            return preferences
            
        except Exception as e:
            logger.error(f"Erreur lors de l'inférence des préférences: {e}")
            return preferences

    def infer_work_style_preferences(self, cv_text: str) -> Dict[str, float]:
        """
        Déduit les préférences de mode de travail à partir d'un CV.
        
        Args:
            cv_text: Texte du CV
            
        Returns:
            Dict: Scores de préférence pour différents styles de travail
        """
        if not self.available:
            logger.warning("infer_work_style_preferences appelé mais transformers n'est pas disponible.")
            return {}
        
        preferences = {
            "autonomy": 0.0,
            "team_work": 0.0,
            "structured": 0.0,
            "flexible": 0.0,
            "creative": 0.0,
            "analytical": 0.0
        }
        
        try:
            # 1. Utiliser le modèle de question-réponse pour des inférences directes
            questions = [
                ("Cette personne préfère-t-elle travailler en autonomie?", "autonomy"),
                ("Cette personne préfère-t-elle le travail d'équipe?", "team_work"),
                ("Cette personne est-elle créative et innovante?", "creative"),
                ("Cette personne est-elle analytique et structurée?", "analytical")
            ]
            
            for question, key in questions:
                answer = self.answer_question(cv_text, question)
                if answer["answer"] and answer["score"] > 0.3:
                    # Analyser le sentiment de la réponse
                    sentiment = self.extract_sentiment(answer["answer"])
                    
                    # Calculer un score basé sur la confiance de la réponse et le sentiment
                    score = answer["score"] * (sentiment["score"] if sentiment["label"] != "NEGATIVE" else 0.3)
                    preferences[key] = min(1.0, score)
            
            # 2. Analyse des mots-clés et expressions
            keyword_patterns = {
                "autonomy": [
                    r'\bautonom(e|ie)\b', r'\bindépendan(t|ce)\b', r'\binitiative\b', 
                    r'\bresponsab(le|ilité)\b', r'\bauto-gestion\b'
                ],
                "team_work": [
                    r'\béquipe\b', r'\bcollaborat(if|ion)\b', r'\bcollect(if|ive)\b',
                    r'\bgroupe\b', r'\bpartag(e|er)\b', r'\bensemble\b'
                ],
                "structured": [
                    r'\bstructur(e|é)\b', r'\bméthodique\b', r'\borganis(é|ation)\b',
                    r'\brigoureux\b', r'\bprécis\b', r'\bsystématique\b'
                ],
                "flexible": [
                    r'\bflexible\b', r'\badaptab(le|ilité)\b', r'\bpolyvalent\b',
                    r'\bagile\b', r'\bchangement\b', r'\bévolution\b'
                ],
                "creative": [
                    r'\bcréati(f|ve|vité)\b', r'\binnov(ant|ation)\b', r'\boriginal\b',
                    r'\bidées\b', r'\bconception\b', r'\bdesign\b'
                ],
                "analytical": [
                    r'\banalytique\b', r'\banalyse\b', r'\blogique\b',
                    r'\brésolution de problèmes\b', r'\bdata\b', r'\brecherche\b'
                ]
            }
            
            for key, patterns in keyword_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, cv_text.lower())
                    if matches:
                        # Augmenter le score selon le nombre de mentions
                        preferences[key] += min(0.5, len(matches) * 0.1)
            
            # 3. Analyse du contexte et des expériences
            # Analyse de la structure des expériences et des activités mentionnées
            # Exemples de patterns d'autonomie vs travail d'équipe
            team_lead_patterns = [
                r'\bdirig(er|é)\b.*\béquipe\b', r'\bmanag(er|é)\b.*\béquipe\b',
                r'\bresponsable d\'équipe\b', r'\bteam lead\b', r'\bcoordinat(eur|ion)\b',
                r'\bsupervision\b', r'\bencadrement\b'
            ]
            
            solo_work_patterns = [
                r'\bseul\b', r'\bindépendamment\b', r'\ben autonomie\b',
                r'\bchargé de\b', r'\bmission\b.*\bindépendante\b'
            ]
            
            # Compter les occurrences des patterns
            team_lead_count = sum(len(re.findall(pattern, cv_text.lower())) for pattern in team_lead_patterns)
            solo_work_count = sum(len(re.findall(pattern, cv_text.lower())) for pattern in solo_work_patterns)
            
            # Ajuster les scores en fonction des résultats
            if team_lead_count > 0:
                preferences["team_work"] += min(0.3, team_lead_count * 0.1)
            
            if solo_work_count > 0:
                preferences["autonomy"] += min(0.3, solo_work_count * 0.1)
            
            # Normaliser les scores entre 0 et 1
            for key in preferences:
                preferences[key] = min(1.0, preferences[key])
            
            # Équilibrage des scores pour les dimensions opposées
            pairs = [
                ("autonomy", "team_work"),
                ("structured", "flexible"),
                ("creative", "analytical")
            ]
            
            for key1, key2 in pairs:
                # Si les deux scores sont élevés, légèrement équilibrer
                total = preferences[key1] + preferences[key2]
                if total > 1.3:  # Seuil arbitraire pour "élevé"
                    # Réduire proportionnellement pour garder leur ratio mais limiter leur somme
                    scale = 1.3 / total
                    preferences[key1] *= scale
                    preferences[key2] *= scale
            
            return preferences
            
        except Exception as e:
            logger.error(f"Erreur lors de l'inférence des préférences de mode de travail: {e}")
            return preferences


# Fonctions d'interface pour l'utilisation dans d'autres modules
def get_bert_extractor() -> BERTExtractor:
    """
    Obtient une instance de BERTExtractor.
    
    Returns:
        BERTExtractor: Instance de l'extracteur BERT
    """
    return BERTExtractor()

def has_advanced_nlp_capabilities() -> bool:
    """
    Vérifie si les capacités avancées de NLP sont disponibles.
    
    Returns:
        bool: True si les dépendances sont disponibles
    """
    return HAS_TRANSFORMERS and HAS_TORCH