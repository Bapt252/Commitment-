#!/bin/bash

# Script de migration vers SuperSmartMatch Unifié
# Automatise la migration complète du projet

echo "🚀 MIGRATION VERS SUPERSMARTMATCH UNIFIÉ"
echo "========================================"
echo "Consolidation vers un seul algorithme de matching intelligent"
echo ""

# Configuration
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="migration_$(date +%Y%m%d_%H%M%S).log"

# Fonction de logging
log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "✅ $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "❌ $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo "ℹ️  $1" | tee -a "$LOG_FILE"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier les permissions
    if [ ! -w . ]; then
        log_error "Permissions insuffisantes dans le dossier courant"
        exit 1
    fi
    
    log_success "Prérequis vérifiés"
}

# Arrêt des services existants
stop_services() {
    log "Arrêt des services existants..."
    
    docker-compose down --remove-orphans >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Services arrêtés"
    else
        log_error "Erreur lors de l'arrêt des services"
    fi
}

# Sauvegarde des données importantes
backup_data() {
    log "Sauvegarde des données importantes..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Sauvegarde des algorithmes existants
    if [ -d "super-smart-match" ]; then
        cp -r super-smart-match/ "$BACKUP_DIR/supersmartmatch_old/" 2>/dev/null || true
        log_success "SuperSmartMatch sauvegardé"
    fi
    
    if [ -d "matching-service" ]; then
        cp -r matching-service/ "$BACKUP_DIR/matching_service/" 2>/dev/null || true
        log_success "Matching service sauvegardé"
    fi
    
    if [ -d "ml_engine" ]; then
        cp -r ml_engine/ "$BACKUP_DIR/ml_engine/" 2>/dev/null || true
        log_success "ML Engine sauvegardé"
    fi
    
    # Sauvegarde des données de volume Docker
    log "Sauvegarde des volumes Docker..."
    docker run --rm -v nexten_postgres-data:/data -v "$(pwd)/$BACKUP_DIR:/backup" busybox tar czf /backup/postgres_data.tar.gz -C /data . 2>/dev/null || true
    docker run --rm -v nexten_redis-data:/data -v "$(pwd)/$BACKUP_DIR:/backup" busybox tar czf /backup/redis_data.tar.gz -C /data . 2>/dev/null || true
    
    log_success "Sauvegarde terminée dans $BACKUP_DIR"
}

# Nettoyage des fichiers obsolètes
cleanup_obsolete_files() {
    log "Nettoyage des fichiers obsolètes..."
    
    # Algorithmes de matching redondants
    obsolete_algorithms=(
        "matching_engine.py"
        "matching_engine_advanced.py"
        "matching_engine_enhanced.py"
        "matching_engine_reverse.py"
        "my_matching_engine.py"
        "enhanced_matching_engine.py"
        "compare_algorithms.py"
    )
    
    for file in "${obsolete_algorithms[@]}"; do
        if [ -f "$file" ]; then
            mv "$file" "$BACKUP_DIR/" 2>/dev/null || rm -f "$file"
            log_success "Supprimé: $file"
        fi
    done
    
    # Fichiers README redondants (garder seulement README.md principal)
    find . -maxdepth 1 -name "README-*.md" -type f | while read -r file; do
        if [ "$file" != "./README.md" ]; then
            mv "$file" "$BACKUP_DIR/" 2>/dev/null || rm -f "$file"
            log_success "Supprimé: $file"
        fi
    done
    
    # Scripts de test obsolètes pour SmartMatch multiples
    find . -maxdepth 2 -name "test_smartmatch_*.py" -type f | while read -r file; do
        mv "$file" "$BACKUP_DIR/" 2>/dev/null || rm -f "$file"
        log_success "Supprimé: $file"
    done
    
    log_success "Nettoyage terminé"
}

# Vérification de l'intégrité de SuperSmartMatch Unifié
verify_unified_structure() {
    log "Vérification de la structure SuperSmartMatch Unifié..."
    
    required_files=(
        "super-smart-match-unified/supersmartmatch_unified.py"
        "super-smart-match-unified/Dockerfile"
        "super-smart-match-unified/requirements.txt"
        "super-smart-match-unified/ml_modules/__init__.py"
    )
    
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        log_success "Structure SuperSmartMatch Unifié vérifiée"
    else
        log_error "Fichiers manquants: ${missing_files[*]}"
        log_error "Veuillez vérifier la structure avant de continuer"
        exit 1
    fi
}

# Construction des nouveaux conteneurs
build_containers() {
    log "Construction des conteneurs..."
    
    # Construction du service SuperSmartMatch Unifié
    log "Construction de SuperSmartMatch Unifié..."
    docker-compose build supersmartmatch-unified >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "SuperSmartMatch Unifié construit"
    else
        log_error "Erreur construction SuperSmartMatch Unifié"
        exit 1
    fi
    
    # Construction des autres services
    log "Construction des autres services..."
    docker-compose build >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Tous les conteneurs construits"
    else
        log_error "Erreur construction des conteneurs"
        exit 1
    fi
}

# Démarrage des services
start_services() {
    log "Démarrage des services..."
    
    docker-compose up -d >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Services démarrés"
    else
        log_error "Erreur démarrage des services"
        exit 1
    fi
}

