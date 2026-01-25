#!/bin/bash

# Voice Deepfake Detector - Start Script
# Starts both backend and frontend servers

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Header
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Voice Deepfake Detector - Starting      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if setup has been run
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "Servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
print_info "Starting backend server on http://localhost:5000..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..
sleep 2
print_success "Backend server started (PID: $BACKEND_PID)"

# Start frontend
print_info "Starting frontend server on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..
sleep 1
print_success "Frontend server started (PID: $FRONTEND_PID)"

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Application Running Successfully! 🚀   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
print_info "Access the application at:"
echo -e "${CYAN}  🌐 http://localhost:3000${NC}"
echo ""
print_info "Backend API available at:"
echo -e "${CYAN}  🔌 http://localhost:5000${NC}"
echo ""
print_warning "Press Ctrl+C to stop both servers"
echo ""

# Wait for processes
wait
