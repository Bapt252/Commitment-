#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Générateur de données de test pour Nexten SmartMatch."""

import random
import json
from datetime import datetime
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestDataGenerator")

def generate_test_candidates(count=50):
    """
    Génère un ensemble de données de candidats de test.
    
    Args:
        count (int): Nombre de candidats à générer
        
    Returns:
        list: Liste des candidats générés
    """
    skills = [
        "Python", "JavaScript", "React", "Node.js", "Java", "C++", "AWS", "Docker", 
        "Kubernetes", "Machine Learning", "Data Analysis", "SQL", "NoSQL", "Django",
        "Flask", "Spring Boot", "Angular", "Vue.js", "TypeScript", "PHP", "Laravel",
        "Ruby", "Ruby on Rails", "Go", "Rust", "Swift", "Kotlin", "Android", "iOS",
        "DevOps", "CI/CD", "Git", "Agile", "Scrum", "Kanban", "TDD", "BDD",
        "REST API", "GraphQL", "Microservices", "Serverless", "Cloud Computing"
    ]
    
    locations = [
        {"address": "75001 Paris, France", "lat": 48.86, "lng": 2.34},
        {"address": "92100 Boulogne-Billancourt, France", "lat": 48.83, "lng": 2.24},
        {"address": "93200 Saint-Denis, France", "lat": 48.93, "lng": 2.35},
        {"address": "94000 Créteil, France", "lat": 48.79, "lng": 2.45},
        {"address": "78000 Versailles, France", "lat": 48.80, "lng": 2.13},
        {"address": "91000 Évry, France", "lat": 48.63, "lng": 2.45},
        {"address": "95000 Cergy, France", "lat": 49.04, "lng": 2.06},
        {"address": "77000 Melun, France", "lat": 48.54, "lng": 2.66},
        {"address": "59000 Lille, France", "lat": 50.63, "lng": 3.06},
        {"address": "69000 Lyon, France", "lat": 45.76, "lng": 4.83}
    ]
    
    remote_preferences = ["full", "hybrid", "office"]
    company_size_preferences = ["startup", "midsize", "enterprise"]
    
    candidates = []
    for i in range(count):
        candidate_skills = random.sample(skills, random.randint(3, 8))
        location = random.choice(locations)
        
        candidate = {
            "id": f"cand_{i}",
            "name": f"Candidat {i}",
            "skills": candidate_skills,
            "experience": random.randint(0, 15),
            "location": location["address"],
            "location_coordinates": {"lat": location["lat"], "lng": location["lng"]},
            "remote_preference": random.choice(remote_preferences),
            "max_travel_time": random.randint(15, 90),  # minutes
            "salary_expectation": random.randint(35000, 120000),
            "preferred_company_size": random.choice(company_size_preferences),
            "created_at": datetime.now().isoformat()
        }
        candidates.append(candidate)
    
    logger.info(f"Génération de {count} candidats de test terminée")
    return candidates

def generate_test_companies(count=20):
    """
    Génère un ensemble de données d'entreprises de test.
    
    Args:
        count (int): Nombre d'entreprises à générer
        
    Returns:
        list: Liste des entreprises générées
    """
    required_skills_sets = [
        ["Python", "Django", "PostgreSQL", "Git"],
        ["JavaScript", "React", "Node.js", "MongoDB"],
        ["Java", "Spring Boot", "Hibernate", "Oracle"],
        ["PHP", "Laravel", "MySQL", "Docker"],
        ["Python", "Flask", "AWS", "Kubernetes"],
        ["JavaScript", "Vue.js", "Express", "NoSQL"],
        ["C++", "Qt", "CMake", "Boost"],
        ["Ruby", "Ruby on Rails", "PostgreSQL", "Redis"],
        ["Go", "RESTful API", "Microservices", "Docker"],
        ["Python", "Machine Learning", "TensorFlow", "Pandas"],
        ["Java", "Android", "Kotlin", "SQLite"],
        ["Swift", "iOS", "Objective-C", "Core Data"],
        ["TypeScript", "Angular", "RxJS", "NgRx"],
        ["React Native", "JavaScript", "Redux", "Firebase"],
        ["DevOps", "CI/CD", "Jenkins", "Terraform"]
    ]
    
    locations = [
        {"address": "75008 Paris, France", "lat": 48.87, "lng": 2.32},
        {"address": "92300 Levallois-Perret, France", "lat": 48.89, "lng": 2.28},
        {"address": "75016 Paris, France", "lat": 48.86, "lng": 2.27},
        {"address": "92130 Issy-les-Moulineaux, France", "lat": 48.82, "lng": 2.26},
        {"address": "75011 Paris, France", "lat": 48.86, "lng": 2.38},
        {"address": "69002 Lyon, France", "lat": 45.75, "lng": 4.83},
        {"address": "59000 Lille, France", "lat": 50.63, "lng": 3.06},
        {"address": "33000 Bordeaux, France", "lat": 44.84, "lng": -0.58},
        {"address": "44000 Nantes, France", "lat": 47.22, "lng": -1.55},
        {"address": "13001 Marseille, France", "lat": 43.30, "lng": 5.37}
    ]
    
    remote_policies = ["full", "hybrid", "office_only"]
    company_sizes = ["startup", "midsize", "enterprise"]
    
    companies = []
    for i in range(count):
        required_skills = random.choice(required_skills_sets)
        location = random.choice(locations)
        min_salary = random.randint(30000, 80000)
        max_salary = min_salary + random.randint(10000, 40000)
        
        company = {
            "id": f"comp_{i}",
            "name": f"Entreprise {i}",
            "required_skills": required_skills,
            "location": location["address"],
            "location_coordinates": {"lat": location["lat"], "lng": location["lng"]},
            "remote_policy": random.choice(remote_policies),
            "required_experience": random.randint(0, 10),
            "salary_range": {"min": min_salary, "max": max_salary},
            "company_size": random.choice(company_sizes),
            "created_at": datetime.now().isoformat()
        }
        companies.append(company)
    
    logger.info(f"Génération de {count} entreprises de test terminée")
    return companies

def save_test_data(candidates, companies, output_dir="test_data"):
    """
    Sauvegarde les données de test dans des fichiers JSON.
    
    Args:
        candidates (list): Liste des candidats
        companies (list): Liste des entreprises
        output_dir (str): Répertoire de sortie
    """
    # Créer le répertoire s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder les candidats
    with open(os.path.join(output_dir, "candidates.json"), "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    
    # Sauvegarder les entreprises
    with open(os.path.join(output_dir, "companies.json"), "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Données de test sauvegardées dans le répertoire '{output_dir}'")

def generate_and_save_test_data(candidates_count=50, companies_count=20, output_dir="test_data"):
    """
    Génère et sauvegarde des données de test pour le système de matching.
    
    Args:
        candidates_count (int): Nombre de candidats à générer
        companies_count (int): Nombre d'entreprises à générer
        output_dir (str): Répertoire de sortie
    """
    candidates = generate_test_candidates(candidates_count)
    companies = generate_test_companies(companies_count)
    save_test_data(candidates, companies, output_dir)

if __name__ == "__main__":
    generate_and_save_test_data()