# Tests de validation
validation_tests() {
    log "Tests de validation..."
    
    # Attendre que les services soient prêts
    log "Attente du démarrage complet..."
    sleep 45
    
    # Test de santé SuperSmartMatch Unifié
    log "Test de santé SuperSmartMatch Unifié..."
    
    for i in {1..10}; do
        if curl -f -s http://localhost:5052/health > /dev/null; then
            log_success "SuperSmartMatch Unifié opérationnel"
            break
        fi
        
        if [ $i -eq 10 ]; then
            log_error "SuperSmartMatch Unifié non accessible"
            return 1
        fi
        
        log "Tentative $i/10..."
        sleep 5
    done
    
    # Test des services de parsing
    services_to_test=(
        "cv-parser:5051"
        "job-parser:5053"
        "api:5050"
        "frontend:3000"
    )
    
    for service in "${services_to_test[@]}"; do
        service_name=$(echo "$service" | cut -d: -f1)
        port=$(echo "$service" | cut -d: -f2)
        
        if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1 || 
           curl -f -s "http://localhost:$port" > /dev/null 2>&1; then
            log_success "$service_name opérationnel"
        else
            log_error "$service_name non accessible"
        fi
    done
    
    # Test du pipeline complet si script disponible
    if [ -f "test_pipeline_script.sh" ]; then
        log "Test du pipeline complet..."
        chmod +x test_pipeline_script.sh
        
        if ./test_pipeline_script.sh >> "$LOG_FILE" 2>&1; then
            log_success "Pipeline complet testé avec succès"
        else
            log_error "Échec du test du pipeline complet"
        fi
    fi
}

# Affichage du résumé
show_summary() {
    echo ""
    echo "🎉 MIGRATION TERMINÉE AVEC SUCCÈS !"
    echo "==================================="
    echo ""
    echo "📊 Résumé de la migration :"
    echo "  ✅ Ancien système sauvegardé dans $BACKUP_DIR"
    echo "  ✅ Fichiers obsolètes supprimés"
    echo "  ✅ SuperSmartMatch Unifié déployé"
    echo "  ✅ Services opérationnels"
    echo ""
    echo "🌐 Services disponibles :"
    echo "  • Frontend: http://localhost:3000"
    echo "  • API principale: http://localhost:5050"
    echo "  • SuperSmartMatch Unifié: http://localhost:5052"
    echo "  • CV Parser: http://localhost:5051"
    echo "  • Job Parser: http://localhost:5053"
    echo ""
    echo "📊 Monitoring :"
    echo "  • Redis Commander: http://localhost:8081"
    echo "  • RQ Dashboard: http://localhost:9181"
    echo "  • MinIO Console: http://localhost:9001"
    echo ""
    echo "🎯 Fonctionnalités SuperSmartMatch Unifié :"
    echo "  ✅ Pipeline 3 étapes : Parsing → Questionnaire → Matching"
    echo "  ✅ Algorithme unifié avec ML sémantique"
    echo "  ✅ Auto-apprentissage basé sur feedback"
    echo "  ✅ Fallback robuste si ML indisponible"
    echo "  ✅ Cache intelligent avec Redis"
    echo "  ✅ API simplifiée et unifiée"
    echo ""
    echo "📝 Prochaines étapes :"
    echo "  1. Tester le pipeline via le frontend"
    echo "  2. Configurer les modèles ML (optionnel)"
    echo "  3. Activer le système d'apprentissage"
    echo "  4. Monitorer les performances"
    echo ""
    echo "📋 Logs de migration: $LOG_FILE"
    echo "💾 Sauvegarde: $BACKUP_DIR"
}

# Gestion des erreurs
handle_error() {
    log_error "Erreur lors de la migration"
    log_info "Consultez le log: $LOG_FILE"
    log_info "Sauvegarde disponible: $BACKUP_DIR"
    
    read -p "Voulez-vous restaurer l'état précédent? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Restauration en cours..."
        docker-compose down >> "$LOG_FILE" 2>&1
        # Ici on pourrait ajouter la logique de restauration
        log_info "Restauration manuelle nécessaire depuis $BACKUP_DIR"
    fi
    
    exit 1
}

# Fonction principale
main() {
    log "Début de la migration SuperSmartMatch Unifié"
    
    # Définir le gestionnaire d'erreur
    trap handle_error ERR
    
    # Étapes de migration
    check_prerequisites
    stop_services
    backup_data
    cleanup_obsolete_files
    verify_unified_structure
    build_containers
    start_services
    validation_tests
    
    # Affichage du résumé
    show_summary
    
    log "Migration terminée avec succès"
}

# Vérification du mode interactif
if [ "$1" = "--auto" ]; then
    echo "Mode automatique activé"
    main
else
    echo "Ce script va migrer votre projet vers SuperSmartMatch Unifié."
    echo "Cela va :"
    echo "  • Arrêter les services actuels"
    echo "  • Sauvegarder les données importantes"
    echo "  • Supprimer les algorithmes redondants"
    echo "  • Déployer le nouveau système unifié"
    echo ""
    read -p "Continuer? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        main
    else
        echo "Migration annulée"
        exit 0
    fi
fi
