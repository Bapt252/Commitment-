#!/bin/bash

# 🚀 SuperSmartMatch V2 - Quick Deployment Script
# Production-ready deployment for SuperSmartMatch V2 service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SuperSmartMatch V2 - Quick Deployment${NC}"
echo "========================================"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}🔄 Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts - waiting for $service_name...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $max_attempts attempts${NC}"
    return 1
}

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies check passed${NC}"

# Check port availability
echo -e "${BLUE}🔍 Checking port availability...${NC}"
if ! check_port 5070; then
    echo -e "${RED}❌ Port 5070 (SuperSmartMatch V2) is already in use${NC}"
    echo -e "${YELLOW}💡 Kill the process using: sudo lsof -ti:5070 | xargs kill -9${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Port 5070 is available${NC}"

# Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p cache

# Environment setup
echo -e "${BLUE}⚙️  Setting up environment...${NC}"
export ENVIRONMENT=development
export NEXTEN_MATCHER_URL=http://localhost:5052
export V1_ALGORITHMS_URL=http://localhost:5062
export REDIS_URL=redis://localhost:6379/0

# Start Redis if not running
echo -e "${BLUE}🔄 Checking Redis...${NC}"
if ! pgrep redis-server > /dev/null; then
    echo -e "${YELLOW}⚠️  Redis not running, attempting to start...${NC}"
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes --port 6379
        sleep 2
        echo -e "${GREEN}✅ Redis started successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis not installed, running without cache${NC}"
    fi
else
    echo -e "${GREEN}✅ Redis is already running${NC}"
fi

# Start SuperSmartMatch V2
echo -e "${BLUE}🚀 Starting SuperSmartMatch V2 on port 5070...${NC}"

# Background startup
nohup python main.py > logs/supersmartmatch-v2.log 2>&1 &
SSM_PID=$!

echo -e "${GREEN}🎯 SuperSmartMatch V2 started with PID: $SSM_PID${NC}"

# Wait for service to be ready
if wait_for_service "http://localhost:5070/health" "SuperSmartMatch V2"; then
    echo ""
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo "========================================"
    echo -e "${BLUE}📊 Service Information:${NC}"
    echo "   🔗 SuperSmartMatch V2: http://localhost:5070"
    echo "   📚 API Documentation: http://localhost:5070/api/docs"  
    echo "   💚 Health Check: http://localhost:5070/health"
    echo "   📊 Statistics: http://localhost:5070/stats"
    echo ""
    echo -e "${BLUE}🧪 Quick Test Commands:${NC}"
    echo "   curl http://localhost:5070/health"
    echo "   curl http://localhost:5070/stats"
    echo ""
    echo -e "${BLUE}📋 Process Management:${NC}"
    echo "   Stop: kill $SSM_PID"
    echo "   Logs: tail -f logs/supersmartmatch-v2.log"
    echo ""
    echo -e "${YELLOW}💡 Note: Make sure your V1 services are running on ports 5052 and 5062${NC}"
    echo -e "${YELLOW}   for full algorithm selection functionality${NC}"
    
else
    echo -e "${RED}❌ DEPLOYMENT FAILED!${NC}"
    echo "Check logs: tail -f logs/supersmartmatch-v2.log"
    kill $SSM_PID 2>/dev/null || true
    exit 1
fi
