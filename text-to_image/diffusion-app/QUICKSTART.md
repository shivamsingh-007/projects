# Quick Start Guide

Get up and running with the AI Image Generator in 5 minutes.

## 🚀 Fastest Route to Running

### Prerequisites Check
```bash
# Check Docker
docker --version

# Check for GPU (optional, but recommended)
nvidia-smi
```

### One-Command Start

**With GPU:**
```bash
docker run -d -p 8000:8000 --gpus all --name ai-image-gen \
  -v $(pwd)/models:/app/models \
  ai-image-generator
```

**CPU Only:**
```bash
docker run -d -p 8000:8000 --name ai-image-gen \
  -v $(pwd)/models:/app/models \
  ai-image-generator
```

### Access the App

1. Open browser: http://localhost:8000
2. Wait ~1-2 minutes for model to load (first time only)
3. Enter a prompt and click "Generate Image"

That's it! 🎉

---

## 📋 Step-by-Step Setup

### Step 1: Clone/Download

```bash
git clone <repository-url>
cd diffusion-app
```

Or download and extract the ZIP file.

### Step 2: Build Docker Image

```bash
docker build -t ai-image-generator .
```

This takes ~5 minutes. The model (~5GB) downloads on first run, not during build.

### Step 3: Run Container

**Using the deployment script (easiest):**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Or manually:**
```bash
docker-compose up -d
```

**Or with Docker directly:**
```bash
docker run -d \
  --name ai-image-generator \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  --restart unless-stopped \
  ai-image-generator
```

### Step 4: Verify It's Running

```bash
# Check logs
docker logs -f ai-image-generator

# You should see:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Loading model on cuda...
# INFO:     Model loaded successfully in X.XXs
```

### Step 5: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Generate an image
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a serene mountain landscape at sunset",
    "num_inference_steps": 25
  }'
```

### Step 6: Open Web Interface

Navigate to: http://localhost:8000

---

## 💡 First Image Generation

1. **Enter a prompt** in the text box:
   ```
   a serene mountain landscape at sunset, professional photography
   ```

2. **Add negative prompt** (optional):
   ```
   blurry, low quality, distorted
   ```

3. **Adjust settings** (optional):
   - Inference Steps: 25-30 recommended
   - Guidance Scale: 7.5 default
   - Resolution: 512x512 recommended

4. **Click "Generate Image"**

5. **Wait** ~5-10 seconds (GPU) or ~30-60 seconds (CPU)

6. **Download** your image!

---

## 🎨 Try These Example Prompts

Copy and paste these into the prompt box:

### Landscapes
```
majestic mountain landscape at golden hour, snow-capped peaks, 
alpine lake reflection, professional landscape photography, 
highly detailed, 8k resolution
```

### Portraits
```
portrait of a wise elderly woman, warm smile, wrinkles showing 
life experience, soft natural lighting, photography by 
Annie Leibovitz, detailed face
```

### Fantasy
```
dragon perched on castle tower at night, full moon, 
medieval fantasy setting, epic cinematic lighting, 
digital art, highly detailed
```

### Architecture
```
modern minimalist house in forest, large windows, 
natural materials, architectural photography, 
surrounded by tall trees, misty morning
```

---

## 🔧 Common Issues & Solutions

### Issue: "Connection refused"
**Solution:** Container isn't running yet
```bash
docker ps  # Check if container is running
docker logs ai-image-generator  # Check logs
```

### Issue: "Model loading takes forever"
**Solution:** First run downloads ~5GB model
- This is normal
- Takes 5-15 minutes depending on internet speed
- Subsequent runs are instant

### Issue: "CUDA out of memory"
**Solution:** Reduce settings or use CPU
```bash
# Stop container
docker stop ai-image-generator

# Restart without GPU
docker run -d -p 8000:8000 --name ai-image-gen ai-image-generator
```

### Issue: Slow generation (>60s)
**Solution:** You're probably running on CPU
- CPU is 5-10x slower than GPU
- Reduce inference steps to 20
- Use 256x256 or 384x384 resolution

### Issue: "Rate limit exceeded"
**Solution:** Wait 1 minute or adjust rate limit
- Default: 10 requests/minute
- Edit `app.py` and change `RATE_LIMIT_PER_MINUTE`

---

## 📊 Monitor Performance

### View Logs
```bash
docker logs -f ai-image-generator
```

### Check Resource Usage
```bash
# CPU/Memory
docker stats ai-image-generator

# GPU (if available)
nvidia-smi
```

### Test API
```bash
python test_api.py
```

---

## 🛑 Stop & Restart

### Stop
```bash
docker stop ai-image-generator
```

### Start
```bash
docker start ai-image-generator
```

### Restart
```bash
docker restart ai-image-generator
```

### Remove
```bash
docker rm -f ai-image-generator
```

### View all commands
```bash
docker-compose down  # Stop
docker-compose up -d  # Start
docker-compose restart  # Restart
docker-compose logs -f  # View logs
```

---

## 📦 Update to Latest Version

```bash
# Stop current container
docker-compose down

# Pull latest code
git pull

# Rebuild image
docker build -t ai-image-generator .

# Start new container
docker-compose up -d
```

---

## 🎯 Next Steps

1. **Explore the UI**: Try different prompts and settings
2. **Read API Docs**: Check [API.md](API.md) for programmatic access
3. **Optimize Performance**: Review [PERFORMANCE.md](PERFORMANCE.md)
4. **Check Examples**: See `test_api.py` for code examples
5. **Customize**: Edit `app.py` to adjust defaults

---

## 🆘 Need Help?

1. Check [README.md](README.md) for full documentation
2. Review [API.md](API.md) for API details
3. See [PERFORMANCE.md](PERFORMANCE.md) for optimization
4. Run `python test_api.py` to diagnose issues
5. Check Docker logs: `docker logs ai-image-generator`

---

## 🎉 You're Ready!

Start creating amazing AI-generated images. Happy generating! 🖼️

**Tips for Best Results:**
- Be specific and descriptive in prompts
- Use style keywords (oil painting, photorealistic, etc.)
- Mention lighting and mood
- Add quality modifiers (highly detailed, 8k, professional)
- Use negative prompts to avoid unwanted elements
- Experiment with guidance scale and steps
- Save seeds for reproducible results

---

**Quick Reference:**

| Action | Command |
|--------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose down` |
| Logs | `docker logs -f ai-image-generator` |
| Test | `python test_api.py` |
| Access | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

*Last updated: 2026-01-25*
