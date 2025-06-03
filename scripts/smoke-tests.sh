#!/bin/bash
set -euo pipefail

VERSION="${1:-all}"
BASE_URL="${2:-http://localhost}"

log() { echo -e "\033[0;34m[$(date +'%H:%M:%S')]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[$(date +'%H:%M:%S')] ✅ $1\033[0m"; }
log_error() { echo -e "\033[0;31m[$(date +'%H:%M:%S')] ❌ $1\033[0m"; }

test_version() {
    local v="$1"
    log "🧪 Test $v..."
    
    if curl -sf "$BASE_URL/health/$v" > /dev/null; then
        log_success "$v health OK"
    else
        log_error "$v health FAIL"
        return 1
    fi
}

if [[ "$VERSION" == "all" ]]; then
    test_version "v1"
    test_version "v2"
    curl -sf "$BASE_URL/health" > /dev/null && log_success "Load balancer OK"
else
    test_version "$VERSION"
fi

log_success "🎉 Tests terminés"
