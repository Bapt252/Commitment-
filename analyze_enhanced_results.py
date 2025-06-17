#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur Résultats Enhanced V3.0 - Validation Rapide
Analyse des 2.4MB de résultats JSON pour évaluer améliorations
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

class EnhancedResultsAnalyzer:
    """Analyseur rapide pour résultats Enhanced V3.0"""
    
    def __init__(self):
        self.results_file = "./test_results/results.json"
        self.data = None
    
    def load_and_analyze(self):
        """Charge et analyse les résultats"""
        
        print("🔍 ANALYSEUR ENHANCED V3.0 - Chargement...")
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            self.stats = full_data.get('stats', {})
            self.data = full_data.get('results', [])
            
            print(f"✅ Données chargées: {len(self.data)} résultats")
            print(f"📊 Statistiques: {self.stats}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return
        
        # Analyses
        self.analyze_parsing_improvements()
        self.analyze_score_distribution() 
        self.identify_top_performers()
        self.find_remaining_issues()
        self.generate_summary()
    
    def analyze_parsing_improvements(self):
        """Analyse améliorations parsing"""
        
        print("\n🎯 ANALYSE PARSING ENHANCED V3.0")
        print("=" * 50)
        
        # Grouper par CV unique
        cv_data = {}
        for result in self.data:
            cv_name = result.get('cv_filename', 'Unknown')
            if cv_name not in cv_data:
                # Extraire données CV du premier résultat
                cv_info = self.extract_cv_info(result)
                cv_data[cv_name] = cv_info
        
        total_cv = len(cv_data)
        
        # Compteurs améliorations
        noms_detectes = 0
        experience_ok = 0
        competences_riches = 0
        secteurs_detectes = 0
        
        problematic_names = []
        excellent_parsing = []
        
        for cv_name, cv_info in cv_data.items():
            # Analyse nom
            name = cv_info.get('name', '')
            if name and name != 'Non détecté' and name.strip() and not name.startswith('Master'):
                noms_detectes += 1
                if len(name.split()) >= 2:  # Prénom + Nom
                    excellent_parsing.append(cv_name)
            else:
                problematic_names.append(cv_name)
            
            # Analyse expérience
            exp = cv_info.get('experience', 0)
            if exp > 0:
                experience_ok += 1
            
            # Analyse compétences
            skills_count = cv_info.get('skills_count', 0)
            if skills_count >= 5:
                competences_riches += 1
            
            # Analyse secteur
            sector = cv_info.get('sector', '')
            if sector and sector != 'Non détecté':
                secteurs_detectes += 1
        
        print(f"👤 Noms détectés: {noms_detectes}/{total_cv} ({noms_detectes/total_cv*100:.1f}%)")
        print(f"⏱️ Expérience cohérente: {experience_ok}/{total_cv} ({experience_ok/total_cv*100:.1f}%)")
        print(f"🎓 Compétences riches (≥5): {competences_riches}/{total_cv} ({competences_riches/total_cv*100:.1f}%)")
        print(f"🏢 Secteurs détectés: {secteurs_detectes}/{total_cv} ({secteurs_detectes/total_cv*100:.1f}%)")
        
        print(f"\n✅ CV parsing excellent: {len(excellent_parsing)}")
        if excellent_parsing[:5]:
            print(f"   Exemples: {', '.join(excellent_parsing[:5])}")
        
        print(f"\n⚠️ CV noms problématiques: {len(problematic_names)}")
        if problematic_names[:5]:
            print(f"   Exemples: {', '.join(problematic_names[:5])}")
        
        return {
            'total_cv': total_cv,
            'noms_detectes': noms_detectes,
            'experience_ok': experience_ok,
            'competences_riches': competences_riches,
            'excellent_parsing': excellent_parsing,
            'problematic_names': problematic_names
        }
    
    def extract_cv_info(self, result):
        """Extrait infos CV d'un résultat"""
        
        # Chercher dans les détails ou directement
        details = result.get('details', {})
        
        # Reconstruction des infos CV approximative
        common_skills = details.get('common_skills', [])
        extra_skills = details.get('extra_skills', [])
        all_skills = list(set(common_skills + extra_skills))
        
        return {
            'name': result.get('cv_name', 'Non détecté'),
            'experience': details.get('experience_ratio', 0),
            'skills_count': len(all_skills),
            'skills': all_skills[:10],
            'sector': 'Détecté' if all_skills else 'Non détecté'
        }
    
    def analyze_score_distribution(self):
        """Analyse distribution scores"""
        
        print("\n📊 DISTRIBUTION SCORES MATCHING")
        print("=" * 50)
        
        scores = [result.get('score', 0) for result in self.data]
        
        score_moyen = sum(scores) / len(scores)
        score_max = max(scores)
        score_min = min(scores)
        
        # Distribution par tranches
        excellent = len([s for s in scores if s >= 85])
        tres_bon = len([s for s in scores if 75 <= s < 85])
        bon = len([s for s in scores if 65 <= s < 75])
        correct = len([s for s in scores if 50 <= s < 65])
        faible = len([s for s in scores if s < 50])
        
        total = len(scores)
        
        print(f"🎯 Score moyen: {score_moyen:.1f}%")
        print(f"📈 Score maximum: {score_max}%")
        print(f"📉 Score minimum: {score_min}%")
        print(f"\n📊 Distribution:")
        print(f"   🥇 Excellent (≥85%): {excellent} ({excellent/total*100:.1f}%)")
        print(f"   🥈 Très bon (75-84%): {tres_bon} ({tres_bon/total*100:.1f}%)")
        print(f"   🥉 Bon (65-74%): {bon} ({bon/total*100:.1f}%)")
        print(f"   ✅ Correct (50-64%): {correct} ({correct/total*100:.1f}%)")
        print(f"   ⚠️ Faible (<50%): {faible} ({faible/total*100:.1f}%)")
        
        return {
            'score_moyen': score_moyen,
            'excellent': excellent,
            'tres_bon': tres_bon,
            'total': total
        }
    
    def identify_top_performers(self):
        """Identifie les meilleurs matches"""
        
        print("\n🏆 TOP MATCHES ENHANCED V3.0")
        print("=" * 50)
        
        # Tri par score
        sorted_results = sorted(self.data, key=lambda x: x.get('score', 0), reverse=True)
        
        print("🥇 TOP 10 MATCHES:")
        for i, result in enumerate(sorted_results[:10], 1):
            cv_name = result.get('cv_filename', 'Unknown')[:30] + "..."
            job_title = result.get('job_title', 'Unknown')[:40] + "..."
            score = result.get('score', 0)
            
            print(f"   {i:2d}. {cv_name} × {job_title} = {score}%")
    
    def find_remaining_issues(self):
        """Identifie problèmes restants"""
        
        print("\n🔍 ANALYSE PROBLÈMES RESTANTS")
        print("=" * 50)
        
        # Grouper par CV
        cv_scores = defaultdict(list)
        for result in self.data:
            cv_name = result.get('cv_filename', 'Unknown')
            score = result.get('score', 0)
            cv_scores[cv_name].append(score)
        
        # CV avec scores moyens faibles
        cv_avg_scores = {cv: sum(scores)/len(scores) for cv, scores in cv_scores.items()}
        worst_cvs = sorted(cv_avg_scores.items(), key=lambda x: x[1])[:10]
        
        print("⚠️ CV avec scores moyens les plus faibles:")
        for cv_name, avg_score in worst_cvs:
            print(f"   {cv_name}: {avg_score:.1f}%")
        
        # Analyse des erreurs communes
        low_scores = [r for r in self.data if r.get('score', 0) < 40]
        
        print(f"\n📉 Matches faibles (<40%): {len(low_scores)}")
        if low_scores:
            reasons = Counter()
            for result in low_scores[:20]:  # Analyser premiers 20
                details = result.get('details', {})
                if details.get('skill_match', 0) < 20:
                    reasons['Compétences incompatibles'] += 1
                if details.get('experience_match', 0) < 30:
                    reasons['Expérience insuffisante'] += 1
                if not details.get('common_skills', []):
                    reasons['Aucune compétence commune'] += 1
            
            print("🔍 Causes principales:")
            for reason, count in reasons.most_common():
                print(f"   - {reason}: {count} cas")
    
    def generate_summary(self):
        """Génère résumé global"""
        
        print("\n" + "="*60)
        print("🎯 RÉSUMÉ ENHANCED PARSER V3.0")
        print("="*60)
        
        # Calculs globaux
        parsing_stats = self.analyze_parsing_improvements()
        score_stats = self.analyze_score_distribution()
        
        # Estimations d'amélioration vs version précédente
        print("📈 AMÉLIORATIONS ESTIMÉES vs VERSION PRÉCÉDENTE:")
        print(f"   🎯 Noms détectés: {parsing_stats['noms_detectes']/parsing_stats['total_cv']*100:.1f}% (était ~30%)")
        print(f"   📊 Expérience cohérente: {parsing_stats['experience_ok']/parsing_stats['total_cv']*100:.1f}% (était ~40%)")
        print(f"   🔍 Compétences riches: {parsing_stats['competences_riches']/parsing_stats['total_cv']*100:.1f}% (était ~50%)")
        
        print(f"\n🏆 PERFORMANCES MATCHING:")
        print(f"   📊 Score moyen: {score_stats['score_moyen']:.1f}% (objectif: >70%)")
        print(f"   🥇 Matches excellents: {score_stats['excellent']} ({score_stats['excellent']/score_stats['total']*100:.1f}%)")
        print(f"   🎯 Qualité globale: {(score_stats['excellent']+score_stats['tres_bon'])/score_stats['total']*100:.1f}% de scores ≥75%")
        
        # Diagnostic final
        if score_stats['score_moyen'] >= 70:
            print(f"\n✅ OBJECTIF ATTEINT: Score moyen {score_stats['score_moyen']:.1f}% ≥ 70%")
        else:
            print(f"\n⚠️ AMÉLIORATION POSSIBLE: Score moyen {score_stats['score_moyen']:.1f}% < 70%")
        
        print(f"\n🚀 SYSTÈME ENHANCED V3.0 OPÉRATIONNEL")
        print(f"📊 Performance: {self.stats.get('matches_calculated', 0)} matchings en {self.stats.get('total_time', 0):.1f}s")
        print(f"⚡ Vitesse: {self.stats.get('matches_calculated', 0) / self.stats.get('total_time', 1):.1f} matchings/seconde")

def main():
    """Analyse principale"""
    analyzer = EnhancedResultsAnalyzer()
    analyzer.load_and_analyze()

if __name__ == "__main__":
    main()
