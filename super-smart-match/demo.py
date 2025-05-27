#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de démarrage pour SuperSmartMatch
Démonstration et test du service unifié
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.app import create_app
from core.engine import SuperSmartMatchEngine, MatchOptions, AlgorithmType

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_data():
    """Crée des données de test pour démontrer SuperSmartMatch"""
    
    candidat_test = {
        "id": "candidate_001",
        "nom": "Jean Dupont",
        "competences": ["Python", "React", "JavaScript", "SQL", "Docker"],
        "annees_experience": 4,
        "adresse": "Paris, France",
        "mobilite": "hybrid",
        "salaire_souhaite": 55000,
        "contrats_recherches": ["CDI"],
        "disponibilite": "immediate",
        "soft_skills": ["communication", "leadership", "autonomie"],
        "criteres_importants": {
            "salaire_important": True,
            "localisation_importante": False,
            "culture_importante": True
        }
    }
    
    offres_test = [
        {
            "id": "job_001",
            "titre": "Développeur Full Stack Python/React",
            "entreprise": "TechCorp",
            "competences": ["Python", "React", "JavaScript", "PostgreSQL"],
            "localisation": "Paris",
            "type_contrat": "CDI",
            "salaire": "50K-60K€",
            "experience_requise": 3,
            "politique_remote": "hybrid",
            "soft_skills": ["communication", "travail en équipe"],
            "culture_entreprise": {
                "valeurs": ["innovation", "collaboration", "excellence"],
                "taille_equipe": "moyenne"
            }
        },
        {
            "id": "job_002",
            "titre": "Data Scientist",
            "entreprise": "DataLab",
            "competences": ["Python", "Machine Learning", "Pandas", "SQL"],
            "localisation": "Lyon",
            "type_contrat": "CDI",
            "salaire": "60K-70K€",
            "experience_requise": 5,
            "politique_remote": "full-remote",
            "soft_skills": ["analytique", "autonomie"],
            "culture_entreprise": {
                "valeurs": ["innovation", "recherche", "liberté"],
                "taille_equipe": "petite"
            }
        },
        {
            "id": "job_003",
            "titre": "Frontend Developer React",
            "entreprise": "WebAgency",
            "competences": ["React", "JavaScript", "TypeScript", "CSS"],
            "localisation": "Paris",
            "type_contrat": "CDI",
            "salaire": "45K-55K€",
            "experience_requise": 2,
            "politique_remote": "onsite",
            "soft_skills": ["créativité", "attention aux détails"],
            "culture_entreprise": {
                "valeurs": ["créativité", "qualité", "client-first"],
                "taille_equipe": "grande"
            }
        }
    ]
    
    return candidat_test, offres_test

def test_all_algorithms(candidat: Dict[str, Any], offres: list):
    """Test tous les algorithmes disponibles"""
    
    print("🧪 Test de tous les algorithmes SuperSmartMatch")
    print("=" * 60)
    
    engine = SuperSmartMatchEngine()
    
    algorithms_to_test = [
        (AlgorithmType.AUTO, "🤖 Auto-sélection"),
        (AlgorithmType.ENHANCED, "⚡ Enhanced"),
        (AlgorithmType.SMART_MATCH, "🎯 SmartMatch"),
        (AlgorithmType.COMPARISON, "📊 Comparaison")
    ]
    
    results = {}
    
    for algo_type, description in algorithms_to_test:
        print(f"\n{description}")
        print("-" * 40)
        
        try:
            options = MatchOptions(
                algorithme=algo_type,
                limite=3,
                details=True,
                explications=True
            )
            
            result = engine.match(candidat, offres, options)
            
            print(f"✅ Statut: {result.status}")
            print(f"⚙️  Algorithme utilisé: {result.algorithme_utilise}")
            print(f"⏱️  Temps d'exécution: {result.temps_execution:.3f}s")
            print(f"📊 Résultats trouvés: {len(result.resultats)}")
            
            if result.resultats:
                print("🏆 Top 3 des matches:")
                for i, match in enumerate(result.resultats[:3], 1):
                    print(f"   {i}. {match.titre} - Score: {match.score_global}%")
                    if match.explications and options.explications:
                        for critere, explication in match.explications.items():
                            if explication:
                                print(f"      • {critere}: {explication}")
            
            results[algo_type.value] = result
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results[algo_type.value] = None
    
    return results

