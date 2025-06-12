#!/usr/bin/env python3
"""
CORRECTION URGENTE - Système de classification des domaines
Le bug : missions extraites mais 0 missions filtrées
"""

import re
from typing import Dict, List, Tuple

class FixedDomainClassifier:
    """
    Version corrigée du système de classification des domaines
    """
    
    def __init__(self):
        # Mots-clés corrigés et étendus par domaine
        self.domain_keywords = {
            'facturation': [
                'facturation', 'facture', 'facturer', 'billing',
                'client', 'clients', 'fournisseur', 'fournisseurs',
                'règlement', 'règlements', 'paiement', 'encaissement',
                'recouvrement', 'relance', 'relances'
            ],
            'comptabilité': [
                'comptable', 'comptabilité', 'accounting',
                'écriture', 'écritures', 'compte', 'comptes',
                'saisie', 'balance', 'grand livre', 'journal',
                'déclaration', 'fiscal', 'fiscale', 'tva'
            ],
            'contrôle': [
                'contrôle', 'contrôler', 'contrôleur', 'control',
                'validation', 'valider', 'vérification', 'vérifier',
                'audit', 'auditer', 'révision', 'analyse',
                'qualité', 'conformité', 'supervision'
            ],
            'gestion': [
                'gestion', 'gérer', 'gestionnaire', 'management',
                'suivi', 'suivre', 'organisation', 'planification',
                'coordination', 'administration', 'administratif',
                'pilotage', 'direction'
            ],
            'reporting': [
                'reporting', 'rapport', 'rapports', 'report',
                'indicateur', 'indicateurs', 'tableau de bord',
                'kpi', 'métrique', 'statistique', 'analyse',
                'performance', 'dashboards', 'synthèse'
            ],
            'commercial': [
                'commercial', 'commerciale', 'vente', 'ventes',
                'business', 'développement', 'prospection',
                'négociation', 'client', 'clientèle', 'marché',
                'chiffre d\'affaires', 'ca', 'revenue'
            ],
            'RH': [
                'rh', 'ressources humaines', 'human resources',
                'recrutement', 'recruter', 'formation', 'paie',
                'personnel', 'collaborateur', 'employé',
                'entretien', 'évaluation', 'carrière'
            ]
        }
        
        # Mots-clés de titres de postes
        self.title_keywords = {
            'facturation': [
                'facturation', 'assistant facturation', 'chargé facturation',
                'responsable facturation'
            ],
            'comptabilité': [
                'comptable', 'assistant comptable', 'responsable comptable',
                'chef comptable', 'comptable général', 'comptable unique'
            ],
            'contrôle': [
                'contrôleur', 'contrôleur de gestion', 'auditeur',
                'responsable contrôle', 'analyste financier'
            ],
            'gestion': [
                'gestionnaire', 'responsable gestion', 'manager',
                'directeur', 'chef de service'
            ],
            'commercial': [
                'commercial', 'ingénieur d\'affaires', 'business developer',
                'chargé d\'affaires', 'responsable commercial'
            ]
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Remplacer les caractères spéciaux
        text = re.sub(r'[àáâãäå]', 'a', text)
        text = re.sub(r'[èéêë]', 'e', text)
        text = re.sub(r'[ìíîï]', 'i', text)
        text = re.sub(r'[òóôõö]', 'o', text)
        text = re.sub(r'[ùúûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        
        # Garder seulement lettres, chiffres et espaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Normaliser les espaces
        text = ' '.join(text.split())
        
        return text
    
    def count_keyword_matches(self, text: str, keywords: List[str]) -> Tuple[int, List[str]]:
        """Compte les occurrences de mots-clés dans le texte"""
        normalized_text = self.normalize_text(text)
        matches = []
        total_score = 0
        
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword)
            
            # Recherche exacte pour mots composés
            if ' ' in normalized_keyword:
                if normalized_keyword in normalized_text:
                    matches.append(keyword)
                    total_score += 2  # Bonus pour expressions complètes
            else:
                # Recherche avec boundaries pour mots simples
                pattern = r'\b' + re.escape(normalized_keyword) + r'\b'
                occurrences = len(re.findall(pattern, normalized_text))
                if occurrences > 0:
                    matches.append(keyword)
                    total_score += occurrences
        
        return total_score, matches
    
    def classify_missions(self, missions: List[str], job_title: str = "") -> Dict:
        """
        Classifie une liste de missions par domaine
        """
        if not missions:
            return {
                'domain': 'unknown',
                'confidence': 0.0,
                'scores': {},
                'matches': {},
                'details': "Aucune mission fournie"
            }
        
        # Concaténer toutes les missions + titre
        full_text = " ".join(missions)
        if job_title:
            full_text = f"{job_title} {full_text}"
        
        domain_scores = {}
        domain_matches = {}
        
        # Calculer scores pour chaque domaine
        for domain, keywords in self.domain_keywords.items():
            score, matches = self.count_keyword_matches(full_text, keywords)
            domain_scores[domain] = score
            domain_matches[domain] = matches
        
        # Bonus pour titres de postes
        for domain, title_keywords in self.title_keywords.items():
            title_score, title_matches = self.count_keyword_matches(job_title, title_keywords)
            if title_score > 0:
                domain_scores[domain] += title_score * 2  # Bonus titre
                domain_matches[domain].extend(title_matches)
        
        # Déterminer domaine principal
        if not any(score > 0 for score in domain_scores.values()):
            return {
                'domain': 'unknown',
                'confidence': 0.0,
                'scores': domain_scores,
                'matches': domain_matches,
                'details': "Aucun mot-clé de domaine détecté"
            }
        
        best_domain = max(domain_scores.items(), key=lambda x: x[1])
        total_score = sum(domain_scores.values())
        confidence = best_domain[1] / total_score if total_score > 0 else 0.0
        
        return {
            'domain': best_domain[0],
            'confidence': confidence,
            'scores': domain_scores,
            'matches': domain_matches,
            'details': f"Détecté avec {best_domain[1]} points"
        }
    
    def filter_missions_by_domain(self, missions: List[str], domain: str) -> List[str]:
        """
        Filtre les missions pertinentes pour un domaine donné
        """
        if domain == 'unknown' or not missions:
            return []
        
        domain_keywords = self.domain_keywords.get(domain, [])
        filtered_missions = []
        
        for mission in missions:
            score, matches = self.count_keyword_matches(mission, domain_keywords)
            if score > 0:
                # Ajouter le domaine à la mission pour le matching
                filtered_mission = f"{mission} {domain}"
                filtered_missions.append(filtered_mission)
        
        return filtered_missions

def test_fixed_classifier():
    """
    Test de la version corrigée avec les données de Vincent Lecocq
    """
    print("🧪 TEST DU CLASSIFICATEUR CORRIGÉ")
    print("=" * 50)
    
    classifier = FixedDomainClassifier()
    
    # Données Vincent Lecocq
    cv_missions = [
        "Facturation clients et suivi des règlements",
        "Saisie des écritures comptables dans Oracle",
        "Contrôle et validation des comptes", 
        "Gestion des relances clients",
        "Reporting mensuel et indicateurs de performance"
    ]
    
    cv_title = "Contrôleur de gestion"
    
    job_missions = [
        "Facturation clients et fournisseurs",
        "Saisie et contrôle des écritures comptables",
        "Suivi des règlements et relances clients",
        "Gestion administrative et reporting",
        "Mise à jour des bases de données Oracle/SAP",
        "Contrôle qualité des données"
    ]
    
    job_title = "Assistant Facturation"
    
    print("🔍 CLASSIFICATION CV:")
    cv_result = classifier.classify_missions(cv_missions, cv_title)
    print(f"   Domaine: {cv_result['domain']}")
    print(f"   Confiance: {cv_result['confidence']:.2f}")
    print(f"   Scores: {cv_result['scores']}")
    print(f"   Détails: {cv_result['details']}")
    
    print("\n🔍 CLASSIFICATION JOB:")
    job_result = classifier.classify_missions(job_missions, job_title)
    print(f"   Domaine: {job_result['domain']}")
    print(f"   Confiance: {job_result['confidence']:.2f}")
    print(f"   Scores: {job_result['scores']}")
    print(f"   Détails: {job_result['details']}")
    
    print("\n🎯 FILTRAGE DES MISSIONS:")
    cv_filtered = classifier.filter_missions_by_domain(cv_missions, cv_result['domain'])
    job_filtered = classifier.filter_missions_by_domain(job_missions, job_result['domain'])
    
    print(f"   CV missions filtrées: {len(cv_filtered)}")
    for mission in cv_filtered:
        print(f"      - {mission}")
    
    print(f"   Job missions filtrées: {len(job_filtered)}")
    for mission in job_filtered:
        print(f"      - {mission}")
    
    print(f"\n🎉 RÉSULTAT:")
    if cv_result['domain'] != 'unknown' and job_result['domain'] != 'unknown':
        print(f"   ✅ Classification réussie !")
        print(f"   ✅ CV: {cv_result['domain']} (confiance: {cv_result['confidence']:.2f})")
        print(f"   ✅ Job: {job_result['domain']} (confiance: {job_result['confidence']:.2f})")
        print(f"   ✅ Missions filtrées: {len(cv_filtered) + len(job_filtered)}")
    else:
        print(f"   ❌ Classification échouée")

if __name__ == "__main__":
    test_fixed_classifier()
    
    print(f"\n🔧 ACTIONS POUR INTÉGRER LA CORRECTION:")
    print("1. Remplacer le système de classification dans l'Enhanced API")
    print("2. Utiliser des mots-clés plus permissifs")
    print("3. Normaliser correctement les textes")
    print("4. Ajouter le bonus pour les titres de postes")
    print("5. Relancer les tests avec le système corrigé")
