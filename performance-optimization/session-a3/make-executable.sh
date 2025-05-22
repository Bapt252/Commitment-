#!/bin/bash

# Make all Session A3 scripts executable
# One-time setup script

echo "🔧 Making all Session A3 scripts executable..."

chmod +x baseline-profiling.sh
chmod +x database-optimization.sh  
chmod +x redis-optimization.sh
chmod +x docker-optimization.sh
chmod +x code-optimization.sh
chmod +x validation-final.sh
chmod +x session-a3-master.sh
chmod +x monitor-performance.sh
chmod +x check-validation-status.sh
chmod +x session-a3-guide.sh
chmod +x quick-commands.sh

echo "✅ All Session A3 scripts are now executable!"
echo ""
echo "Available scripts:"
echo "  ./session-a3-guide.sh status      - Quick status check"
echo "  ./check-validation-status.sh     - Validation progress"
echo "  ./quick-commands.sh              - Rapid status & commands"
echo "  ./validation-final.sh            - Final validation (if needed)"
echo "  ./monitor-performance.sh         - Performance monitoring"
