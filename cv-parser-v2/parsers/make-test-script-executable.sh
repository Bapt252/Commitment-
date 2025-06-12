#!/bin/bash
# Ce script rend test-cv-simple.sh exécutable

chmod +x test-cv-simple.sh
chmod +x cv-parser-service/test_parser_simple.py

echo "Scripts rendus exécutables avec succès."
echo "Vous pouvez maintenant tester le parsing avec:"
echo "./test-cv-simple.sh <chemin_vers_votre_cv.pdf>"
