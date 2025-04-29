
#!/bin/bash

# Script pour reconstruire et redémarrer le service cv-parser avec logs de debug

echo "🛑 Arrêt des services cv-parser et cv-parser-worker..."
docker-compose stop cv-parser cv-parser-worker

echo "🔄 Suppression des conteneurs existants..."
docker-compose rm -f cv-parser cv-parser-worker

echo "🛠️ Reconstruction des images avec cache invalidé..."
docker-compose build --no-cache cv-parser cv-parser-worker

echo "🔧 Configuration du mode debug et logging..."
export LOG_LEVEL=DEBUG

echo "🚀 Démarrage des services en mode debug..."
docker-compose up -d cv-parser cv-parser-worker

echo "📊 Vérification du statut des services..."
docker-compose ps cv-parser cv-parser-worker

echo "📋 Affichage des logs pour vérifier le démarrage..."
docker-compose logs --tail=50 cv-parser

echo "✅ Service redémarré avec succès!"
echo ""
echo "✨ Instructions de test ✨"
echo "1. Accédez à l'interface de parsing: http://localhost:3000/cv-upload"
echo "2. Téléchargez votre CV et activez l'option 'Force refresh'"
echo "3. Pour suivre les logs en temps réel: docker-compose logs -f cv-parser"
echo ""
echo "Si le parsing échoue, vérifiez que:"
echo "- Votre clé API OpenAI est correctement configurée dans .env"
echo "- Le format de votre CV est supporté (PDF, DOCX, etc.)"
echo "- Le CV n'est pas trop volumineux ou complexe"
