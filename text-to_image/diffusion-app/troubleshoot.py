#!/usr/bin/env python3
"""
AI Image Generator - Automated Troubleshooting & Error Solver
This script diagnoses and fixes common issues automatically
"""

import os
import sys
import subprocess
import json
import time
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_fix(msg: str):
    print(f"{Colors.MAGENTA}🔧 {msg}{Colors.END}")

def run_command(cmd: str, capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_docker_installed() -> bool:
    """Check if Docker is installed"""
    print_info("Checking Docker installation...")
    code, stdout, stderr = run_command("docker --version")
    
    if code == 0:
        print_success(f"Docker is installed: {stdout.strip()}")
        return True
    else:
        print_error("Docker is not installed or not in PATH")
        return False

def fix_docker_not_installed():
    """Provide instructions to install Docker"""
    print_fix("Docker Installation Instructions:")
    
    system = platform.system()
    
    if system == "Linux":
        print("\nFor Ubuntu/Debian:")
        print("  curl -fsSL https://get.docker.com -o get-docker.sh")
        print("  sudo sh get-docker.sh")
        print("  sudo usermod -aG docker $USER")
        print("  newgrp docker")
        
    elif system == "Darwin":
        print("\nFor macOS:")
        print("  Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
        print("  Or install via Homebrew:")
        print("  brew install --cask docker")
        
    elif system == "Windows":
        print("\nFor Windows:")
        print("  Download Docker Desktop from: https://www.docker.com/products/docker-desktop")
        print("  Make sure WSL 2 is enabled")
    
    print("\nAfter installation, run this script again.")

def check_docker_running() -> bool:
    """Check if Docker daemon is running"""
    print_info("Checking if Docker daemon is running...")
    code, stdout, stderr = run_command("docker ps")
    
    if code == 0:
        print_success("Docker daemon is running")
        return True
    else:
        print_error("Docker daemon is not running")
        return False

def fix_docker_not_running():
    """Try to start Docker daemon"""
    print_fix("Attempting to start Docker daemon...")
    
    system = platform.system()
    
    if system == "Linux":
        print_info("Trying to start Docker with systemctl...")
        code, _, _ = run_command("sudo systemctl start docker")
        if code == 0:
            print_success("Docker daemon started successfully")
            time.sleep(2)
            return True
        else:
            print_warning("Failed to start Docker daemon")
            print("Please start Docker manually:")
            print("  sudo systemctl start docker")
            
    elif system in ["Darwin", "Windows"]:
        print_warning("Please start Docker Desktop manually")
        print("Then run this script again")
    
    return False

def check_disk_space() -> bool:
    """Check if there's enough disk space"""
    print_info("Checking available disk space...")
    
    try:
        stat = os.statvfs('.')
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        
        if free_gb >= 20:
            print_success(f"Sufficient disk space: {free_gb:.1f} GB available")
            return True
        else:
            print_error(f"Insufficient disk space: only {free_gb:.1f} GB available (need 20+ GB)")
            return False
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
        return True  # Assume OK

def fix_disk_space():
    """Provide instructions to free up disk space"""
    print_fix("To free up disk space:")
    print("\n1. Remove unused Docker images and containers:")
    print("   docker system prune -a --volumes")
    print("\n2. Clean up system cache:")
    print("   - Linux: sudo apt-get clean && sudo apt-get autoclean")
    print("   - macOS: Clean Downloads, clear cache folders")
    print("   - Windows: Run Disk Cleanup utility")
    print("\n3. Move or delete large files")

def check_port_available(port: int = 8000) -> bool:
    """Check if port is available"""
    print_info(f"Checking if port {port} is available...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    
    if result != 0:
        print_success(f"Port {port} is available")
        return True
    else:
        print_error(f"Port {port} is already in use")
        return False

def fix_port_in_use(port: int = 8000):
    """Fix port conflict"""
    print_fix(f"Port {port} is in use. Options:")
    
    print("\n1. Find and stop the process using the port:")
    system = platform.system()
    
    if system == "Linux" or system == "Darwin":
        print(f"   lsof -i :{port}")
        print(f"   kill -9 <PID>")
    elif system == "Windows":
        print(f"   netstat -ano | findstr :{port}")
        print(f"   taskkill /PID <PID> /F")
    
    print("\n2. Use a different port:")
    print("   docker run -p 8080:8000 ... ai-image-generator")
    print("   Then access at http://localhost:8080")

def check_container_exists() -> bool:
    """Check if container exists"""
    print_info("Checking for existing container...")
    code, stdout, _ = run_command("docker ps -a --filter name=ai-image-generator --format '{{.Names}}'")
    
    if code == 0 and "ai-image-generator" in stdout:
        print_warning("Container 'ai-image-generator' already exists")
        return True
    else:
        print_success("No conflicting container found")
        return False

def fix_container_exists():
    """Remove existing container"""
    print_fix("Removing existing container...")
    
    response = input("Remove existing container? (y/n): ").lower()
    if response == 'y':
        code, _, _ = run_command("docker rm -f ai-image-generator")
        if code == 0:
            print_success("Container removed successfully")
            return True
        else:
            print_error("Failed to remove container")
            print("Try manually: docker rm -f ai-image-generator")
            return False
    return False

def check_image_exists() -> bool:
    """Check if Docker image exists"""
    print_info("Checking if Docker image exists...")
    code, stdout, _ = run_command("docker images ai-image-generator --format '{{.Repository}}'")
    
    if code == 0 and "ai-image-generator" in stdout:
        print_success("Docker image 'ai-image-generator' exists")
        return True
    else:
        print_warning("Docker image 'ai-image-generator' not found")
        return False

def fix_image_not_exists():
    """Build Docker image"""
    print_fix("Building Docker image...")
    
    if not Path("Dockerfile").exists():
        print_error("Dockerfile not found in current directory")
        print("Please run this script from the diffusion-app directory")
        return False
    
    response = input("Build Docker image now? This may take 5-10 minutes. (y/n): ").lower()
    if response == 'y':
        print_info("Building image... (this may take a while)")
        code, stdout, stderr = run_command("docker build -t ai-image-generator .", capture_output=False)
        
        if code == 0:
            print_success("Image built successfully")
            return True
        else:
            print_error("Image build failed")
            print("Check the output above for errors")
            return False
    return False

def check_container_running() -> bool:
    """Check if container is running"""
    print_info("Checking if container is running...")
    code, stdout, _ = run_command("docker ps --filter name=ai-image-generator --format '{{.Names}}'")
    
    if code == 0 and "ai-image-generator" in stdout:
        print_success("Container is running")
        return True
    else:
        print_warning("Container is not running")
        return False

def fix_container_not_running():
    """Start the container"""
    print_fix("Starting container...")
    
    # Check if container exists but is stopped
    code, stdout, _ = run_command("docker ps -a --filter name=ai-image-generator --format '{{.Names}}'")
    
    if "ai-image-generator" in stdout:
        # Container exists, just start it
        code, _, _ = run_command("docker start ai-image-generator")
        if code == 0:
            print_success("Container started successfully")
            return True
    else:
        # Need to create and run container
        print_info("Container doesn't exist. Creating new container...")
        
        # Check for GPU
        gpu_available = check_gpu_available()
        
        if gpu_available:
            cmd = "docker run -d --name ai-image-generator --gpus all -p 8000:8000 -v $(pwd)/models:/app/models --restart unless-stopped ai-image-generator"
        else:
            cmd = "docker run -d --name ai-image-generator -p 8000:8000 -v $(pwd)/models:/app/models --restart unless-stopped ai-image-generator"
        
        print_info(f"Running: {cmd}")
        code, _, stderr = run_command(cmd)
        
        if code == 0:
            print_success("Container created and started successfully")
            return True
        else:
            print_error(f"Failed to start container: {stderr}")
            return False
    
    return False

def check_gpu_available() -> bool:
    """Check if NVIDIA GPU is available"""
    print_info("Checking for NVIDIA GPU...")
    code, stdout, _ = run_command("nvidia-smi")
    
    if code == 0:
        print_success("NVIDIA GPU detected")
        return True
    else:
        print_warning("No NVIDIA GPU detected or nvidia-smi not available")
        print_info("Application will run on CPU (slower)")
        return False

def check_nvidia_docker() -> bool:
    """Check if nvidia-docker runtime is available"""
    if not check_gpu_available():
        return False
    
    print_info("Checking for NVIDIA Docker runtime...")
    code, stdout, _ = run_command("docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi")
    
    if code == 0:
        print_success("NVIDIA Docker runtime is working")
        return True
    else:
        print_warning("NVIDIA Docker runtime not available")
        return False

def fix_nvidia_docker():
    """Provide instructions to install NVIDIA Docker"""
    print_fix("To install NVIDIA Docker runtime:")
    print("\nFor Ubuntu/Debian:")
    print("  distribution=$(. /etc/os-release;echo $ID$VERSION_ID)")
    print("  curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -")
    print("  curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list")
    print("  sudo apt-get update && sudo apt-get install -y nvidia-docker2")
    print("  sudo systemctl restart docker")
    print("\nFor other distributions, see: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html")

def check_application_health() -> bool:
    """Check if application is responding"""
    print_info("Checking application health...")
    
    import urllib.request
    import urllib.error
    
    try:
        response = urllib.request.urlopen('http://localhost:8000/health', timeout=10)
        data = json.loads(response.read().decode())
        
        if data.get('status') == 'healthy':
            print_success("Application is healthy")
            print_info(f"  - Device: {data.get('device', 'unknown')}")
            print_info(f"  - Model loaded: {data.get('model_loaded', False)}")
            return True
        else:
            print_warning(f"Application status: {data.get('status', 'unknown')}")
            return False
            
    except urllib.error.URLError:
        print_error("Cannot connect to application at http://localhost:8000")
        return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def check_container_logs():
    """Check container logs for errors"""
    print_info("Checking container logs for errors...")
    
    code, stdout, _ = run_command("docker logs --tail 50 ai-image-generator")
    
    if code == 0:
        errors = []
        warnings = []
        
        for line in stdout.split('\n'):
            lower_line = line.lower()
            if 'error' in lower_line or 'exception' in lower_line or 'failed' in lower_line:
                errors.append(line)
            elif 'warning' in lower_line or 'warn' in lower_line:
                warnings.append(line)
        
        if errors:
            print_error(f"Found {len(errors)} error(s) in logs:")
            for error in errors[:5]:  # Show first 5
                print(f"  {error}")
        
        if warnings:
            print_warning(f"Found {len(warnings)} warning(s) in logs")
        
        if not errors and not warnings:
            print_success("No errors or warnings found in recent logs")
        
        return len(errors) == 0
    else:
        print_error("Could not retrieve container logs")
        return False

def diagnose_common_errors():
    """Diagnose common error patterns from logs"""
    print_info("Diagnosing common error patterns...")
    
    code, stdout, _ = run_command("docker logs --tail 100 ai-image-generator")
    
    if code != 0:
        return
    
    logs_lower = stdout.lower()
    
    # CUDA out of memory
    if 'cuda out of memory' in logs_lower or 'out of memory' in logs_lower:
        print_error("CUDA out of memory detected")
        print_fix("Solutions:")
        print("  1. Reduce image resolution (use 256x256 or 384x384)")
        print("  2. Reduce inference steps (use 20-25 instead of 30+)")
        print("  3. Run on CPU instead:")
        print("     docker stop ai-image-generator")
        print("     docker rm ai-image-generator")
        print("     docker run -d -p 8000:8000 --name ai-image-gen ai-image-generator")
    
    # Model download issues
    if 'connection' in logs_lower and 'huggingface' in logs_lower:
        print_error("Model download connection issues detected")
        print_fix("Solutions:")
        print("  1. Check internet connection")
        print("  2. Wait and retry (downloads can be slow)")
        print("  3. Set up HuggingFace token if needed")
    
    # Port binding issues
    if 'address already in use' in logs_lower:
        print_error("Port binding issue detected")
        print_fix("Port 8000 is already in use. Use a different port:")
        print("  docker run -p 8080:8000 ... ai-image-generator")
    
    # Permission issues
    if 'permission denied' in logs_lower:
        print_error("Permission issues detected")
        print_fix("Solutions:")
        print("  1. Run Docker commands with sudo")
        print("  2. Add user to docker group:")
        print("     sudo usermod -aG docker $USER")
        print("     newgrp docker")

def full_diagnostic():
    """Run complete diagnostic check"""
    print_header("🔍 Running Full System Diagnostic")
    
    issues = []
    
    # Check Docker installation
    if not check_docker_installed():
        issues.append(("Docker not installed", fix_docker_not_installed))
    
    # Check Docker running
    if not check_docker_running():
        issues.append(("Docker not running", fix_docker_not_running))
    
    # Check disk space
    if not check_disk_space():
        issues.append(("Insufficient disk space", fix_disk_space))
    
    # Check port availability
    if not check_port_available():
        issues.append(("Port 8000 in use", lambda: fix_port_in_use(8000)))
    
    # Check for existing container
    if check_container_exists():
        issues.append(("Container already exists", fix_container_exists))
    
    # Check image exists
    if not check_image_exists():
        issues.append(("Docker image not built", fix_image_not_exists))
    
    # Check GPU
    gpu_available = check_gpu_available()
    if gpu_available:
        if not check_nvidia_docker():
            issues.append(("NVIDIA Docker runtime not available", fix_nvidia_docker))
    
    # Check container running
    if not check_container_running():
        issues.append(("Container not running", fix_container_not_running))
    
    # Check application health
    if not check_application_health():
        check_container_logs()
        diagnose_common_errors()
    
    return issues

def auto_fix_issues(issues: List[Tuple]):
    """Automatically fix detected issues"""
    print_header("🔧 Auto-Fix Detected Issues")
    
    if not issues:
        print_success("No issues detected!")
        return
    
    print_info(f"Found {len(issues)} issue(s)")
    print()
    
    for i, (description, fix_func) in enumerate(issues, 1):
        print(f"{i}. {description}")
    
    print()
    response = input("Attempt to auto-fix these issues? (y/n): ").lower()
    
    if response == 'y':
        for description, fix_func in issues:
            print(f"\n{Colors.BOLD}Fixing: {description}{Colors.END}")
            try:
                fix_func()
            except Exception as e:
                print_error(f"Auto-fix failed: {e}")
            print()

def interactive_troubleshoot():
    """Interactive troubleshooting menu"""
    while True:
        print_header("🛠️  Interactive Troubleshooter")
        print("1. Run full diagnostic")
        print("2. Check Docker installation")
        print("3. Check container status")
        print("4. View container logs")
        print("5. Restart container")
        print("6. Rebuild image")
        print("7. Check GPU availability")
        print("8. Clean up Docker resources")
        print("9. Test API health")
        print("0. Exit")
        print()
        
        choice = input("Select option: ").strip()
        print()
        
        if choice == '1':
            issues = full_diagnostic()
            auto_fix_issues(issues)
        
        elif choice == '2':
            if check_docker_installed() and check_docker_running():
                print_success("Docker is properly installed and running")
            else:
                print_error("Docker issues detected")
        
        elif choice == '3':
            check_container_running()
            check_container_logs()
        
        elif choice == '4':
            print_info("Container logs (last 50 lines):")
            code, stdout, _ = run_command("docker logs --tail 50 ai-image-generator", capture_output=False)
        
        elif choice == '5':
            print_info("Restarting container...")
            run_command("docker restart ai-image-generator", capture_output=False)
            print_success("Container restarted")
        
        elif choice == '6':
            print_warning("This will rebuild the Docker image (may take 5-10 minutes)")
            response = input("Continue? (y/n): ").lower()
            if response == 'y':
                run_command("docker build -t ai-image-generator .", capture_output=False)
        
        elif choice == '7':
            if check_gpu_available():
                check_nvidia_docker()
            else:
                print_info("No GPU available - application will use CPU")
        
        elif choice == '8':
            print_warning("This will remove all stopped containers and unused images")
            response = input("Continue? (y/n): ").lower()
            if response == 'y':
                run_command("docker system prune -f", capture_output=False)
                print_success("Cleanup complete")
        
        elif choice == '9':
            check_application_health()
        
        elif choice == '0':
            print_info("Exiting troubleshooter")
            break
        
        else:
            print_error("Invalid option")
        
        print()
        input("Press Enter to continue...")
        print("\n" * 2)

def main():
    """Main entry point"""
    print_header("🚀 AI Image Generator - Troubleshooter & Error Solver")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--auto':
            # Auto mode: diagnose and fix
            issues = full_diagnostic()
            auto_fix_issues(issues)
        elif sys.argv[1] == '--check':
            # Check mode: diagnose only
            full_diagnostic()
        else:
            print("Usage:")
            print("  python troubleshoot.py           # Interactive mode")
            print("  python troubleshoot.py --auto    # Auto-diagnose and fix")
            print("  python troubleshoot.py --check   # Diagnose only")
    else:
        # Interactive mode
        interactive_troubleshoot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