def demo_api_integration():
    """Démonstration de l'intégration API"""
    
    print("\n🚀 Démonstration de l'API SuperSmartMatch")
    print("=" * 50)
    
    candidat, offres = create_test_data()
    
    # Test de l'endpoint de matching
    print("📡 Test de l'endpoint /api/v1/match")
    
    test_request = {
        "candidat": candidat,
        "offres": offres,
        "options": {
            "algorithme": "auto",
            "limite": 5,
            "details": True,
            "explications": True
        }
    }
    
    print(f"📤 Requête de test créée avec {len(offres)} offres")
    print(f"👤 Candidat: {candidat['nom']} ({len(candidat['competences'])} compétences)")
    
    # Simulation d'une réponse API
    engine = SuperSmartMatchEngine()
    options = MatchOptions(
        algorithme=AlgorithmType.AUTO,
        limite=5,
        details=True,
        explications=True
    )
    
    try:
        result = engine.match(candidat, offres, options)
        
        api_response = {
            "status": result.status,
            "algorithme_utilise": result.algorithme_utilise,
            "temps_execution": result.temps_execution,
            "resultats": [
                {
                    "id": r.id,
                    "titre": r.titre,
                    "score_global": r.score_global,
                    "confiance": r.confiance
                }
                for r in result.resultats
            ],
            "meta": result.meta
        }
        
        print("✅ Réponse API simulée:")
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation API: {e}")

def show_integration_guide():
    """Affiche le guide d'intégration avec le front-end existant"""
    
    print("\n🔌 Guide d'intégration avec votre front-end")
    print("=" * 50)
    
    integration_examples = {
        "JavaScript": """
// Remplacer votre endpoint actuel
const response = await fetch('/api/v1/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        candidat: candidateData,
        offres: jobsData,
        options: { algorithme: 'auto', details: true }
    })
});

const results = await response.json();
        """,
        
        "HTML Form": """
<!-- Dans votre formulaire existant -->
<form id="matching-form">
    <!-- Vos champs existants -->
    <select name="algorithme">
        <option value="auto">Auto-sélection</option>
        <option value="enhanced">Enhanced</option>
        <option value="smart-match">SmartMatch</option>
    </select>
    <button type="submit">Lancer le matching</button>
</form>
        """,
        
        "Configuration": """
# Variables d'environnement
SUPER_SMART_MATCH_URL=http://localhost:5000
SUPER_SMART_MATCH_MODE=auto
OPENAI_API_KEY=your-openai-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
        """
    }
    
    for language, code in integration_examples.items():
        print(f"\n📝 {language}:")
        print(code)

def main():
    """Fonction principale de démonstration"""
    
    print("🚀 SuperSmartMatch - Service Unifié de Matching")
    print("🏗️  Nexten - Algorithmes de Matching Intelligents")
    print("=" * 60)
    
    # Créer les données de test
    candidat, offres = create_test_data()
    
    print(f"📊 Données de test créées:")
    print(f"   👤 Candidat: {candidat['nom']}")
    print(f"   💼 Compétences: {', '.join(candidat['competences'][:3])}...")
    print(f"   🏢 Offres: {len(offres)} postes disponibles")
    
    # Test des algorithmes
    results = test_all_algorithms(candidat, offres)
    
    # Démonstration API
    demo_api_integration()
    
    # Guide d'intégration
    show_integration_guide()
    
    print("\n🎯 Prochaines étapes:")
    print("   1. 📦 Installer les dépendances: pip install -r requirements.txt")
    print("   2. 🔧 Configurer les variables d'environnement")
    print("   3. 🚀 Lancer le service: python -m api.app")
    print("   4. 🔌 Intégrer avec votre front-end existant")
    print("   5. 📈 Monitorer les performances via /api/v1/performance")
    
    print(f"\n✨ SuperSmartMatch est prêt à optimiser vos matchings !")

if __name__ == "__main__":
    main()
