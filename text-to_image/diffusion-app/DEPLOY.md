# 🚀 COMPLETE DEPLOYMENT GUIDE

## One-Command Deployment (Fastest)

### Build the Image
```bash
cd diffusion-app
docker build -t ai-image-generator .
```

### Run the Container

**With GPU (Recommended):**
```bash
docker run -d \
  --name ai-image-generator \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  ai-image-generator
```

**CPU Only:**
```bash
docker run -d \
  --name ai-image-generator \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  ai-image-generator
```

### Access the Application
Open browser: **http://localhost:8000**

---

## Alternative: Docker Compose (Even Easier)

```bash
cd diffusion-app

# For GPU
docker-compose up -d

# For CPU only (edit docker-compose.yml first to remove GPU section)
docker-compose up -d
```

---

## Alternative: Automated Script

```bash
cd diffusion-app
chmod +x deploy.sh
./deploy.sh
```

Follow the interactive prompts.

---

## What Happens on First Run?

1. **Container Starts** (~5 seconds)
2. **Model Downloads** (~5-15 minutes, only first time)
   - Downloads Stable Diffusion 2.1 (~5GB)
   - Saved to `./models` directory
   - Subsequent runs skip this step
3. **Model Loads** (~15-30 seconds)
4. **Server Ready** ✅

**Total First Run**: 6-16 minutes (mostly model download)  
**Subsequent Runs**: ~20-45 seconds

---

## Verify Deployment

### Check Container Status
```bash
docker ps
```

Should show `ai-image-generator` with status "Up"

### Check Logs
```bash
docker logs -f ai-image-generator
```

Should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading model on cuda...
INFO:     Model loaded successfully in X.XXs
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "device": "cuda",
  "model_loaded": true,
  "timestamp": "2026-01-25T..."
}
```

### Run Full Test Suite
```bash
python test_api.py
```

---

## Generate Your First Image

### Web Interface
1. Open http://localhost:8000
2. Enter prompt: `a serene mountain landscape at sunset`
3. Click "Generate Image"
4. Wait ~5-10 seconds (GPU) or ~30-60 seconds (CPU)
5. Download your image!

### API (cURL)
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset over the ocean",
    "num_inference_steps": 25
  }' | jq -r '.image' | base64 -d > output.png
```

### API (Python)
```python
import requests
import base64

response = requests.post('http://localhost:8000/generate', json={
    'prompt': 'a beautiful sunset over the ocean',
    'num_inference_steps': 25
})

data = response.json()
image_data = base64.b64decode(data['image'])

with open('output.png', 'wb') as f:
    f.write(image_data)

print(f"Generated in {data['generation_time']:.2f}s with seed {data['seed']}")
```

---

## File Structure

```
diffusion-app/
├── app.py                  # Backend server (FastAPI)
├── frontend/
│   └── index.html         # Web interface (React SPA)
├── models/                # Model cache (auto-created)
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker Compose config
├── requirements.txt      # Python dependencies
├── deploy.sh            # Automated deployment
├── test_api.py          # Test suite
├── README.md            # Main documentation
├── API.md               # API reference
├── QUICKSTART.md        # Quick start guide
├── PERFORMANCE.md       # Performance benchmarks
├── PROJECT_SUMMARY.md   # Project overview
├── LICENSE              # MIT License
└── .env.example         # Configuration template
```

---

## Management Commands

### Start
```bash
docker start ai-image-generator
# OR
docker-compose up -d
```

### Stop
```bash
docker stop ai-image-generator
# OR
docker-compose down
```

### Restart
```bash
docker restart ai-image-generator
# OR
docker-compose restart
```

### View Logs
```bash
docker logs -f ai-image-generator
# OR
docker-compose logs -f
```

### Remove
```bash
docker rm -f ai-image-generator
# OR
docker-compose down -v  # Also removes volumes
```

### Update
```bash
docker-compose down
docker build -t ai-image-generator .
docker-compose up -d
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs ai-image-generator

# Common issues:
# 1. Port 8000 already in use
#    - Use different port: -p 8080:8000
# 2. No GPU available
#    - Remove --gpus all flag
# 3. Insufficient disk space
#    - Need ~20GB free
```

### Model Download Fails
```bash
# Check internet connection
curl -I https://huggingface.co

# Manually download (optional)
huggingface-cli download stabilityai/stable-diffusion-2-1-base
```

