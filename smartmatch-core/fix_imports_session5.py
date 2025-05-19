#!/usr/bin/env python3
"""
Script de correction des imports Session 5
==========================================

Corrige automatiquement tous les imports relatifs problématiques
dans les modules Session 5 pour les transformer en imports absolus.

Usage: python fix_imports_session5.py

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

import os
import re
import glob
from pathlib import Path

def fix_imports_in_file(filepath):
    """Corrige les imports dans un fichier spécifique."""
    print(f"🔧 Analysing: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern pour corriger les imports avec ..
    patterns_replacements = [
        # from ..optimizers.optuna_optimizer import -> from optimizers.optuna_optimizer import
        (r'from \.\.([a-zA-Z_]+)\.([a-zA-Z_]+) import', r'from \1.\2 import'),
        # from ..optimizers import -> from optimizers import
        (r'from \.\.([a-zA-Z_]+) import', r'from \1 import'),
        # from .auto_trainer import -> from pipeline.auto_trainer import (contextualisé)
        (r'from \.([a-zA-Z_]+) import', lambda m: f'from {get_module_name(filepath)}.{m.group(1)} import'),
        # from . import -> from pipeline import (contextualisé)
        (r'from \. import', lambda m: f'from {get_module_name(filepath)} import'),
    ]
    
    # Appliquer les corrections
    modified = False
    for pattern, replacement in patterns_replacements:
        if callable(replacement):
            def repl_func(match):
                return replacement(match)
            new_content = re.sub(pattern, repl_func, content)
        else:
            new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            content = new_content
            modified = True
    
    # Sauvegarder si modifié
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   ✅ Corrigé")
        return True
    else:
        print(f"   ⚪ Aucun changement nécessaire")
        return False

def get_module_name(filepath):
    """Détermine le nom du module à partir du chemin de fichier."""
    parts = Path(filepath).parts
    for part in parts:
        if part in ['admin', 'pipeline', 'optimizers', 'metrics', 'datasets']:
            return part
    return 'unknown'

def scan_and_fix_all_modules():
    """Scanne et corrige tous les modules Session 5."""
    modules = ['admin', 'pipeline', 'optimizers', 'metrics', 'datasets']
    
    total_fixed = 0
    
    for module in modules:
        if not os.path.exists(module):
            print(f"❌ Module non trouvé: {module}")
            continue
        
        print(f"\n📁 Module: {module}")
        
        # Trouver tous les fichiers Python
        python_files = glob.glob(f"{module}/**/*.py", recursive=True)
        
        module_fixed = 0
        for filepath in python_files:
            if fix_imports_in_file(filepath):
                module_fixed += 1
                total_fixed += 1
        
        print(f"   📊 {module_fixed} fichiers corrigés dans {module}")
    
    return total_fixed

def verify_imports():
    """Vérifie que les imports fonctionnent après correction."""
    print(f"\n🔍 Vérification des imports corrigés...")
    
    import sys
    import importlib
    sys.path.insert(0, os.getcwd())
    
    modules_to_test = [
        ('admin', ['AdminOrchestrator', 'create_admin_config']),
        ('pipeline', ['PipelineOrchestrator', 'create_pipeline_config']),
        ('optimizers', ['OptunaSingleObjectiveOptimizer']),
        ('metrics', ['BusinessMetricsCollector']),
        ('datasets', ['SyntheticDataGenerator'])
    ]
    
    success_count = 0
    for module_name, classes in modules_to_test:
        try:
            # Recharger le module pour s'assurer d'avoir la version corrigée
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            
            module = importlib.import_module(module_name)
            
            # Vérifier que les classes existent
            for class_name in classes:
                if hasattr(module, class_name):
                    print(f"   ✅ {module_name}.{class_name}")
                else:
                    print(f"   ⚠️  {module_name}.{class_name} - classe non trouvée")
            
            success_count += 1
            
        except ImportError as e:
            print(f"   ❌ {module_name} - erreur import: {e}")
        except Exception as e:
            print(f"   ⚠️  {module_name} - autre erreur: {e}")
    
    print(f"\n📊 Résultat: {success_count}/{len(modules_to_test)} modules importés avec succès")
    return success_count == len(modules_to_test)

def create_test_script():
    """Crée un script de test pour valider Session 5."""
    test_script = '''#!/usr/bin/env python3
"""
Test rapide Session 5 post-correction
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_session5():
    """Test rapide de tous les modules Session 5."""
    print("🚀 Test Session 5 post-correction")
    print("=" * 40)
    
    try:
        # Test admin
        from admin import AdminOrchestrator, create_admin_config
        config = create_admin_config(enable_auth=False)
        print("✅ Admin: OK")
        
        # Test pipeline
        from pipeline import PipelineOrchestrator, create_pipeline_config
        pipeline_config = create_pipeline_config()
        print("✅ Pipeline: OK")
        
        # Test autres modules
        from optimizers import OptunaSingleObjectiveOptimizer
        from metrics import BusinessMetricsCollector
        from datasets import SyntheticDataGenerator
        print("✅ Autres modules: OK")
        
        print("\\n🎉 Session 5 entièrement fonctionnelle!")
        print(f"📊 Dashboard: http://localhost:{config['dashboard']['port']}")
        print(f"🔧 API: http://localhost:{config['model_controller']['api_port']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_session5()
'''
    
    with open('test_session5_corrected.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Script de test créé: test_session5_corrected.py")

def main():
    """Fonction principale."""
    print("🔧 Correction des imports Session 5")
    print("=" * 50)
    
    # 1. Correction des imports
    total_fixed = scan_and_fix_all_modules()
    print(f"\n📊 Total: {total_fixed} fichiers corrigés")
    
    # 2. Vérification
    if verify_imports():
        print("\n✅ Tous les imports fonctionnent correctement!")
    else:
        print("\n⚠️  Certains imports ont encore des problèmes")
    
    # 3. Créer script de test
    create_test_script()
    
    print("\n🎯 Prochaines étapes:")
    print("1. python test_session5_corrected.py")
    print("2. streamlit run simple_dashboard.py")
    print("3. python demo_session5_integration_fixed.py --create-config")

if __name__ == "__main__":
    main()
