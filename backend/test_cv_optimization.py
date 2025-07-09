#!/usr/bin/env python3
"""
🧪 Test CV Parsing Optimization
================================

Script de test pour valider l'amélioration du CV parsing avec l'optimiseur.
Objectif: Passer de 54.5% à >90% de réussite.

Author: Nextvision Team
Version: 1.0 - CV Optimization Testing
"""

import json
import time
import os
from pathlib import Path
from typing import List, Dict, Any
import glob

# Import de l'optimiseur
from cv_parser_optimizer import CVParserOptimizer, CVExtractionResult, DataQuality

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class CVOptimizationTester:
    """Testeur pour l'optimisation du CV parsing"""
    
    def __init__(self):
        self.optimizer = CVParserOptimizer()
        self.results = []
        self.test_dir = Path.home() / "Desktop" / "CV TEST"
        
    def find_test_cvs(self, limit: int = 10) -> List[Path]:
        """Trouve les CVs de test"""
        
        if not self.test_dir.exists():
            print(f"{Colors.RED}❌ Répertoire CV TEST introuvable: {self.test_dir}{Colors.END}")
            return []
        
        # Chercher les fichiers PDF
        cv_files = list(self.test_dir.glob("*.pdf"))[:limit]
        
        print(f"{Colors.BLUE}📁 Répertoire CV: {self.test_dir}{Colors.END}")
        print(f"{Colors.BLUE}📄 CVs trouvés: {len(cv_files)}{Colors.END}")
        
        return cv_files
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extrait le texte d'un PDF (simulation)"""
        
        # Simulation d'extraction de texte
        # En réalité, tu utiliserais PyPDF2, pdfplumber, ou ton extracteur existant
        
        simulated_cvs = {
            "Mohamed": """
            Mohamed OUADHANE
            Développeur Full-Stack
            mohamed.ouadhane@email.com
            +33 6 12 34 56 78
            Paris, France
            
            EXPÉRIENCE PROFESSIONNELLE:
            2022-2024: Développeur Full-Stack Senior - TechStartup (2 ans)
            2020-2022: Développeur Backend - DigitalCorp (2 ans)
            2018-2020: Développeur Junior - WebAgency (2 ans)
            
            COMPÉTENCES TECHNIQUES:
            - JavaScript, TypeScript, Node.js
            - React, Vue.js, Angular
            - Python, Django, FastAPI
            - PostgreSQL, MongoDB, Redis
            - Docker, Kubernetes, AWS
            - Git, CI/CD, Jest, Cypress
            
            FORMATION:
            Master Informatique - Université Paris-Saclay (2018)
            Licence Informatique - Université Paris-Saclay (2016)
            """,
            
            "Teddy": """
            AGBASSE Teddy
            Data Scientist & Machine Learning Engineer
            teddy.agbasse@gmail.com
            06 98 76 54 32
            Lyon, France
            
            EXPÉRIENCE:
            2021-2024: Senior Data Scientist - AI Company (3 ans)
            2019-2021: Data Analyst - Analytics Firm (2 ans)
            
            COMPÉTENCES:
            - Python, R, SQL
            - TensorFlow, PyTorch, Scikit-learn
            - Pandas, NumPy, Matplotlib
            - Apache Spark, Hadoop
            - AWS, GCP, Azure
            - MLOps, Docker, Kubernetes
            
            FORMATION:
            Master Data Science - École Centrale Lyon (2019)
            """,
            
            "Charlotte": """
            DARMON Charlotte
            Chef de Projet Digital
            charlotte.darmon@email.com
            01 23 45 67 89
            Marseille, France
            
            EXPÉRIENCE:
            2020-2024: Chef de Projet Senior - Digital Agency (4 ans)
            2017-2020: Chef de Projet Junior - WebCorp (3 ans)
            
            COMPÉTENCES:
            - Gestion de projet Agile/Scrum
            - Product Management
            - UX/UI Design collaboration
            - Analytics (Google Analytics, Mixpanel)
            - Outils: Jira, Notion, Figma
            - Communication client
            
            FORMATION:
            Master Management Digital - ESSEC (2017)
            """,
            
            "Default": """
            Jean MARTIN
            Consultant IT
            jean.martin@email.com
            06 11 22 33 44
            
            EXPÉRIENCE:
            2019-2024: Consultant Senior - IT Consulting (5 ans)
            
            COMPÉTENCES:
            - Java, Spring, Hibernate
            - Oracle, MySQL
            - Jenkins, Maven
            
            FORMATION:
            Ingénieur Informatique - EPITA (2019)
            """
        }
        
        # Détecter le type de CV basé sur le nom du fichier
        filename = pdf_path.stem.lower()
        
        if "mohamed" in filename:
            return simulated_cvs["Mohamed"]
        elif "teddy" in filename or "agbasse" in filename:
            return simulated_cvs["Teddy"]
        elif "charlotte" in filename or "darmon" in filename:
            return simulated_cvs["Charlotte"]
        else:
            return simulated_cvs["Default"]
    
    def simulate_openai_call(self, prompt: str) -> str:
        """Simule un appel à OpenAI (à remplacer par le vrai appel)"""
        
        # Simulation de réponse OpenAI basée sur le prompt
        # En réalité, tu remplacerais par ton appel OpenAI existant
        
        if "Mohamed OUADHANE" in prompt:
            return json.dumps({
                "nom": "OUADHANE",
                "prenom": "Mohamed",
                "email": "mohamed.ouadhane@email.com",
                "telephone": "+33 6 12 34 56 78",
                "adresse": "Paris, France",
                "annees_experience": 6,
                "poste_actuel": "Développeur Full-Stack Senior",
                "entreprise_actuelle": "TechStartup",
                "postes_precedents": ["Développeur Backend", "Développeur Junior"],
                "entreprises_precedentes": ["DigitalCorp", "WebAgency"],
                "competences_techniques": ["JavaScript", "TypeScript", "Node.js", "React", "Vue.js", "Python", "Django", "FastAPI", "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS"],
                "competences_transversales": ["Gestion de projet", "Travail en équipe", "Communication"],
                "technologies": ["React", "Vue.js", "Node.js", "Python", "Docker", "AWS"],
                "certifications": [],
                "niveau_formation": "Master",
                "domaine_formation": "Informatique",
                "etablissement": "Université Paris-Saclay",
                "diplomes": ["Master Informatique", "Licence Informatique"],
                "langues": ["Français", "Anglais"],
                "objectif_professionnel": "Développement full-stack avec technologies modernes",
                "resume_profil": "Développeur full-stack expérimenté avec 6 ans d'expérience",
                "secteurs_experience": ["Technologie", "Startup", "Web"]
            })
        
        elif "AGBASSE Teddy" in prompt:
            return json.dumps({
                "nom": "AGBASSE",
                "prenom": "Teddy",
                "email": "teddy.agbasse@gmail.com",
                "telephone": "06 98 76 54 32",
                "adresse": "Lyon, France",
                "annees_experience": 5,
                "poste_actuel": "Senior Data Scientist",
                "entreprise_actuelle": "AI Company",
                "postes_precedents": ["Data Analyst"],
                "entreprises_precedentes": ["Analytics Firm"],
                "competences_techniques": ["Python", "R", "SQL", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Apache Spark", "AWS", "GCP", "Azure"],
                "competences_transversales": ["Analyse", "Présentation", "Recherche"],
                "technologies": ["Python", "TensorFlow", "AWS", "Docker"],
                "certifications": [],
                "niveau_formation": "Master",
                "domaine_formation": "Data Science",
                "etablissement": "École Centrale Lyon",
                "diplomes": ["Master Data Science"],
                "langues": ["Français", "Anglais"],
                "objectif_professionnel": "Machine Learning et IA",
                "resume_profil": "Data Scientist expérimenté en ML et IA",
                "secteurs_experience": ["IA", "Analytics", "Tech"]
            })
        
        else:
            # Réponse par défaut moins complète (pour tester les cas d'échec)
            return json.dumps({
                "nom": "MARTIN",
                "prenom": "Jean",
                "email": "jean.martin@email.com",
                "telephone": "06 11 22 33 44",
                "adresse": "N/A",
                "annees_experience": 5,
                "poste_actuel": "Consultant Senior",
                "entreprise_actuelle": "IT Consulting",
                "postes_precedents": [],
                "entreprises_precedentes": [],
                "competences_techniques": ["Java", "Spring", "Oracle"],
                "competences_transversales": [],
                "technologies": ["Java", "Oracle"],
                "certifications": [],
                "niveau_formation": "Ingénieur",
                "domaine_formation": "Informatique",
                "etablissement": "EPITA",
                "diplomes": ["Ingénieur Informatique"],
                "langues": [],
                "objectif_professionnel": "N/A",
                "resume_profil": "N/A",
                "secteurs_experience": ["IT", "Conseil"]
            })
    
    def test_cv_with_optimizer(self, cv_path: Path) -> Dict[str, Any]:
        """Teste un CV avec l'optimiseur"""
        
        start_time = time.time()
        
        try:
            # 1. Extraire le texte
            cv_text = self.extract_text_from_pdf(cv_path)
            
            # 2. Générer prompt optimisé
            optimized_prompt = self.optimizer.get_optimized_prompt(cv_text)
            
            # 3. Appel simulé à OpenAI
            raw_response = self.simulate_openai_call(optimized_prompt)
            
            # 4. Parser la réponse
            raw_result = json.loads(raw_response)
            
            # 5. Améliorer l'extraction
            enhanced_result = self.optimizer.enhance_extraction(raw_result)
            
            processing_time = time.time() - start_time
            
            return {
                "filename": cv_path.name,
                "success": True,
                "processing_time": processing_time,
                "quality_score": enhanced_result.quality_score,
                "quality_level": enhanced_result.quality_level.value,
                "missing_fields": enhanced_result.missing_fields,
                "confidence_score": enhanced_result.confidence_score,
                "result": enhanced_result
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "filename": cv_path.name,
                "success": False,
                "processing_time": processing_time,
                "error": str(e),
                "quality_score": 0.0,
                "quality_level": "poor"
            }
    
    def run_optimization_test(self, max_cvs: int = 10):
        """Lance le test d'optimisation"""
        
        print(f"{Colors.BOLD}{Colors.BLUE}🧪 === TEST CV PARSING OPTIMIZATION ==={Colors.END}")
        print(f"Objectif: >90% de qualité parsing")
        print()
        
        # Trouver les CVs de test
        cv_files = self.find_test_cvs(max_cvs)
        
        if not cv_files:
            print(f"{Colors.RED}❌ Aucun CV trouvé pour les tests{Colors.END}")
            return
        
        print(f"{Colors.BLUE}🔄 Test de {len(cv_files)} CVs avec optimiseur...{Colors.END}")
        
        # Tester chaque CV
        total_start = time.time()
        
        for i, cv_path in enumerate(cv_files, 1):
            print(f"   {i}/{len(cv_files)} - {cv_path.name[:50]}...", end=" ")
            
            result = self.test_cv_with_optimizer(cv_path)
            self.results.append(result)
            
            if result["success"]:
                quality = result["quality_score"]
                if quality >= 90:
                    status = f"{Colors.GREEN}✅ {quality:.1f}%{Colors.END}"
                elif quality >= 70:
                    status = f"{Colors.YELLOW}⚠️ {quality:.1f}%{Colors.END}"
                else:
                    status = f"{Colors.RED}❌ {quality:.1f}%{Colors.END}"
                
                print(f"{status} ({result['processing_time']:.3f}s)")
            else:
                print(f"{Colors.RED}❌ ERREUR{Colors.END}")
        
        total_time = time.time() - total_start
        
        # Analyser les résultats
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time: float):
        """Analyse les résultats des tests"""
        
        print(f"\n{Colors.BOLD}📊 === ANALYSE DES RÉSULTATS ==={Colors.END}")
        
        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]
        
        if not successful_tests:
            print(f"{Colors.RED}❌ Aucun test réussi{Colors.END}")
            return
        
        # Calculs de performance
        qualities = [r["quality_score"] for r in successful_tests]
        avg_quality = sum(qualities) / len(qualities)
        
        excellent_count = sum(1 for q in qualities if q >= 95)
        good_count = sum(1 for q in qualities if q >= 80)
        acceptable_count = sum(1 for q in qualities if q >= 60)
        poor_count = sum(1 for q in qualities if q < 60)
        
        success_rate = (good_count / len(self.results)) * 100
        
        print(f"⏱️ Temps total: {total_time:.2f}s")
        print(f"📄 CVs testés: {len(self.results)}")
        print(f"✅ Tests réussis: {len(successful_tests)}")
        print(f"❌ Tests échoués: {len(failed_tests)}")
        print()
        
        print(f"📊 Qualité moyenne: {avg_quality:.1f}%")
        print(f"🌟 Excellente (>95%): {excellent_count}")
        print(f"✅ Bonne (80-95%): {good_count}")
        print(f"⚠️ Acceptable (60-80%): {acceptable_count}")
        print(f"❌ Faible (<60%): {poor_count}")
        print()
        
        print(f"🎯 Taux de succès (>80%): {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"{Colors.GREEN}🎉 OBJECTIF >90% ATTEINT! ({success_rate:.1f}%){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Objectif >90% non atteint ({success_rate:.1f}%){Colors.END}")
        
        # Identifier les problèmes
        if failed_tests or poor_count > 0:
            print(f"\n{Colors.BOLD}🔍 === ANALYSE DES PROBLÈMES ==={Colors.END}")
            
            for result in self.results:
                if not result["success"] or result["quality_score"] < 60:
                    print(f"❌ {result['filename']}: {result.get('quality_score', 0):.1f}%")
                    if not result["success"]:
                        print(f"   Erreur: {result.get('error', 'Inconnue')}")
                    else:
                        missing = result.get('missing_fields', [])
                        if missing:
                            print(f"   Champs manquants: {', '.join(missing[:3])}")
        
        # Sauvegarder les résultats
        self.save_results()
    
    def save_results(self):
        """Sauvegarde les résultats"""
        
        timestamp = int(time.time())
        filename = f"cv_optimization_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_summary": {
                    "total_cvs": len(self.results),
                    "successful_tests": len([r for r in self.results if r["success"]]),
                    "avg_quality": sum(r["quality_score"] for r in self.results if r["success"]) / max(1, len([r for r in self.results if r["success"]])),
                    "success_rate": len([r for r in self.results if r["success"] and r["quality_score"] >= 80]) / len(self.results) * 100
                },
                "detailed_results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Résultats sauvegardés: {filename}")

def main():
    """Point d'entrée principal"""
    
    tester = CVOptimizationTester()
    
    # Lancer le test d'optimisation
    tester.run_optimization_test(max_cvs=10)
    
    print(f"\n{Colors.BOLD}💡 === PROCHAINES ÉTAPES ==={Colors.END}")
    print("1. Intégrer l'optimiseur dans le parser existant")
    print("2. Remplacer simulate_openai_call() par le vrai appel API")
    print("3. Tester sur l'ensemble des 69 CVs")
    print("4. Mesurer l'amélioration vs baseline 54.5%")

if __name__ == "__main__":
    main()