### Out of Memory (GPU)
```bash
# Use CPU instead
docker run -d -p 8000:8000 --name ai-image-gen ai-image-generator

# OR edit app.py to enable CPU offloading:
# pipe.enable_model_cpu_offload()
```

### Slow Generation
```bash
# Check if using CPU
docker logs ai-image-generator | grep device

# If CPU:
# - Reduce steps to 20
# - Use 256x256 resolution
# - Or get a GPU!
```

---

## Performance Optimization

### GPU Optimization
- Ensure NVIDIA drivers are up to date
- Use xformers (auto-enabled if available)
- Reduce inference steps to 20-25 for speed
- Use 512x512 resolution (native)

### CPU Optimization
- Reduce steps to 20
- Use 256x256 or 384x384 resolution
- Ensure adequate RAM (16GB+)
- Close other applications

### Docker Optimization
```bash
# Allocate more resources (if using Docker Desktop)
# Settings > Resources > Advanced
# - CPUs: 4+
# - Memory: 16GB+
# - Swap: 2GB+
```

---

## Security Considerations

### Production Deployment

1. **Add Authentication**
   - Not included by default
   - Consider adding JWT or API keys

2. **Use HTTPS**
   - Put behind reverse proxy (nginx)
   - Use Let's Encrypt for SSL

3. **Configure Firewall**
   - Only expose port 8000 to trusted networks
   - Or use VPN

4. **Rate Limiting**
   - Default: 10 requests/minute
   - Adjust in `app.py` if needed

5. **Monitoring**
   - Set up logging aggregation
   - Monitor GPU/CPU usage
   - Track generation times

---

## Cloud Deployment

### AWS EC2

1. Launch GPU instance (g4dn.xlarge or better)
2. Install Docker and NVIDIA Docker
3. Clone repository
4. Run deployment commands
5. Configure security group (port 8000)
6. (Optional) Set up Elastic IP

### Google Cloud Platform

1. Create Compute Engine instance with GPU
2. Install Docker and NVIDIA Docker
3. Clone repository
4. Run deployment commands
5. Configure firewall rules

### Azure

1. Create VM with GPU (NC-series)
2. Install Docker and NVIDIA Docker
3. Clone repository
4. Run deployment commands
5. Configure Network Security Group

---

## Scaling

### Horizontal Scaling
```yaml
# docker-compose-scale.yml
version: '3.8'
services:
  diffusion-app:
    image: ai-image-generator
    deploy:
      replicas: 3
    # ... rest of config
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancing
Use nginx to distribute requests across multiple containers.

---

## Monitoring

### Basic Monitoring
```bash
# Container stats
docker stats ai-image-generator

# GPU monitoring (if available)
watch nvidia-smi

# Request logs
docker logs -f ai-image-generator | grep "Generated image"
```

### Advanced Monitoring
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- DataDog, New Relic, etc.

---

## Backup & Restore

### Backup Models
```bash
# Models are in ./models directory
tar -czf models-backup.tar.gz models/
```

### Restore Models
```bash
tar -xzf models-backup.tar.gz
```

---

## Environment Variables

Create `.env` file (from `.env.example`):

```bash
# Model Configuration
MODEL_ID=stabilityai/stable-diffusion-2-1-base
TRANSFORMERS_CACHE=/app/models
HF_HOME=/app/models

# Performance
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENABLE_XFORMERS=true

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10

# Safety
ENABLE_SAFETY_CHECKER=true
```

---

## Support

### Documentation
- `README.md` - Complete guide
- `QUICKSTART.md` - 5-minute setup
- `API.md` - API reference
- `PERFORMANCE.md` - Optimization guide
- `PROJECT_SUMMARY.md` - Overview

### Testing
```bash
python test_api.py
```

### Issues
- Check logs: `docker logs ai-image-generator`
- Review documentation
- Check GitHub issues

---

## Summary

**Deployment Steps:**
1. Build: `docker build -t ai-image-generator .`
2. Run: `docker run -d -p 8000:8000 --gpus all ai-image-generator`
3. Access: http://localhost:8000
4. Generate!

**First Run:** 6-16 minutes (model download)  
**Subsequent Runs:** 20-45 seconds  
**Generation Time:** 5-10s (GPU) / 30-60s (CPU)

**You're ready to create amazing AI-generated images! 🎨**

---

*For detailed information, see README.md, QUICKSTART.md, and API.md*
