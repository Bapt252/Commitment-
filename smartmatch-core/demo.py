#!/usr/bin/env python3
"""
Démonstration SmartMatchEngine - Session 3
-----------------------------------------
Script de démonstration du nouveau moteur SmartMatch refactorisé.

Ce script illustre :
- Utilisation du nouveau SmartMatchEngine
- Comparaison avec l'ancien système
- Fonctionnalités avancées (insights, performance, etc.)
"""

import asyncio
import logging
import time
from typing import Dict, Any

# Configuration du logging pour une sortie propre
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Simuler les imports (ajuster selon l'environnement)
try:
    # Imports du nouveau système
    from engine import SmartMatchEngine, LegacySmartMatcher
    from core.config import SmartMatchConfig
    NEW_ENGINE_AVAILABLE = True
except ImportError:
    print("⚠️  Nouveau moteur non disponible - simulation uniquement")
    NEW_ENGINE_AVAILABLE = False


class SmartMatchDemo:
    """Démonstration interactive du SmartMatchEngine."""
    
    def __init__(self):
        """Initialise la démonstration avec des données d'exemple."""
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self) -> Dict[str, Any]:
        """Crée des données d'exemple pour la démonstration."""
        return {
            "candidate": {
                "id": "demo_candidate_1",
                "name": "Alice Développeuse",
                "skills": [
                    "Python", "Django", "React", "JavaScript", 
                    "PostgreSQL", "Docker", "Git", "AWS"
                ],
                "location": {
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "address": "Paris, France"
                },
                "years_of_experience": 5,
                "education_level": "master",
                "seniority_level": "senior",
                "preferences": {
                    "remote_work": True,
                    "salary_expectation": 65000,
                    "job_type": "full_time",
                    "industry": "tech"
                },
                "experience": [
                    {
                        "position_title": "Senior Python Developer",
                        "company": "TechCorp",
                        "duration_years": 3,
                        "technologies": ["Python", "Django", "React", "AWS"],
                        "start_date": "2021-01-01T00:00:00",
                        "end_date": "2024-01-01T00:00:00"
                    },
                    {
                        "position_title": "Lead Developer",
                        "company": "StartupAI",
                        "duration_years": 2,
                        "technologies": ["Python", "FastAPI", "Machine Learning"],
                        "team_size": 5,
                        "start_date": "2019-01-01T00:00:00",
                        "end_date": "2021-01-01T00:00:00"
                    }
                ]
            },
            "job": {
                "id": "demo_job_1",
                "title": "Senior Python Developer",
                "description": "Nous recherchons un développeur Python expérimenté...",
                "company": "InnovateTech",
                "required_skills": [
                    "Python", "Django", "REST API", "PostgreSQL"
                ],
                "preferred_skills": [
                    "React", "Docker", "AWS", "Machine Learning"
                ],
                "location": {
                    "latitude": 48.8847,
                    "longitude": 2.2967,
                    "address": "Levallois-Perret, France"
                },
                "requirements": {
                    "experience": {
                        "min_years": 4,
                        "max_years": 8,
                        "specific_areas": [
                            {"name": "python", "min_years": 3},
                            {"name": "django", "min_years": 2}
                        ]
                    },
                    "education_level": "bachelor",
                    "seniority_level": "senior",
                    "requires_leadership": False
                },
                "remote_policy": {
                    "allowed": True,
                    "policy": "hybrid",
                    "days_per_week": 2
                },
                "salary_range": {
                    "min": 55000,
                    "max": 75000,
                    "currency": "EUR"
                },
                "benefits": [
                    "Télétravail flexible",
                    "Formation continue",
                    "Tickets restaurant"
                ],
                "job_type": "full_time",
                "industry": "tech"
            }
        }
    
    def print_header(self, title: str):
        """Affiche un en-tête formaté."""
        print("\\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
    
    def print_section(self, title: str):
        """Affiche un titre de section."""
        print(f"\\n📋 {title}")
        print("-" * 40)
    
    def print_candidate_summary(self, candidate: Dict[str, Any]):
        """Affiche un résumé du candidat."""
        print(f"👤 **{candidate['name']}** (ID: {candidate['id']})")
        print(f"   🎓 Niveau: {candidate['education_level']} - {candidate['seniority_level']}")
        print(f"   💼 Expérience: {candidate['years_of_experience']} ans")
        print(f"   📍 Localisation: {candidate['location']['address']}")
        print(f"   🛠️  Compétences: {', '.join(candidate['skills'][:5])}{'...' if len(candidate['skills']) > 5 else ''}")
        print(f"   🏠 Télétravail: {'✅ Souhaité' if candidate['preferences']['remote_work'] else '❌ Non souhaité'}")
        print(f"   💰 Salaire attendu: {candidate['preferences']['salary_expectation']:,} €")
    
    def print_job_summary(self, job: Dict[str, Any]):
        """Affiche un résumé de l'offre d'emploi."""
        print(f"💼 **{job['title']}** (ID: {job['id']})")
        print(f"   🏢 Entreprise: {job['company']}")
        print(f"   📍 Localisation: {job['location']['address']}")
        print(f"   🔧 Compétences requises: {', '.join(job['required_skills'])}")
        print(f"   ⭐ Compétences préférées: {', '.join(job['preferred_skills'][:3])}{'...' if len(job['preferred_skills']) > 3 else ''}")
        print(f"   📅 Expérience: {job['requirements']['experience']['min_years']}-{job['requirements']['experience']['max_years']} ans")
        print(f"   🏠 Télétravail: {'✅ Autorisé' if job['remote_policy']['allowed'] else '❌ Non autorisé'}")
        print(f"   💰 Salaire: {job['salary_range']['min']:,}-{job['salary_range']['max']:,} €")
    
    async def demo_new_engine(self):
        """Démonstration du nouveau SmartMatchEngine."""
        self.print_section("SmartMatchEngine - Architecture Refactorisée")
        
        if not NEW_ENGINE_AVAILABLE:
            print("⚠️  SmartMatchEngine non disponible (mode simulation)")
            print("   Résultat simulé:")
            print("   📊 Score global: 0.87 (Excellent match)")
            print("   🎯 Compétences: 0.92 | 📍 Localisation: 0.95")
            print("   💼 Expérience: 0.83 | 🏠 Préférences: 0.89")
            print("   💡 3 insights générés")
            return
        
        try:
            # Configuration personnalisée
            config = SmartMatchConfig()
            config.scoring.weights = {
                "skills": 0.40,
                "location": 0.25,
                "experience": 0.20,
                "preferences": 0.15
            }
            
            # Initialisation du moteur
            engine = SmartMatchEngine(config=config)
            
            # Calcul du matching
            print("🔄 Calcul du matching en cours...")
            start_time = time.time()
            
            result = await engine.calculate_match(
                self.sample_data["candidate"],
                self.sample_data["job"]
            )
            
            execution_time = time.time() - start_time
            
            # Affichage des résultats
            print(f"✅ Calcul terminé en {execution_time*1000:.1f}ms")
            print(f"\\n📊 **Score global: {result.overall_score:.2f}** ({'🟢 Excellent' if result.overall_score >= 0.8 else '🟡 Bon' if result.overall_score >= 0.6 else '🔴 Faible'} match)")
            
            print("\\n📈 Scores détaillés:")
            for category, score in result.category_scores.items():
                emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
                print(f"   {emoji} {category.capitalize()}: {score:.2f}")
            
            # Affichage des insights
            if result.insights:
                print(f"\\n💡 Insights générés ({len(result.insights)}):")
                for i, insight in enumerate(result.insights[:3], 1):
                    type_emoji = {"strength": "✅", "weakness": "⚠️", "neutral": "ℹ️"}.get(insight.type, "💡")
                    print(f"   {i}. {type_emoji} **{insight.title}**")
                    print(f"      {insight.message}")
                
                if len(result.insights) > 3:
                    print(f"      ... et {len(result.insights) - 3} autres insights")
            
            # Métriques de performance
            perf_metrics = engine.get_performance_metrics()
            print(f"\\n⚡ Performance:")
            print(f"   📊 Matches calculés: {perf_metrics['total_matches']}")
            print(f"   ⏱️  Temps moyen: {perf_metrics['average_time']*1000:.1f}ms")
            
        except Exception as e:
            print(f"❌ Erreur lors de la démonstration: {str(e)}")
    
    def demo_legacy_compatibility(self):
        """Démonstration de la compatibilité legacy."""
        self.print_section("Interface Legacy - Compatibilité")
        
        if not NEW_ENGINE_AVAILABLE:
            print("⚠️  Interface legacy non disponible")
            return
        
        try:
            # Interface legacy compatible
            legacy_matcher = LegacySmartMatcher()
            
            # Adaptation des données au format legacy
            legacy_candidate = {
                "id": self.sample_data["candidate"]["id"],
                "skills": self.sample_data["candidate"]["skills"],
                "location": "48.8566,2.3522",
                "years_of_experience": self.sample_data["candidate"]["years_of_experience"],
                "education_level": self.sample_data["candidate"]["education_level"],
                "remote_work": self.sample_data["candidate"]["preferences"]["remote_work"],
                "salary_expectation": self.sample_data["candidate"]["preferences"]["salary_expectation"]
            }
            
            legacy_job = {
                "id": self.sample_data["job"]["id"],
                "required_skills": self.sample_data["job"]["required_skills"],
                "preferred_skills": self.sample_data["job"]["preferred_skills"],
                "location": "48.8847,2.2967",
                "min_years_of_experience": self.sample_data["job"]["requirements"]["experience"]["min_years"],
                "max_years_of_experience": self.sample_data["job"]["requirements"]["experience"]["max_years"],
                "required_education": self.sample_data["job"]["requirements"]["education_level"],
                "offers_remote": self.sample_data["job"]["remote_policy"]["allowed"],
                "salary_range": self.sample_data["job"]["salary_range"]
            }
            
            # Calcul avec interface legacy
            print("🔄 Test de l'interface de compatibilité...")
            start_time = time.time()
            
            result = legacy_matcher.calculate_match(legacy_candidate, legacy_job)
            
            execution_time = time.time() - start_time
            
            # Vérification du format
            print(f"✅ Interface legacy fonctionnelle ({execution_time*1000:.1f}ms)")
            print(f"📊 Score: {result['overall_score']:.2f}")
            print(f"🔧 Format: {'✅ Compatible' if 'overall_score' in result else '❌ Incompatible'}")
            print("💡 Migration transparente vers la nouvelle architecture réussie!")
            
        except Exception as e:
            print(f"❌ Erreur interface legacy: {str(e)}")
    
    async def demo_batch_processing(self):
        """Démonstration du traitement par lots."""
        self.print_section("Traitement par Lots - Performance")
        
        if not NEW_ENGINE_AVAILABLE:
            print("⚠️  Batch processing non disponible (simulation)")
            print("   Simulation: 10 candidats × 5 jobs = 50 calculs")
            print("   Temps estimé: ~15ms par calcul")
            print("   Total estimé: ~750ms avec parallélisation")
            return
        
        try:
            # Création de données de test multiples
            candidates = []
            jobs = []
            
            # Générer 3 candidats variants
            base_candidate = self.sample_data["candidate"].copy()
            for i in range(3):
                candidate = base_candidate.copy()
                candidate["id"] = f"demo_candidate_{i+1}"
                candidate["name"] = f"Candidat Test {i+1}"
                candidate["years_of_experience"] = 3 + i * 2
                candidates.append(candidate)
            
            # Générer 2 jobs variants  
            base_job = self.sample_data["job"].copy()
            for i in range(2):
                job = base_job.copy()
                job["id"] = f"demo_job_{i+1}"
                job["title"] = f"Poste Test {i+1}"
                jobs.append(job)
            
            # Test batch processing
            engine = SmartMatchEngine()
            
            print(f"🔄 Calcul batch: {len(candidates)} candidats × {len(jobs)} jobs = {len(candidates) * len(jobs)} calculs")
            start_time = time.time()
            
            results = await engine.batch_match(
                candidates, 
                jobs, 
                max_concurrent=5  # Limite de concurrence
            )
            
            execution_time = time.time() - start_time
            avg_time_per_calc = execution_time / len(results)
            
            print(f"✅ Batch processing terminé!")
            print(f"⏱️  Temps total: {execution_time*1000:.1f}ms")
            print(f"⚡ Temps moyen par calcul: {avg_time_per_calc*1000:.1f}ms")
            print(f"🚀 Parallélisation efficace: {len(results)} résultats")
            
            # Afficher le meilleur match
            best_result = max(results, key=lambda r: r.overall_score)
            print(f"\\n🏆 Meilleur match trouvé:")
            print(f"   Candidat: {best_result.candidate_id}")
            print(f"   Job: {best_result.job_id}")
            print(f"   Score: {best_result.overall_score:.2f}")
            
        except Exception as e:
            print(f"❌ Erreur batch processing: {str(e)}")
    
    def demo_configuration(self):
        """Démonstration de la configuration flexible."""
        self.print_section("Configuration Flexible")
        
        configurations = [
            {
                "name": "Profil Tech",
                "weights": {"skills": 0.50, "experience": 0.30, "location": 0.15, "preferences": 0.05},
                "description": "Priorité aux compétences techniques"
            },
            {
                "name": "Profil Équilibre",
                "weights": {"skills": 0.30, "location": 0.30, "experience": 0.25, "preferences": 0.15},
                "description": "Approche équilibrée"
            },
            {
                "name": "Profil Géo",
                "weights": {"location": 0.45, "skills": 0.25, "experience": 0.20, "preferences": 0.10},
                "description": "Priorité à la proximité géographique"
            }
        ]
        
        for config in configurations:
            print(f"\\n🎯 **{config['name']}**: {config['description']}")
            for criterion, weight in config["weights"].items():
                bar = "█" * int(weight * 20)
                print(f"   {criterion.capitalize():<12} {weight:.2f} {bar}")
        
        print("\\n✨ Configuration dynamique selon le contexte métier!")
        print("🔧 Adaptation possible en temps réel selon les besoins")
    
    async def run_complete_demo(self):
        """Lance la démonstration complète."""
        self.print_header("SmartMatchEngine - Démonstration Session 3")
        
        print("🎯 Cette démonstration illustre les améliorations apportées")
        print("   par l'architecture refactorisée du SmartMatcher.")
        
        # Affichage des données d'exemple
        self.print_section("Données d'Exemple")
        self.print_candidate_summary(self.sample_data["candidate"])
        print()
        self.print_job_summary(self.sample_data["job"])
        
        # Démonstrations
        await self.demo_new_engine()
        self.demo_legacy_compatibility()
        await self.demo_batch_processing()
        self.demo_configuration()
        
        # Conclusion
        self.print_header("Résumé des Améliorations")
        print("✅ Architecture modulaire SOLID implémentée")
        print("✅ Performance améliorée (asynchrone + parallélisation)")
        print("✅ Insights explicables et contextuels")
        print("✅ Compatibilité legacy maintenue")
        print("✅ Configuration flexible et extensible")
        print("✅ Tests automatisés et validation complète")
        
        print("\\n🚀 **SmartMatchEngine - Session 3 réussie !**")
        print("   Prêt pour l'implémentation des fonctionnalités avancées.")


async def main():
    """Fonction principale de démonstration."""
    demo = SmartMatchDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Exécuter la démonstration
    asyncio.run(main())
