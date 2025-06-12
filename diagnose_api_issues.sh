#!/bin/bash

# 🔍 Diagnostic précis des problèmes restants
# CV Parser V2 fonctionne, mais problèmes avec Enhanced API V2.1

echo "🔍 === DIAGNOSTIC PRÉCIS SYSTÈME V2.1 ==="
echo "Services fonctionnels, analyse des problèmes API..."
echo ""

# Test détaillé Hugo Salvat
echo "👨‍💼 === TEST HUGO SALVAT DÉTAILLÉ ==="
echo ""

echo "Requête Hugo Salvat..."
HUGO_RESPONSE=$(curl -s http://localhost:5055/api/test/hugo-salvat)
echo "Réponse brute:"
echo "$HUGO_RESPONSE" | jq . 2>/dev/null || echo "$HUGO_RESPONSE"
echo ""

# Test détaillé Enhanced API
echo "🔧 === TEST ENHANCED API V2.1 DÉTAILLÉ ==="
echo ""

echo "Health check Enhanced API:"
HEALTH_RESPONSE=$(curl -s http://localhost:5055/health)
echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test des endpoints disponibles
echo "📋 === ENDPOINTS DISPONIBLES ==="
echo ""

echo "Test endpoint /api/matching/enhanced:"
curl -s -X POST http://localhost:5055/api/matching/enhanced \
  -H "Content-Type: application/json" \
  -d '{"test": "ping"}' | jq . 2>/dev/null || echo "Erreur format"
echo ""

# Test avec fichiers réels - diagnostic détaillé
echo "📄 === TEST FICHIERS RÉELS DÉTAILLÉ ==="
echo ""

BATU_CV="$HOME/Desktop/BATU Sam.pdf"
IT_JOB="$HOME/Desktop/IT .pdf"

if [ -f "$BATU_CV" ] && [ -f "$IT_JOB" ]; then
    echo "✅ Fichiers trouvés"
    echo "CV: $(ls -lh "$BATU_CV")"
    echo "Job: $(ls -lh "$IT_JOB")"
    echo ""
    
    echo "Test matching avec fichiers..."
    MATCHING_RESULT=$(curl -s -X POST \
        -F "cv_file=@$BATU_CV" \
        -F "job_file=@$IT_JOB" \
        http://localhost:5055/api/matching/files)
    
    echo "Réponse matching brute:"
    echo "$MATCHING_RESULT" | jq . 2>/dev/null || echo "$MATCHING_RESULT"
    echo ""
    
    # Test des parsers individuellement
    echo "🧪 Test CV Parser individuel:"
    CV_RESULT=$(curl -s -X POST -F "file=@$BATU_CV" http://localhost:5051/api/parse-cv/)
    echo "Status CV Parser:" 
    echo "$CV_RESULT" | grep -o '"status":"[^"]*"' || echo "Pas de status trouvé"
    echo ""
    
    echo "🧪 Test Job Parser individuel:"
    JOB_RESULT=$(curl -s -X POST -F "file=@$IT_JOB" http://localhost:5053/api/parse-job/)
    echo "Status Job Parser:"
    echo "$JOB_RESULT" | grep -o '"status":"[^"]*"' || echo "Pas de status trouvé"
    echo ""
else
    echo "❌ Fichiers non trouvés"
fi

# Vérification des logs Enhanced API
echo "📋 === LOGS ENHANCED API ==="
echo ""

echo "Processus Python Enhanced API:"
ps aux | grep -E "(api-matching-enhanced|5055)" | grep -v grep || echo "Aucun processus trouvé"
echo ""

# Test simple de l'Enhanced API
echo "🔧 === TEST SIMPLE ENHANCED API ==="
echo ""

echo "Test endpoint simple /api/matching/complete:"
SIMPLE_TEST=$(curl -s -X POST http://localhost:5055/api/matching/complete \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"name": "Test User", "skills": ["Python"]},
    "job_data": {"title": "Developer", "required_skills": ["Python"]}
  }')

echo "Réponse simple:"
echo "$SIMPLE_TEST" | jq . 2>/dev/null || echo "$SIMPLE_TEST"
echo ""

# Recommandations
echo "💡 === RECOMMANDATIONS ==="
echo ""

echo "1. Si Hugo Salvat ne retourne pas de score:"
echo "   - Vérifier la logique dans api-matching-enhanced-v2.py"
echo "   - Le test prédéfini doit retourner un JSON avec total_score"
echo ""

echo "2. Si matching fichiers échoue:"
echo "   - Vérifier que l'endpoint /api/matching/files existe"
echo "   - Tester les parsers individuellement d'abord"
echo ""

echo "3. Pour corriger:"
echo "   - Redémarrer Enhanced API: python api-matching-enhanced-v2.py"
echo "   - Vérifier les logs en temps réel"
echo ""

echo "✅ Diagnostic terminé. Le CV Parser V2 fonctionne, reste à ajuster Enhanced API V2.1"
