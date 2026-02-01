#!/bin/bash
# TikTok Viral Script Generator - Start Script

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════╗"
echo "║  TikTok Viral Script Generator v1.0   ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo -e "${CYAN}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Run the server
echo -e "${GREEN}Starting server on http://localhost:8080${NC}"
echo -e "${CYAN}Press Ctrl+C to stop${NC}"
echo ""

PYTHONPATH=. uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
