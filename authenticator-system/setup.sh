#!/bin/bash

# OTP Authenticator System - Quick Start Script
# This script helps you set up the system quickly

echo "=========================================="
echo "  OTP Authenticator System - Quick Start"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js v18 or higher from https://nodejs.org"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node -v) detected${NC}"

# Check if MongoDB is running (for local setup)
if command -v mongod &> /dev/null; then
    echo -e "${GREEN}✓ MongoDB detected${NC}"
else
    echo -e "${YELLOW}⚠ MongoDB not detected locally. You can use MongoDB Atlas instead.${NC}"
fi

echo ""
echo "=========================================="
echo "  Setting up Backend"
echo "=========================================="
echo ""

cd backend || exit

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp ../.env.example .env
    echo -e "${YELLOW}⚠ Please edit backend/.env with your credentials:${NC}"
    echo "  - MongoDB URI"
    echo "  - JWT Secret"
    echo "  - Gmail credentials"
    echo "  - Twilio credentials"
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

# Install backend dependencies
echo "Installing backend dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Setting up Frontend"
echo "=========================================="
echo ""

cd ../frontend || exit

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
    exit 1
fi

cd ..

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  npm start"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
echo -e "${GREEN}✓ Ready to go!${NC}"
echo ""
