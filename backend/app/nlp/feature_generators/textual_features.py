"""
Générateur de features basées sur les similarités textuelles.
"""

import logging
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class TextualSimilarityGenerator:
    """
    Générateur de features pour les similarités textuelles entre profils et offres.
    """
    
    def __init__(self, embedding_model="paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialise le générateur de features textuelles.
        
        Args:
            embedding_model: Nom du modèle Sentence-BERT pour les embeddings
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialisation du vectoriseur TF-IDF pour les textes généraux
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85,
            stop_words=['french', 'english'],
            use_idf=True
        )
        
        # Vectoriseur spécifique pour les titres de poste (moins strict)
        self.title_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            stop_words=None,  # Garder les mots courants pour les titres
            use_idf=True
        )
        
        # Vectoriseur Count pour BM25
        self.count_vectorizer = CountVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.85,
            stop_words=['french', 'english']
        )
        
        # Initialisation du modèle d'embeddings
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer(embedding_model)
                self.embeddings_available = True
            except Exception as e:
                self.logger.warning(f"Impossible de charger le modèle d'embeddings: {e}")
                self.embeddings_available = False
        else:
            self.logger.warning("Package sentence-transformers non disponible. Fonctionnalités d'embedding désactivées.")
            self.embeddings_available = False
        
        # Charger spaCy pour le traitement du texte
        try:
            self.nlp = spacy.load("fr_core_news_md")
        except:
            self.logger.warning("Modèle fr_core_news_md non trouvé, chargement du modèle plus petit.")
            try:
                self.nlp = spacy.load("fr_core_news_sm")
            except:
                self.logger.error("Aucun modèle spaCy disponible.")
                self.nlp = None
    
    def generate_text_features(self, candidate_profile, job_profile):
        """
        Génère les features de similarité textuelle entre un candidat et une offre.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            Dict: Features de similarité textuelle
        """
        features = {}
        
        # Extraction des textes
        candidate_experience_text = self._extract_experience_text(candidate_profile)
        job_description = self._extract_job_description(job_profile)
        
        candidate_full_profile = self._extract_full_profile(candidate_profile)
        job_full_profile = self._extract_full_profile(job_profile)
        
        candidate_titles = self._extract_job_titles(candidate_profile)
        job_title = self._extract_job_title(job_profile)
        
        # 1. Similarité sémantique entre expérience et description de poste
        features["experience_job_semantic_sim"] = self.calculate_semantic_similarity(
            candidate_experience_text, job_description)
        
        # 2. Similarité TF-IDF entre expérience et description de poste
        features["experience_job_tfidf_sim"] = self.calculate_tfidf_similarity(
            candidate_experience_text, job_description)
        
        # 3. Score BM25 entre profil complet et offre d'emploi
        features["profile_job_bm25"] = self.calculate_bm25_score(
            candidate_full_profile, job_full_profile)
        
        # 4. Similarité des titres de poste
        features["job_title_similarity"] = self.calculate_job_title_similarity(
            candidate_titles, job_title)
        
        # 5. Extraction et matching d'entités nommées
        features["named_entities_match"] = self.calculate_named_entities_match(
            candidate_full_profile, job_full_profile)
        
        # 6. Analyse des verbes d'action et responsabilités
        features["action_verbs_match"] = self.calculate_action_verbs_match(
            candidate_experience_text, job_description)
        
        # 7. Analyse des mots-clés spécifiques au domaine
        features["domain_keywords_match"] = self.calculate_domain_keywords_match(
            candidate_full_profile, job_full_profile)
        
        # 8. Correspondance des exigences et compétences
        features["requirements_skills_match"] = self.calculate_requirements_match(
            candidate_profile, job_profile)
        
        return features
    
    def _extract_experience_text(self, candidate_profile):
        """
        Extrait le texte d'expérience professionnelle du candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            str: Texte combiné des expériences
        """
        if not candidate_profile:
            return ""
        
        experience_texts = []
        
        # Chercher des expériences structurées
        if "experience" in candidate_profile:
            experiences = candidate_profile["experience"]
            
            if isinstance(experiences, list):
                for exp in experiences:
                    if isinstance(exp, dict):
                        # Extraire la description
                        if "description" in exp:
                            experience_texts.append(exp["description"])
                        
                        # Extraire d'autres champs pertinents
                        for field in ["title", "company", "responsibilities", "achievements"]:
                            if field in exp and exp[field]:
                                experience_texts.append(exp[field])
                    elif isinstance(exp, str):
                        experience_texts.append(exp)
            elif isinstance(experiences, str):
                experience_texts.append(experiences)
        
        # Chercher d'autres champs liés à l'expérience
        experience_fields = [
            "work_experience", "professional_experience", 
            "job_history", "employment_history"
        ]
        
        for field in experience_fields:
            if field in candidate_profile:
                value = candidate_profile[field]
                
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for subfield in ["description", "title", "responsibilities"]:
                                if subfield in item:
                                    experience_texts.append(item[subfield])
                        elif isinstance(item, str):
                            experience_texts.append(item)
                elif isinstance(value, str):
                    experience_texts.append(value)
        
        # Combiner les textes
        return " ".join(experience_texts)
    
    def _extract_job_description(self, job_profile):
        """
        Extrait la description de poste d'une offre d'emploi.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Description combinée du poste
        """
        if not job_profile:
            return ""
        
        description_texts = []
        
        # Chercher différents champs de description
        description_fields = [
            "description", "job_description", "responsibilities", 
            "role_description", "mission", "detailed_description"
        ]
        
        for field in description_fields:
            if field in job_profile:
                value = job_profile[field]
                
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            description_texts.append(item)
                elif isinstance(value, str):
                    description_texts.append(value)
        
        # Ajouter les compétences requises
        skills_fields = ["required_skills", "skills", "technical_skills"]
        for field in skills_fields:
            if field in job_profile:
                value = job_profile[field]
                
                if isinstance(value, list):
                    description_texts.append(" ".join(value))
                elif isinstance(value, str):
                    description_texts.append(value)
        
        # Ajouter les exigences
        req_fields = ["requirements", "qualifications", "prerequisites"]
        for field in req_fields:
            if field in job_profile:
                value = job_profile[field]
                
                if isinstance(value, list):
                    description_texts.append(" ".join(value))
                elif isinstance(value, str):
                    description_texts.append(value)
        
        # Combiner les textes
        return " ".join(description_texts)
    
    def _extract_full_profile(self, profile):
        """
        Extrait le texte complet d'un profil (candidat ou offre).
        
        Args:
            profile: Profil à extraire
            
        Returns:
            str: Texte complet du profil
        """
        if not profile:
            return ""
        
        text_parts = []
        
        # Parcourir tous les champs du profil
        for key, value in profile.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                # Pour les listes d'éléments textuels
                if all(isinstance(item, str) for item in value):
                    text_parts.append(" ".join(value))
                # Pour les listes de dictionnaires
                elif any(isinstance(item, dict) for item in value):
                    for item in value:
                        if isinstance(item, dict):
                            for _, subvalue in item.items():
                                if isinstance(subvalue, str):
                                    text_parts.append(subvalue)
            elif isinstance(value, dict):
                # Pour les dictionnaires imbriqués
                for _, subvalue in value.items():
                    if isinstance(subvalue, str):
                        text_parts.append(subvalue)
        
        # Combiner les textes
        return " ".join(text_parts)
    
    def _extract_job_titles(self, candidate_profile):
        """
        Extrait les titres de poste d'un profil de candidat.
        
        Args:
            candidate_profile: Profil du candidat
            
        Returns:
            List: Liste des titres de poste
        """
        if not candidate_profile:
            return []
        
        titles = []
        
        # Chercher le titre actuel/principal
        title_fields = ["job_title", "title", "current_title", "profession", "position"]
        for field in title_fields:
            if field in candidate_profile:
                value = candidate_profile[field]
                if isinstance(value, str) and value.strip():
                    titles.append(value.strip())
        
        # Chercher les titres dans les expériences
        if "experience" in candidate_profile:
            experiences = candidate_profile["experience"]
            
            if isinstance(experiences, list):
                for exp in experiences:
                    if isinstance(exp, dict) and "title" in exp:
                        title = exp["title"]
                        if title and title.strip():
                            titles.append(title.strip())
        
        # Éliminer les doublons
        return list(set(titles))
    
    def _extract_job_title(self, job_profile):
        """
        Extrait le titre d'une offre d'emploi.
        
        Args:
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            str: Titre du poste
        """
        if not job_profile:
            return ""
        
        # Chercher le titre du poste
        title_fields = ["job_title", "title", "position", "role"]
        for field in title_fields:
            if field in job_profile:
                value = job_profile[field]
                if isinstance(value, str) and value.strip():
                    return value.strip()
        
        return ""
    
    def calculate_semantic_similarity(self, text1, text2):
        """
        Calcule la similarité sémantique entre deux textes
        en utilisant des embeddings de phrases.
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            float: Score de similarité sémantique (0.0 - 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Si nous avons un modèle d'embeddings, utiliser la similarité sémantique
        if self.embeddings_available:
            try:
                # Calculer les embeddings
                text1_embedding = self.embeddings_model.encode([text1])[0]
                text2_embedding = self.embeddings_model.encode([text2])[0]
                
                # Calculer la similarité cosinus
                similarity = cosine_similarity(
                    [text1_embedding],
                    [text2_embedding]
                )[0][0]
                
                return float(similarity)
            except Exception as e:
                self.logger.error(f"Erreur lors du calcul de similarité sémantique: {e}")
        
        # Sinon, utiliser TF-IDF comme fallback
        return self.calculate_tfidf_similarity(text1, text2)
    
    def calculate_tfidf_similarity(self, text1, text2):
        """
        Calcule la similarité TF-IDF entre deux textes.
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            float: Score de similarité TF-IDF (0.0 - 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            # Vectoriser les textes
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de similarité TF-IDF: {e}")
            
            # Méthode de repli: mots communs
            if self.nlp:
                try:
                    text1_doc = self.nlp(text1)
                    text2_doc = self.nlp(text2)
                    
                    text1_tokens = set(token.lemma_.lower() for token in text1_doc 
                                     if not token.is_stop and not token.is_punct and token.is_alpha)
                    text2_tokens = set(token.lemma_.lower() for token in text2_doc 
                                     if not token.is_stop and not token.is_punct and token.is_alpha)
                    
                    if not text1_tokens or not text2_tokens:
                        return 0.0
                    
                    common_tokens = text1_tokens.intersection(text2_tokens)
                    
                    return len(common_tokens) / max(len(text1_tokens), len(text2_tokens))
                except Exception:
                    pass
            
            # Simple intersection de mots
            text1_words = set(re.findall(r'\\w+', text1.lower()))
            text2_words = set(re.findall(r'\\w+', text2.lower()))
            
            if not text1_words or not text2_words:
                return 0.0
                
            common_words = text1_words.intersection(text2_words)
            
            return len(common_words) / max(len(text1_words), len(text2_words))
    
    def calculate_bm25_score(self, query_text, document_text):
        """
        Calcule un score BM25 entre un texte de requête et un document.
        
        Args:
            query_text: Texte de la requête (profil candidat)
            document_text: Texte du document (description de poste)
            
        Returns:
            float: Score BM25 normalisé (0.0 - 1.0)
        """
        if not query_text or not document_text:
            return 0.0
        
        try:
            # Paramètres BM25
            k1 = 1.5
            b = 0.75
            
            # Créer la matrice de termes
            count_matrix = self.count_vectorizer.fit_transform([document_text, query_text])
            
            # Obtenir les fréquences des termes
            doc_term_freqs = count_matrix[0].toarray()[0]
            query_term_freqs = count_matrix[1].toarray()[0]
            
            # Calculer la longueur du document
            doc_length = sum(doc_term_freqs)
            avg_doc_length = doc_length  # Nous n'avons qu'un seul document
            
            # Calculer le score BM25
            bm25_score = 0.0
            
            for term_idx, query_freq in enumerate(query_term_freqs):
                if query_freq > 0 and doc_term_freqs[term_idx] > 0:
                    # Calculer l'IDF
                    idf = 1.0  # Simplifié car nous n'avons qu'un seul document
                    
                    # Calculer le facteur TF
                    tf = doc_term_freqs[term_idx]
                    tf_factor = ((k1 + 1) * tf) / (k1 * ((1 - b) + b * (doc_length / avg_doc_length)) + tf)
                    
                    # Ajouter au score
                    bm25_score += idf * tf_factor * query_freq
            
            # Normaliser le score
            if bm25_score > 0:
                # La normalisation est approximative car nous n'avons pas un corpus complet
                return min(1.0, bm25_score / (doc_length * 0.5))
            
            return 0.0
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du score BM25: {e}")
            return self.calculate_tfidf_similarity(query_text, document_text)
    
    def calculate_job_title_similarity(self, candidate_titles, job_title):
        """
        Calcule la similarité entre les titres de poste du candidat et le titre de l'offre.
        
        Args:
            candidate_titles: Liste des titres du candidat
            job_title: Titre du poste de l'offre
            
        Returns:
            float: Score de similarité des titres (0.0 - 1.0)
        """
        if not candidate_titles or not job_title:
            return 0.0
        
        best_similarity = 0.0
        
        # Comparer chaque titre du candidat avec le titre du poste
        for candidate_title in candidate_titles:
            # D'abord vérifier une correspondance exacte ou partielle
            if candidate_title.lower() == job_title.lower():
                return 1.0
            elif candidate_title.lower() in job_title.lower() or job_title.lower() in candidate_title.lower():
                best_similarity = max(best_similarity, 0.9)
            else:
                try:
                    # Utiliser le vectoriseur spécifique aux titres
                    title_tfidf = self.title_vectorizer.fit_transform([candidate_title, job_title])
                    similarity = cosine_similarity(title_tfidf[0:1], title_tfidf[1:2])[0][0]
                    best_similarity = max(best_similarity, similarity)
                except Exception:
                    # Méthode de repli: mots communs
                    candidate_words = set(candidate_title.lower().split())
                    job_words = set(job_title.lower().split())
                    
                    if candidate_words and job_words:
                        common_words = candidate_words.intersection(job_words)
                        word_similarity = len(common_words) / max(len(candidate_words), len(job_words))
                        best_similarity = max(best_similarity, word_similarity)
        
        return best_similarity
    
    def calculate_named_entities_match(self, candidate_text, job_text):
        """
        Calcule la correspondance des entités nommées entre deux textes.
        
        Args:
            candidate_text: Texte du candidat
            job_text: Texte de l'offre d'emploi
            
        Returns:
            float: Score de correspondance des entités (0.0 - 1.0)
        """
        if not self.nlp or not candidate_text or not job_text:
            return 0.0
        
        try:
            # Analyser les textes avec spaCy
            candidate_doc = self.nlp(candidate_text[:100000])  # Limiter pour éviter les problèmes de mémoire
            job_doc = self.nlp(job_text[:100000])
            
            # Extraire les entités nommées
            candidate_entities = self._extract_entities(candidate_doc)
            job_entities = self._extract_entities(job_doc)
            
            if not candidate_entities or not job_entities:
                return 0.0
            
            # Compter les entités correspondantes
            matched_entities = 0
            total_job_entities = 0
            
            for entity_type, job_items in job_entities.items():
                total_job_entities += len(job_items)
                
                if entity_type in candidate_entities:
                    for job_item in job_items:
                        if any(self._entity_match(job_item, candidate_item) 
                               for candidate_item in candidate_entities[entity_type]):
                            matched_entities += 1
            
            if total_job_entities == 0:
                return 0.0
            
            return matched_entities / total_job_entities
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de correspondance d'entités: {e}")
            return 0.0
    
    def _extract_entities(self, doc):
        """
        Extrait les entités nommées d'un document spaCy.
        
        Args:
            doc: Document spaCy
            
        Returns:
            Dict: Entités regroupées par type
        """
        entities = {}
        
        for ent in doc.ents:
            entity_type = ent.label_
            entity_text = ent.text.lower()
            
            if entity_type not in entities:
                entities[entity_type] = []
            
            entities[entity_type].append(entity_text)
        
        return entities
    
    def _entity_match(self, entity1, entity2):
        """
        Vérifie si deux entités correspondent.
        
        Args:
            entity1: Première entité
            entity2: Deuxième entité
            
        Returns:
            bool: True si les entités correspondent
        """
        # Correspondance exacte
        if entity1 == entity2:
            return True
        
        # Correspondance partielle
        if entity1 in entity2 or entity2 in entity1:
            return True
        
        # Correspondance par mots
        words1 = set(entity1.split())
        words2 = set(entity2.split())
        
        common_words = words1.intersection(words2)
        
        if len(common_words) > 0 and len(common_words) >= len(words1) / 2:
            return True
        
        return False
    
    def calculate_action_verbs_match(self, candidate_text, job_text):
        """
        Analyse la correspondance des verbes d'action entre l'expérience du candidat
        et les responsabilités du poste.
        
        Args:
            candidate_text: Texte d'expérience du candidat
            job_text: Description du poste
            
        Returns:
            float: Score de correspondance des verbes d'action (0.0 - 1.0)
        """
        if not self.nlp or not candidate_text or not job_text:
            return 0.0
        
        try:
            # Analyser les textes avec spaCy
            candidate_doc = self.nlp(candidate_text[:100000])
            job_doc = self.nlp(job_text[:100000])
            
            # Extraire les verbes d'action
            candidate_verbs = set()
            job_verbs = set()
            
            for token in candidate_doc:
                if token.pos_ == "VERB" and not token.is_stop:
                    candidate_verbs.add(token.lemma_.lower())
            
            for token in job_doc:
                if token.pos_ == "VERB" and not token.is_stop:
                    job_verbs.add(token.lemma_.lower())
            
            if not job_verbs:
                return 0.0
            
            # Compter les verbes correspondants
            matched_verbs = candidate_verbs.intersection(job_verbs)
            
            return len(matched_verbs) / len(job_verbs)
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de correspondance des verbes: {e}")
            return 0.0
    
    def calculate_domain_keywords_match(self, candidate_text, job_text):
        """
        Calcule la correspondance des mots-clés spécifiques au domaine.
        
        Args:
            candidate_text: Texte du candidat
            job_text: Texte de l'offre d'emploi
            
        Returns:
            float: Score de correspondance des mots-clés (0.0 - 1.0)
        """
        if not self.nlp or not candidate_text or not job_text:
            return 0.0
        
        try:
            # Extraire les mots-clés du domaine depuis le texte de l'offre
            job_doc = self.nlp(job_text[:100000])
            
            # Identifier les mots-clés potentiels (noms et adjectifs non courants)
            domain_keywords = []
            
            for token in job_doc:
                if (token.pos_ in ["NOUN", "PROPN"] or 
                    (token.pos_ == "ADJ" and token.text.lower() not in ["grand", "petit", "nouveau"])) and \
                   not token.is_stop and token.is_alpha and len(token.text) > 3:
                    domain_keywords.append(token.lemma_.lower())
            
            # Filtrer les mots-clés par fréquence
            if domain_keywords:
                keyword_counts = {}
                for keyword in domain_keywords:
                    if keyword in keyword_counts:
                        keyword_counts[keyword] += 1
                    else:
                        keyword_counts[keyword] = 1
                
                # Garder les mots-clés qui apparaissent plus d'une fois
                filtered_keywords = [k for k, v in keyword_counts.items() if v > 1]
                
                # Si peu de mots-clés sont filtrés, prendre les plus fréquents
                if len(filtered_keywords) < 5:
                    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
                    filtered_keywords = [k for k, v in sorted_keywords[:10]]
                
                # Chercher les mots-clés dans le texte du candidat
                candidate_doc = self.nlp(candidate_text[:100000])
                candidate_lemmas = [token.lemma_.lower() for token in candidate_doc 
                                   if token.is_alpha and not token.is_stop]
                
                matched_keywords = sum(1 for keyword in filtered_keywords if keyword in candidate_lemmas)
                
                return matched_keywords / len(filtered_keywords) if filtered_keywords else 0.0
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de correspondance des mots-clés: {e}")
        
        return 0.0
    
    def calculate_requirements_match(self, candidate_profile, job_profile):
        """
        Calcule la correspondance entre les compétences du candidat
        et les exigences du poste.
        
        Args:
            candidate_profile: Profil du candidat
            job_profile: Profil de l'offre d'emploi
            
        Returns:
            float: Score de correspondance des exigences (0.0 - 1.0)
        """
        if not candidate_profile or not job_profile:
            return 0.0
        
        # Extraire les compétences du candidat
        candidate_skills = []
        skill_fields = ["skills", "competences", "technical_skills", "hard_skills", "soft_skills"]
        
        for field in skill_fields:
            if field in candidate_profile:
                value = candidate_profile[field]
                
                if isinstance(value, list):
                    candidate_skills.extend([s.lower() for s in value if isinstance(s, str)])
                elif isinstance(value, str):
                    candidate_skills.extend([s.strip().lower() for s in value.split(',')])
                elif isinstance(value, dict):
                    candidate_skills.extend([k.lower() for k in value.keys()])
        
        # Extraire les exigences du poste
        job_requirements = []
        req_fields = ["requirements", "qualifications", "prerequisites", "required_skills"]
        
        for field in req_fields:
            if field in job_profile:
                value = job_profile[field]
                
                if isinstance(value, list):
                    job_requirements.extend([r.lower() for r in value if isinstance(r, str)])
                elif isinstance(value, str):
                    # Essayer de diviser par lignes ou par puces
                    if '\n' in value:
                        job_requirements.extend([r.strip().lower() for r in value.split('\n') if r.strip()])
                    else:
                        job_requirements.extend([r.strip().lower() for r in value.split(',') if r.strip()])
        
        if not candidate_skills or not job_requirements:
            return 0.0
        
        # Calculer la correspondance
        matched_requirements = 0
        
        for req in job_requirements:
            for skill in candidate_skills:
                if skill in req or req in skill:
                    matched_requirements += 1
                    break
        
        return matched_requirements / len(job_requirements)
