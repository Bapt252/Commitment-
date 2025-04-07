#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation complet du système de parsing et matching
Ce script montre comment utiliser toutes les fonctionnalités du système amélioré
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

# Import des modules nécessaires
from app.nlp.enhanced_parsing_system import parse_document, save_parsing_feedback, export_training_dataset
from app.nlp.matching_engine import match_cv_with_job


def run_example():
    """
    Exécute un exemple complet d'utilisation du système
    """
    print("\n" + "=" * 80)
    print("EXEMPLE D'UTILISATION DU SYSTÈME DE PARSING ET MATCHING COMMITMENT")
    print("=" * 80)
    
    # Créer un répertoire pour les exemples
    examples_dir = "examples"
    Path(examples_dir).mkdir(exist_ok=True)
    
    # 1. Générer un exemple de CV si aucun n'est fourni
    cv_path = os.path.join(examples_dir, "exemple_cv.txt")
    if not os.path.exists(cv_path):
        print("\nCréation d'un exemple de CV...")
        with open(cv_path, 'w', encoding='utf-8') as f:
            f.write(generate_sample_cv())
        print(f"CV d'exemple créé dans {cv_path}")
    
    # 2. Générer un exemple d'offre d'emploi si aucune n'est fournie
    job_path = os.path.join(examples_dir, "exemple_offre.txt")
    if not os.path.exists(job_path):
        print("\nCréation d'un exemple d'offre d'emploi...")
        with open(job_path, 'w', encoding='utf-8') as f:
            f.write(generate_sample_job())
        print(f"Offre d'emploi d'exemple créée dans {job_path}")
    
    # 3. Parsing du CV
    print("\n" + "-" * 50)
    print("ÉTAPE 1: PARSING DU CV")
    print("-" * 50)
    print(f"Analyse du CV: {cv_path}")
    
    cv_result = parse_document(file_path=cv_path)
    
    # Afficher un résumé des résultats
    print("\nRésultat du parsing:")
    print(f"- Type détecté: {cv_result.get('doc_type', 'Inconnu')}")
    print(f"- Format: {cv_result.get('file_format', 'Inconnu')}")
    
    extracted_data = cv_result.get("extracted_data", {})
    for key, value in extracted_data.items():
        if key == 'preferences':
            continue  # Traiter les préférences séparément
        if isinstance(value, list):
            print(f"- {key}: {', '.join(value[:5])}{'...' if len(value) > 5 else ''}")
        else:
            print(f"- {key}: {value}")
    
    # Afficher les préférences si présentes
    if 'preferences' in extracted_data:
        print("\nPréférences détectées:")
        
        env_prefs = extracted_data['preferences'].get('environment', {})
        if env_prefs:
            print("Environnement de travail:")
            for pref, score in env_prefs.items():
                if score > 0.3:  # N'afficher que les préférences significatives
                    print(f"  - {pref}: {score*100:.1f}%")
        
        work_prefs = extracted_data['preferences'].get('work_style', {})
        if work_prefs:
            print("Style de travail:")
            for pref, score in work_prefs.items():
                if score > 0.3:  # N'afficher que les préférences significatives
                    print(f"  - {pref}: {score*100:.1f}%")
    
    # Afficher les scores de confiance
    confidence_scores = cv_result.get("confidence_scores", {})
    if confidence_scores:
        print("\nScores de confiance:")
        for key, score in confidence_scores.items():
            print(f"- {key}: {score*100:.1f}%")
    
    # 4. Parsing de l'offre d'emploi
    print("\n" + "-" * 50)
    print("ÉTAPE 2: PARSING DE L'OFFRE D'EMPLOI")
    print("-" * 50)
    print(f"Analyse de l'offre: {job_path}")
    
    job_result = parse_document(file_path=job_path, doc_type="job_posting")
    
    # Afficher un résumé des résultats
    print("\nRésultat du parsing:")
    print(f"- Type détecté: {job_result.get('doc_type', 'Inconnu')}")
    print(f"- Format: {job_result.get('file_format', 'Inconnu')}")
    
    extracted_data = job_result.get("extracted_data", {})
    for key, value in extracted_data.items():
        if isinstance(value, list):
            print(f"- {key}: {', '.join(value[:5])}{'...' if len(value) > 5 else ''}")
        else:
            print(f"- {key}: {value}")
    
    # 5. Exemple de correction et feedback
    print("\n" + "-" * 50)
    print("ÉTAPE 3: ENREGISTREMENT D'UN FEEDBACK")
    print("-" * 50)
    print("Simulation d'une correction par un utilisateur...")
    
    # Créer une version corrigée du CV
    corrected_cv = cv_result.copy()
    
    # Ajouter une compétence manquante
    if 'competences' in corrected_cv.get('extracted_data', {}):
        # Vérifier si React est déjà présent
        if 'React' not in corrected_cv['extracted_data']['competences']:
            corrected_cv['extracted_data']['competences'].append('React')
            print("Ajout de la compétence 'React' au CV")
    else:
        corrected_cv['extracted_data']['competences'] = ['React']
        print("Création de la liste de compétences avec 'React'")
    
    # Enregistrer le feedback
    feedback_id = save_parsing_feedback(
        original_result=cv_result,
        corrected_result=corrected_cv,
        user_id="exemple_utilisateur"
    )
    
    print(f"\nFeedback enregistré avec l'ID: {feedback_id}")
    
    # 6. Matching entre CV et offre
    print("\n" + "-" * 50)
    print("ÉTAPE 4: MATCHING CV/OFFRE")
    print("-" * 50)
    print("Calcul du matching entre le CV et l'offre d'emploi...")
    
    match_result = match_cv_with_job(cv_result, job_result)
    
    # Afficher les résultats du matching
    overall_score = match_result.get("score", 0)
    print(f"\nScore global: {overall_score*100:.1f}%")
    
    # Afficher les compétences correspondantes
    matching_skills = match_result.get("matching_skills", [])
    print(f"\nCompétences correspondantes ({len(matching_skills)}):")
    for skill in matching_skills:
        print(f"- {skill}")
    
    # Afficher les compétences manquantes
    missing_skills = match_result.get("missing_skills", [])
    print(f"\nCompétences manquantes ({len(missing_skills)}):")
    for skill in missing_skills:
        print(f"- {skill}")
    
    # Afficher les scores détaillés si disponibles
    detail_scores = match_result.get("detail_scores", {})
    if detail_scores:
        print("\nScores détaillés:")
        for category, score in detail_scores.items():
            print(f"- {category}: {score*100:.1f}%")
    
    # 7. Export des données d'entraînement
    print("\n" + "-" * 50)
    print("ÉTAPE 5: EXPORT DES DONNÉES D'ENTRAÎNEMENT")
    print("-" * 50)
    print("Export des données d'entraînement pour le fine-tuning...")
    
    # Créer un répertoire pour l'export
    export_dir = os.path.join(examples_dir, "training_data")
    
    # Exporter les données
    success = export_training_dataset(export_dir)
    
    if success:
        print(f"\nDonnées d'entraînement exportées dans {export_dir}")
    else:
        print("\nAucune donnée d'entraînement à exporter.")
    
    # 8. Conclusion
    print("\n" + "=" * 80)
    print("RÉCAPITULATIF ET PROCHAINES ÉTAPES")
    print("=" * 80)
    print("""
Félicitations ! Vous venez de voir un exemple complet d'utilisation du système 
amélioré de parsing et matching de Commitment.

Vous avez testé :
1. La détection automatique de format et type de document
2. L'extraction d'informations avec BERT
3. La déduction des préférences d'environnement et de mode de travail
4. L'enregistrement et l'utilisation des feedbacks utilisateurs
5. Le matching entre CV et offres d'emploi
6. L'export des données d'entraînement pour le fine-tuning

Pour aller plus loin, vous pouvez :
- Traiter des documents réels avec le script 'test_batch_parsing.py'
- Générer des questionnaires intelligents avec 'generate_smart_questionnaire.py'
- Créer un tableau de bord de matching avec 'create_matching_dashboard.py'
- Intégrer ces fonctionnalités dans votre API FastAPI existante
""")


