#!/bin/bash
# TUKUB AI - One-Command Installer

set -e

echo "=========================================="
echo "TUKUB AI - Security Testing Framework"
echo "=========================================="
echo "WARNING: Only install on systems you own"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        echo -e "${RED}Unsupported OS${NC}"
        exit 1
    fi
    echo -e "${GREEN}Detected OS: $OS${NC}"
}

# Install dependencies
install_deps() {
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git curl wget
    elif [[ "$OS" == "macos" ]]; then
        brew update
        brew install python3 git curl wget
    fi
}

# Install Ollama
install_ollama() {
    echo -e "${YELLOW}Installing Ollama...${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    elif [[ "$OS" == "macos" ]]; then
        brew install ollama
    fi
    
    ollama serve &
    sleep 3
    ollama pull llama3.2
}

# Setup Python environment
setup_env() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    
    mkdir -p ~/.tukub
    python3 -m venv ~/.tukub/venv
    source ~/.tukub/venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Main
main() {
    detect_os
    install_deps
    install_ollama
    setup_env
    
    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}TUKUB AI Installation Complete!${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo "Quick Start:"
    echo "  source ~/.tukub/venv/bin/activate"
    echo "  python main.py --help"
    echo ""
    echo -e "${RED}AUTHORIZED USE ONLY${NC}"
}

main