# 🛠️ Troubleshooting Guide & Error Solutions

Complete guide to diagnosing and fixing all common issues with the AI Image Generator.

---

## 🚀 Quick Fix Tool

We've included an **automated troubleshooting script** that can diagnose and fix most issues automatically:

```bash
# Interactive mode (recommended)
python troubleshoot.py

# Auto-diagnose and fix
python troubleshoot.py --auto

# Diagnose only (no fixes)
python troubleshoot.py --check
```

**The script can automatically detect and fix:**
- Docker installation issues
- Container conflicts
- Port conflicts
- Missing images
- GPU configuration
- Container startup problems
- And more!

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Container Issues](#container-issues)
3. [Performance Issues](#performance-issues)
4. [Generation Issues](#generation-issues)
5. [Network Issues](#network-issues)
6. [GPU Issues](#gpu-issues)
7. [Model Download Issues](#model-download-issues)
8. [API Issues](#api-issues)
9. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## 🔧 Installation Issues

### Docker Not Installed

**Symptoms:**
- `docker: command not found`
- `bash: docker: command not found`

**Solution:**

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# Using Homebrew
brew install --cask docker

# Or download from https://www.docker.com/products/docker-desktop
```

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Enable WSL 2

**Verify:**
```bash
docker --version
```

---

### Docker Daemon Not Running

**Symptoms:**
- `Cannot connect to the Docker daemon`
- `Is the docker daemon running?`

**Solution:**

**Linux:**
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Start on boot
```

**macOS/Windows:**
- Start Docker Desktop application

**Verify:**
```bash
docker ps
```

---

### Permission Denied

**Symptoms:**
- `permission denied while trying to connect to the Docker daemon socket`

**Solution:**

**Linux:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes (logout/login or use)
newgrp docker

# Or use sudo (not recommended for regular use)
sudo docker ...
```

**Verify:**
```bash
docker run hello-world
```

---

### Insufficient Disk Space

**Symptoms:**
- `no space left on device`
- Build or download fails

**Solution:**

```bash
# Check available space
df -h

# Clean Docker resources
docker system prune -a --volumes

# Clean apt cache (Ubuntu/Debian)
sudo apt-get clean
sudo apt-get autoclean

# Find large files
du -h --max-depth=1 | sort -hr | head -20
```

**Requirements:**
- Minimum: 20GB free space
- Recommended: 50GB free space

---

## 🐳 Container Issues

### Container Already Exists

**Symptoms:**
- `Conflict. The container name "/ai-image-generator" is already in use`

**Solution:**

```bash
# Option 1: Remove existing container
docker rm -f ai-image-generator

# Option 2: Use a different name
docker run --name my-image-gen ...

# Option 3: Remove and restart
docker rm -f ai-image-generator && docker run ...
```

---

### Container Won't Start

**Symptoms:**
- Container exits immediately
- Status shows "Exited (1)"

**Solution:**

```bash
# Check container logs
docker logs ai-image-generator

# Common fixes based on error:

# If port conflict:
docker run -p 8080:8000 ...  # Use different port

# If permission issues:
sudo docker run ...

# If missing image:
docker build -t ai-image-generator .

# Restart container
docker restart ai-image-generator
```

---

### Container Running but Not Accessible

**Symptoms:**
- Container shows "Up" status
- Cannot access http://localhost:8000

**Solution:**

```bash
# 1. Wait for model to load (first time)
docker logs -f ai-image-generator
# Wait for: "Model loaded successfully"

# 2. Check port binding
docker port ai-image-generator
# Should show: 8000/tcp -> 0.0.0.0:8000

# 3. Check container health
docker inspect ai-image-generator | grep Health -A 10

# 4. Test with curl
curl http://localhost:8000/health

# 5. Check firewall
sudo ufw status  # Linux
# Allow port 8000 if blocked
```

---

### Port Already in Use

**Symptoms:**
- `bind: address already in use`
- `port is already allocated`

**Solution:**

```bash
# Find what's using the port (Linux/Mac)
sudo lsof -i :8000
# Or
sudo netstat -tulpn | grep :8000

# Find what's using the port (Windows)
netstat -ano | findstr :8000

# Option 1: Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# Option 2: Use different port
docker run -p 8080:8000 ... ai-image-generator
# Access at http://localhost:8080
```

---

## ⚡ Performance Issues

### Slow Image Generation (>60s)

**Symptoms:**
- Generation takes more than 60 seconds
- UI freezes during generation

**Diagnosis:**
```bash
# Check if using GPU or CPU
docker logs ai-image-generator | grep "device"

# Check GPU usage (if GPU)
nvidia-smi

# Check CPU usage
docker stats ai-image-generator
```

**Solutions:**

**If on CPU (expected behavior):**
```bash
# Reduce inference steps
# In UI: Set steps to 20-25 instead of 30+

# Reduce resolution
# In UI: Use 256x256 or 384x384 instead of 512x512

# Expected times:
# - 20 steps, 256x256: ~20-30s
# - 25 steps, 512x512: ~40-60s
```

**If on GPU but slow:**
```bash
# Check GPU memory
nvidia-smi

# If out of memory:
# 1. Reduce resolution
# 2. Reduce batch size
# 3. Close other GPU applications

# Restart container
docker restart ai-image-generator
```

---

### High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors

**Solution:**

```bash
# Check memory usage
docker stats ai-image-generator

# Reduce memory footprint:
# 1. Lower image resolution (256x256)
# 2. Reduce inference steps (20-25)
# 3. Close other applications

# Restart Docker
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop
```

---

## 🎨 Generation Issues

### CUDA Out of Memory

**Symptoms:**
- `RuntimeError: CUDA out of memory`
- Generation fails with memory error

**Solution:**

```bash
# Option 1: Reduce settings
# - Use 256x256 or 384x384 resolution
# - Reduce inference steps to 20-25

# Option 2: Run on CPU
docker stop ai-image-generator
docker rm ai-image-generator
docker run -d -p 8000:8000 --name ai-image-gen \
  -v $(pwd)/models:/app/models \
  ai-image-generator  # No --gpus flag

# Option 3: Enable CPU offloading (edit app.py)
# Add: pipe.enable_model_cpu_offload()
```

---

### Images Are Blurry or Low Quality

**Symptoms:**
- Generated images lack detail
- Images look washed out or blurry

**Solution:**

```bash
# Increase inference steps
# In UI: Set to 30-40 steps

# Increase guidance scale
# In UI: Set to 8-12 (default is 7.5)

# Use better prompts
# - Be more specific and detailed
# - Add quality keywords: "highly detailed", "8k", "professional"
# - Use style keywords: "photorealistic", "oil painting", etc.

# Add negative prompts
# Example: "blurry, low quality, distorted, ugly, deformed"

# Use native resolution
# Set to 512x512 (native for SD 2.1)
```

---

### NSFW Content Flagged

**Symptoms:**
- Generation succeeds but image is blank/black
- Response shows `"is_safe": false`

**Solution:**

```bash
# This is the safety filter working correctly

# Option 1: Modify your prompt
# - Remove potentially inappropriate keywords
# - Be more specific and professional

# Option 2: Check logs for details
docker logs ai-image-generator | grep -i nsfw

# Option 3: Disable safety checker (NOT RECOMMENDED)
# Edit app.py and set safety_checker=None
# Only do this for private, controlled use
```

---

### Generation Fails with Error 500

**Symptoms:**
- HTTP 500 Internal Server Error
- Generation request fails

**Solution:**

```bash
# Check container logs
docker logs --tail 50 ai-image-generator

# Common causes and fixes:

# 1. Model not loaded
# Wait longer (first run can take 5-15 minutes)

# 2. Out of memory
# Reduce resolution or use CPU mode

# 3. Invalid parameters
# Check request parameters are within valid ranges

# 4. Restart container
docker restart ai-image-generator
```

---

## 🌐 Network Issues

### Cannot Access Web Interface

**Symptoms:**
- `ERR_CONNECTION_REFUSED`
- Browser can't connect to localhost:8000

**Solution:**

```bash
# 1. Verify container is running
docker ps | grep ai-image-generator

# 2. Check logs for startup errors
docker logs ai-image-generator

# 3. Wait for model to load (first time)
# Look for: "Model loaded successfully in X.XXs"

# 4. Test with curl
curl http://localhost:8000/health

# 5. Check port binding
docker port ai-image-generator

# 6. Try 127.0.0.1 instead of localhost
http://127.0.0.1:8000

# 7. Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# 8. Restart container
docker restart ai-image-generator
```

---

### API Requests Timeout

**Symptoms:**
- Requests hang and timeout
- No response after long wait

**Solution:**

```bash
# 1. Check if model is still loading
docker logs -f ai-image-generator

# 2. Increase client timeout
# For curl: --max-time 120
# For Python requests: timeout=120

# 3. Reduce generation complexity
# - Lower inference steps (20-25)
# - Smaller resolution (256x256)

# 4. Check resource usage
docker stats ai-image-generator
nvidia-smi  # If GPU

# 5. Restart if hung
docker restart ai-image-generator
```

---

## 🎮 GPU Issues

### GPU Not Detected

**Symptoms:**
- Logs show "device: cpu"
- Slow generation times

**Diagnosis:**
```bash
# Check if NVIDIA GPU is available
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Solutions:**

**No nvidia-smi:**
```bash
# Install NVIDIA drivers (Ubuntu)
sudo apt-get update
sudo apt-get install nvidia-driver-535

# Reboot
sudo reboot
```

**nvidia-smi works but Docker doesn't:**
```bash
# Install NVIDIA Container Toolkit (Ubuntu)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Still not working:**
```bash
# Run without GPU (uses CPU)
docker run -d -p 8000:8000 --name ai-image-gen ai-image-generator
```

---

### GPU Out of Memory

**Symptoms:**
- `RuntimeError: CUDA out of memory`
- Generation fails partway through

**Solution:**

```bash
# Check GPU memory
nvidia-smi

# Solutions in order of preference:

# 1. Close other GPU applications
# Check what's using GPU: nvidia-smi
# Kill unnecessary processes

# 2. Reduce generation settings
# - Resolution: 256x256 or 384x384
# - Steps: 20-25
# - Guidance scale: 5-7

# 3. Restart container (clears GPU memory)
docker restart ai-image-generator

# 4. Run on CPU instead
docker stop ai-image-generator
docker rm ai-image-generator
docker run -d -p 8000:8000 ai-image-generator  # No GPU
```

---

## 📥 Model Download Issues

### Model Download Stuck

**Symptoms:**
- Download doesn't progress
- "Downloading..." for very long time

**Solution:**

```bash
# Check logs
docker logs -f ai-image-generator

# Model is ~5GB, download times:
# - 100 Mbps: 5-10 minutes
# - 50 Mbps: 10-20 minutes
# - 10 Mbps: 40-70 minutes

# If truly stuck:

# 1. Check internet connection
ping huggingface.co

# 2. Restart download
docker restart ai-image-generator

# 3. Manual download (advanced)
# Inside container:
docker exec -it ai-image-generator bash
python -c "from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-2-1-base', cache_dir='./models')"
```

---

### Connection Timeout During Download

**Symptoms:**
- `Connection timeout`
- `Failed to download`

**Solution:**

```bash
# 1. Check internet connection
ping -c 5 huggingface.co

# 2. Wait and retry
docker restart ai-image-generator

# 3. Use different DNS
# Edit /etc/docker/daemon.json:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
sudo systemctl restart docker

# 4. Set HuggingFace token (if needed)
# Create token at https://huggingface.co/settings/tokens
export HF_TOKEN=your_token_here
docker run -e HF_TOKEN=$HF_TOKEN ...
```

---

## 🔌 API Issues

### Rate Limit Exceeded (429)

**Symptoms:**
- `HTTP 429: Too Many Requests`
- `Rate limit exceeded`

**Solution:**

```bash
# Default limit: 10 requests per minute

# Option 1: Wait 1 minute
# Limit resets every 60 seconds

# Option 2: Increase rate limit
# Edit app.py:
# RATE_LIMIT_PER_MINUTE = 20  # Increase to 20

# Rebuild and restart:
docker build -t ai-image-generator .
docker restart ai-image-generator

# Option 3: Disable rate limiting (NOT RECOMMENDED)
# Comment out rate limit check in app.py
```

---

### Invalid Request (422)

**Symptoms:**
- `HTTP 422: Unprocessable Entity`
- Validation error

**Solution:**

```bash
# Check parameter ranges:

# Valid ranges:
# - prompt: 1-500 characters
# - negative_prompt: 0-500 characters
# - num_inference_steps: 10-50
# - guidance_scale: 1.0-20.0
# - width/height: 256, 512, or 768
# - seed: 0 to 2^32-1

# Example valid request:
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful landscape",
    "num_inference_steps": 25,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512
  }'
```

---

## 🔍 Advanced Troubleshooting

### Complete Reset

**When nothing else works:**

```bash
# 1. Stop and remove everything
docker stop ai-image-generator
docker rm ai-image-generator
docker rmi ai-image-generator

# 2. Clean Docker system
docker system prune -a --volumes

# 3. Rebuild from scratch
cd diffusion-app
docker build -t ai-image-generator .

# 4. Run fresh container
docker run -d -p 8000:8000 --gpus all \
  --name ai-image-generator \
  -v $(pwd)/models:/app/models \
  ai-image-generator

# 5. Monitor startup
docker logs -f ai-image-generator
```

---

### View All Logs

```bash
# Real-time logs
docker logs -f ai-image-generator

# Last 100 lines
docker logs --tail 100 ai-image-generator

# Since specific time
docker logs --since 30m ai-image-generator

# Save logs to file
docker logs ai-image-generator > app-logs.txt 2>&1
```

---

### Debug Mode

**Enable detailed logging:**

```bash
# Edit app.py, change:
logging.basicConfig(level=logging.DEBUG)

# Rebuild
docker build -t ai-image-generator .
docker restart ai-image-generator

# View debug logs
docker logs -f ai-image-generator
```

---

### Container Shell Access

**Access container for debugging:**

```bash
# Start bash shell in container
docker exec -it ai-image-generator bash

# Inside container you can:
# - Check files: ls -la
# - View logs: cat /var/log/*
# - Test Python: python3
# - Check GPU: nvidia-smi
# - Check models: ls -lh models/

# Exit when done
exit
```

---

### Resource Monitoring

```bash
# Container resource usage
docker stats ai-image-generator

# GPU monitoring (if GPU)
watch -n 1 nvidia-smi

# System resources
htop  # or top

# Disk usage
docker system df
du -sh models/
```

---

## 📞 Getting Additional Help

### Automated Troubleshooter

```bash
# Interactive mode (best for most users)
python troubleshoot.py

# Auto-fix mode
python troubleshoot.py --auto

# Diagnostic mode
python troubleshoot.py --check
```

### Manual Diagnostics

```bash
# Run comprehensive tests
python test_api.py

# Health check
curl http://localhost:8000/health

# Model info
curl http://localhost:8000/model/info
```

### Collect Debug Information

```bash
# Create debug report
cat > debug-report.txt << EOF
=== System Info ===
$(uname -a)
$(docker --version)
$(nvidia-smi 2>&1 || echo "No GPU")

=== Container Status ===
$(docker ps -a | grep ai-image)

=== Recent Logs ===
$(docker logs --tail 50 ai-image-generator 2>&1)

=== Resource Usage ===
$(docker stats --no-stream ai-image-generator 2>&1)

=== Disk Space ===
$(df -h .)
EOF

cat debug-report.txt
```

---

## ✅ Health Check Checklist

Run through this checklist to verify everything is working:

- [ ] Docker installed and running: `docker --version`
- [ ] Image built: `docker images | grep ai-image`
- [ ] Container running: `docker ps | grep ai-image`
- [ ] Logs show no errors: `docker logs ai-image-generator`
- [ ] Health endpoint responds: `curl localhost:8000/health`
- [ ] Web UI loads: Open http://localhost:8000
- [ ] Can generate image: Try a simple prompt
- [ ] GPU detected (if applicable): Check logs for "device: cuda"
- [ ] No rate limiting issues: Generate 3-4 images quickly
- [ ] Images download correctly: Download a generated image

---

## 🎯 Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Can't connect | `docker logs ai-image-generator` |
| Port in use | `docker run -p 8080:8000 ...` |
| Out of memory | Reduce resolution or use CPU |
| Slow generation | Expected on CPU, use GPU |
| Model downloading | Wait 5-15 minutes first time |
| Container won't start | `docker rm -f ai-image-generator && docker run ...` |
| GPU not detected | Remove `--gpus all` flag |
| Bad image quality | Increase steps to 30-40 |
| Rate limited | Wait 60 seconds |
| Complete reset | `docker rm -f ai-image-generator && docker rmi ai-image-generator` |

---

## 🆘 Emergency Commands

```bash
# Nuclear option - complete clean restart
docker stop ai-image-generator 2>/dev/null
docker rm -f ai-image-generator 2>/dev/null
docker rmi ai-image-generator 2>/dev/null
docker system prune -f
cd diffusion-app
docker build -t ai-image-generator .
docker run -d -p 8000:8000 --name ai-image-generator ai-image-generator
docker logs -f ai-image-generator
```

---

**Still having issues? Run the automated troubleshooter:**

```bash
python troubleshoot.py
```

It will diagnose and fix most problems automatically! 🔧
