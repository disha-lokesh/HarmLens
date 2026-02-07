#!/bin/bash

# HarmLens Blockchain Integration - Installation Script
# This script installs all dependencies and sets up the environment

set -e  # Exit on error

echo "=============================================="
echo "HarmLens Blockchain Integration Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo -e "${GREEN}✓${NC} Python $python_version found"
else
    echo -e "${RED}✗${NC} Python 3.8+ required, found $python_version"
    exit 1
fi

# Check Node.js (for IPFS)
echo ""
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $node_version found"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found (optional, needed for IPFS)"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo -e "${GREEN}✓${NC} Python dependencies installed"

# Check for Ganache
echo ""
echo "Checking for Ganache..."
if command -v ganache &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ganache found"
else
    echo -e "${YELLOW}⚠${NC} Ganache not found"
    read -p "Install Ganache globally? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install -g ganache
        echo -e "${GREEN}✓${NC} Ganache installed"
    else
        echo "Skipping Ganache installation"
    fi
fi

# Check for IPFS
echo ""
echo "Checking for IPFS..."
if command -v ipfs &> /dev/null; then
    ipfs_version=$(ipfs --version)
    echo -e "${GREEN}✓${NC} $ipfs_version found"
else
    echo -e "${YELLOW}⚠${NC} IPFS not found"
    echo "Install IPFS:"
    echo "  macOS: brew install ipfs"
    echo "  Linux: https://docs.ipfs.tech/install/"
fi

# Create environment file
echo ""
echo "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file"
    echo -e "${YELLOW}⚠${NC} Remember to update .env with your keys!"
else
    echo -e "${YELLOW}⚠${NC} .env file already exists, skipping"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p blockchain_sim
mkdir -p contracts
echo -e "${GREEN}✓${NC} Directories created"

# Run tests
echo ""
echo "Running integration tests..."
python3 test_blockchain_integration.py

# Summary
echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start local blockchain (optional):"
echo "   ${GREEN}ganache --deterministic${NC}"
echo ""
echo "2. Start IPFS daemon (optional):"
echo "   ${GREEN}ipfs daemon${NC}"
echo ""
echo "3. Deploy smart contract (optional):"
echo "   ${GREEN}python3 blockchain_setup.py${NC}"
echo ""
echo "4. Start API server:"
echo "   ${GREEN}python3 api_server.py${NC}"
echo ""
echo "5. Run demo:"
echo "   ${GREEN}python3 examples/blockchain_example.py${NC}"
echo ""
echo "Documentation:"
echo "  • Quick Start: QUICKSTART_BLOCKCHAIN.md"
echo "  • Full Guide: BLOCKCHAIN_GUIDE.md"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "=============================================="