def generate_sample_cv():
    """
    Génère un exemple de CV pour les tests
    
    Returns:
        str: Texte du CV
    """
    return """
CURRICULUM VITAE

Marie DUPONT
Développeuse Full Stack
marie.dupont@email.com | 06 12 34 56 78
17 rue des Lilas, 75011 Paris

PROFIL
-------
Développeuse full stack passionnée avec 5 ans d'expérience dans la conception et le développement d'applications web et mobiles. Expérience significative en architecture logicielle et méthodologies agiles. Je recherche un environnement de travail stimulant qui me permettra de collaborer sur des projets innovants en télétravail.  

COMPÉTENCES
-----------
Langages de programmation: JavaScript, TypeScript, Python, Java, PHP
Frameworks & bibliothèques: Angular, Node.js, Express, Django, Spring Boot
Bases de données: PostgreSQL, MongoDB, MySQL, Redis
Outils & méthodologies: Git, Docker, AWS, Agile/Scrum, CI/CD
Langues: Français (natif), Anglais (courant), Espagnol (intermédiaire)

EXPÉRIENCE PROFESSIONNELLE
-------------------------
DÉVELOPPEUSE FULL STACK | TECH SOLUTIONS | 2020 - PRÉSENT
- Développement d'applications web complexes utilisant Angular et Node.js
- Conception et implémentation d'API RESTful avec Express et MongoDB
- Participation aux cérémonies agiles et revues de code
- Mise en place de pipelines CI/CD avec Jenkins et Docker
- Travail en autonomie en télétravail 3 jours par semaine

DÉVELOPPEUSE BACKEND | STARTAPP | 2018 - 2020
- Développement backend avec Django et PostgreSQL
- Maintenance et amélioration de microservices existants
- Collaboration avec une équipe internationale
- Travail dans un environnement de startup dynamique

DÉVELOPPEUSE JUNIOR | AGENCE WEB DIGITAL | 2017 - 2018
- Développement de sites web avec PHP/Laravel
- Intégration frontend (HTML, CSS, JavaScript)
- Participation aux réunions client

FORMATION
--------
Master en Développement Logiciel | UNIVERSITÉ DE PARIS | 2015 - 2017
Licence en Informatique | UNIVERSITÉ DE LYON | 2012 - 2015

PROJETS PERSONNELS
----------------
PLATEFORME DE GESTION DE PROJETS OPEN SOURCE
- Développement d'une alternative à Trello avec React et Firebase
- Plus de 500 utilisateurs actifs
- Disponible sur GitHub avec plus de 200 étoiles

APPLICATION MOBILE DE SUIVI FITNESS
- Application React Native connectée à une API Node.js
- Utilisation de Redux pour la gestion d'état
- Intégration de graphiques et visualisations de données

CENTRES D'INTÉRÊT
---------------
- Contribution à des projets open source
- Participation à des hackathons
- Randonnée et photographie
- Yoga et méditation
"""


