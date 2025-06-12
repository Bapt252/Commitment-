
#!/bin/bash

# Script pour redémarrer les services après les modifications

echo "🔄 Redémarrage des services après modifications du parsing CV..."

# Arrêter les services concernés
echo "🛑 Arrêt des services cv-parser, cv-parser-worker et frontend..."
docker-compose stop cv-parser cv-parser-worker frontend

# Reconstruire les services
echo "🛠️ Reconstruction des services cv-parser et cv-parser-worker..."
docker-compose build cv-parser cv-parser-worker

# Démarrer les services
echo "▶️ Démarrage des services..."
docker-compose up -d cv-parser cv-parser-worker frontend

# Vérifier le statut des services
echo "📊 Vérification du statut des services..."
docker-compose ps cv-parser cv-parser-worker frontend

echo "✅ Redémarrage terminé ! Vérifiez les logs pour vous assurer que tout fonctionne correctement."
echo "📝 Pour vérifier les logs du service cv-parser, exécutez: docker-compose logs -f cv-parser"
echo "🌐 Accédez à l'interface de parsing CV à l'adresse: http://localhost:3000/cv-upload"
