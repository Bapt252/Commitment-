# FICHIER SUPPRIMÉ - REMPLACÉ PAR SuperSmartMatch v2.1
# 
# Ce fichier a été supprimé lors du nettoyage des algorithmes obsolètes
# Remplacé par: super-smart-match/algorithms/supersmartmatch.py (mode bidirectionnel)
# 
# Raison: Matching "reverse" basique comparé au système bidirectionnel SuperSmartMatch v2.1:
# 
# ANCIEN (matching_engine_reverse.py):
# - Pondération fixe selon type de poste
# - Logique de scoring simpliste
# - Pas d'analytics
# - Explications basiques
# - Performance non optimisée
# 
# NOUVEAU (SuperSmartMatch v2.1 bidirectionnel):
# - Pondération dynamique selon priorités CANDIDAT
# - Raisonnement intelligent avec analyse risques/opportunités
# - Analytics intégrés et monitoring
# - Scoring côté entreprise avec profiling candidat détaillé
# - Explications enrichies avec recommandations
# - Performance optimisée < 200ms
# - Analyse flexibilité (télétravail, horaires, RTT)
# - Matching symétrique candidat↔entreprise
#
# Le matching bidirectionnel SuperSmartMatch v2.1 est bien plus sophistiqué:
# - Adapte la pondération selon chaque candidat individuellement
# - Analyse 4 leviers: évolution, rémunération, proximité, flexibilité
# - Génère des scores côté entreprise personnalisés
# - Propose des analyses de risques et recommandations
#
# Date suppression: 2025-05-28
# Audit: claude-audit-supersmartmatch