def generate_sample_job():
    """
    Génère un exemple d'offre d'emploi pour les tests
    
    Returns:
        str: Texte de l'offre
    """
    return """
OFFRE D'EMPLOI

DÉVELOPPEUR FULL STACK (H/F)

INNOVTECH - Paris, France

À PROPOS DE NOUS
---------------
InnovTech est une scale-up spécialisée dans les solutions SaaS pour la gestion de la relation client. Fondée en 2015, notre entreprise compte aujourd'hui plus de 50 collaborateurs et continue sa croissance rapide sur le marché européen.

DESCRIPTION DU POSTE
------------------
Nous recherchons un(e) Développeur(se) Full Stack pour rejoindre notre équipe technique en pleine expansion. Vous serez responsable de la conception, du développement et de la maintenance de nos applications web, en travaillant en étroite collaboration avec nos équipes produit et design.

RESPONSABILITÉS
--------------
- Développer et maintenir des applications web performantes et scalables
- Concevoir et implémenter des API RESTful
- Participer aux cérémonies agiles (planification, rétrospectives, etc.)
- Collaborer avec les équipes produit et design pour définir les fonctionnalités
- Réaliser des revues de code et partager vos connaissances
- Contribuer à l'amélioration continue de nos processus de développement

PROFIL RECHERCHÉ
--------------
- Minimum 3 ans d'expérience en développement full stack
- Maîtrise de JavaScript/TypeScript, HTML, CSS
- Expérience avec Angular, React ou Vue.js
- Expérience avec Node.js, Express ou frameworks similaires
- Connaissance de PostgreSQL ou autres SGBD relationnels
- Familiarité avec les méthodologies agiles
- Expérience avec Git et les bonnes pratiques de CI/CD
- Bon niveau d'anglais (environnement de travail international)

COMPÉTENCES TECHNIQUES REQUISES
-----------------------------
- JavaScript/TypeScript
- Angular
- Node.js
- PostgreSQL
- Git
- Docker
- AWS ou autre cloud provider

COMPÉTENCES APPRÉCIÉES
---------------------
- Python
- MongoDB
- Redis
- GraphQL
- Kubernetes

CE QUE NOUS OFFRONS
-----------------
- CDI à temps plein
- Rémunération attractive selon expérience (50-70K€)
- Intéressement et participation
- Travail hybride (2-3 jours de télétravail par semaine)
- Mutuelle d'entreprise
- Tickets restaurant
- Budget formation
- Événements d'entreprise réguliers

PROCESSUS DE RECRUTEMENT
----------------------
1. Entretien téléphonique avec un recruteur (30 min)
2. Test technique à réaliser à la maison
3. Entretien technique avec l'équipe (1h)
4. Entretien final avec le CTO (45 min)

COMMENT POSTULER
--------------
Envoyez votre CV et lettre de motivation à careers@innovtech.fr avec pour objet "Candidature Développeur Full Stack"
"""


# Point d'entrée si le script est exécuté directement
if __name__ == "__main__":
    run_example()