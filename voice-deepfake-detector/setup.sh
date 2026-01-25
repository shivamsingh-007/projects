#!/bin/bash

# Voice Deepfake Detector - Setup Script
# This script sets up the entire application with one command

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Header
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Voice Deepfake Detector - Setup         ║${NC}"
echo -e "${CYAN}║   AI-Powered Audio Authentication          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION found"

# Check pip
print_info "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi
print_success "pip3 found"

# Create virtual environment (optional but recommended)
print_info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Install Python dependencies
print_info "Installing backend dependencies..."
cd backend

# Try to install with TensorFlow first
pip install --upgrade pip
if pip install -r requirements.txt 2>/dev/null; then
    print_success "Backend dependencies installed (with TensorFlow)"
else
    print_warning "TensorFlow installation failed - using lightweight version"
    print_info "Installing lightweight dependencies..."
    pip install -r requirements-lite.txt
    if [ $? -eq 0 ]; then
        print_success "Lightweight dependencies installed (without TensorFlow)"
        print_info "The app will use Random Forest instead of CNN"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Initialize model
print_info "Initializing ML model..."
python3 -c "from model import DeepfakeDetector; detector = DeepfakeDetector(); print('Model initialized successfully')"
print_success "ML model initialized"

cd ..

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_info "Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_info "Detected Linux"
fi

# Setup complete
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Setup Complete! 🎉               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

print_info "To start the application, run:"
echo -e "${CYAN}  ./start.sh${NC}"
echo ""
print_info "Or manually start components:"
echo -e "${CYAN}  Backend:  cd backend && python3 app.py${NC}"
echo -e "${CYAN}  Frontend: cd frontend && python3 -m http.server 3000${NC}"
echo ""

print_warning "Note: The model is initialized with random weights."
print_warning "For production use, train the model on real datasets:"
print_warning "  - ASVspoof 2019"
print_warning "  - FakeAVCeleb"
print_warning "  - WaveFake"
echo ""
