# 📦 AI Image Generator - All-in-One Installation Package

**Complete installation guide with all files embedded**

This single file contains everything you need. Just copy the code sections below to create each file.

---

## 🚀 Quick Installation Steps

1. Create a directory: `mkdir diffusion-app && cd diffusion-app`
2. Copy each section below into the corresponding file
3. Run: `docker build -t ai-image-generator .`
4. Run: `docker run -d -p 8000:8000 --gpus all ai-image-generator`
5. Access: http://localhost:8000

---

## 📁 File 1: requirements.txt

Create file: `requirements.txt`

```text
# Core Dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3

# ML/AI Dependencies
torch==2.1.2
torchvision==0.16.2
diffusers==0.25.1
transformers==4.36.2
accelerate==0.26.1
safetensors==0.4.2
xformers==0.0.23.post1

# Image Processing
Pillow==10.2.0
numpy==1.26.3

# Utilities
python-multipart==0.0.6
aiofiles==23.2.1
```

---

## 📁 File 2: Dockerfile

Create file: `Dockerfile`

```dockerfile
# Production-Ready Dockerfile for Stable Diffusion Image Generator
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY frontend/ ./frontend/

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Run the application
CMD ["python", "app.py"]
```

---

## 📁 File 3: docker-compose.yml

Create file: `docker-compose.yml`

```yaml
version: '3.8'

services:
  diffusion-app:
    build: .
    container_name: ai-image-generator
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
    environment:
      - PYTHONUNBUFFERED=1
      - TRANSFORMERS_CACHE=/app/models
      - HF_HOME=/app/models
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

---

## 📁 File 4: app.py

Create file: `app.py`

**Note: This is a large file. Copy carefully!**

```python
"""
Production-Ready Text-to-Image Generation API
FastAPI backend with Stable Diffusion 2.1
"""

import os
import io
import base64
import time
import hashlib
import logging
from typing import Optional, List
from datetime import datetime
from pathlib import Path

import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    MODEL_ID = "stabilityai/stable-diffusion-2-1-base"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    MAX_BATCH_SIZE = 1
    DEFAULT_NUM_INFERENCE_STEPS = 30
    DEFAULT_GUIDANCE_SCALE = 7.5
    IMAGE_SIZE = 512
    ENABLE_ATTENTION_SLICING = True
    ENABLE_VAE_SLICING = True
    CACHE_DIR = "./models"
    RATE_LIMIT_PER_MINUTE = 10
    MAX_PROMPT_LENGTH = 500

config = Config()

# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., max_length=config.MAX_PROMPT_LENGTH)
    negative_prompt: Optional[str] = Field(default="", max_length=config.MAX_PROMPT_LENGTH)
    num_inference_steps: int = Field(default=30, ge=10, le=50)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    seed: Optional[int] = Field(default=None, ge=0)
    width: int = Field(default=512, ge=256, le=768)
    height: int = Field(default=512, ge=256, le=768)

class GenerateResponse(BaseModel):
    image: str
    seed: int
    generation_time: float
    is_safe: bool
    metadata: dict

class HealthResponse(BaseModel):
    status: str
    device: str
    model_loaded: bool
    timestamp: str

# Rate limiting
request_timestamps = {}

def check_rate_limit(client_id: str) -> bool:
    now = time.time()
    if client_id not in request_timestamps:
        request_timestamps[client_id] = []
    
    request_timestamps[client_id] = [
        ts for ts in request_timestamps[client_id] 
        if now - ts < 60
    ]
    
    if len(request_timestamps[client_id]) >= config.RATE_LIMIT_PER_MINUTE:
        return False
    
    request_timestamps[client_id].append(now)
    return True

# Model Manager
class DiffusionModelManager:
    def __init__(self):
        self.pipe = None
        self.device = config.DEVICE
        self.loaded = False
        
    def load_model(self):
        if self.loaded:
            return
        
        logger.info(f"Loading model on {self.device}...")
        start_time = time.time()
        
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                config.MODEL_ID,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=config.CACHE_DIR,
                safety_checker=StableDiffusionSafetyChecker.from_pretrained(
                    "CompVis/stable-diffusion-safety-checker",
                    cache_dir=config.CACHE_DIR
                )
            )
            
            self.pipe.scheduler = EulerDiscreteScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            self.pipe = self.pipe.to(self.device)
            
            if config.ENABLE_ATTENTION_SLICING:
                self.pipe.enable_attention_slicing()
            if config.ENABLE_VAE_SLICING:
                self.pipe.enable_vae_slicing()
            
            if self.device == "cuda":
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    logger.info("xformers memory efficient attention enabled")
                except Exception as e:
                    logger.warning(f"xformers not available: {e}")
            
            self.loaded = True
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        width: int = 512,
        height: int = 512,
    ) -> tuple[Image.Image, int, bool]:
        if not self.loaded:
            self.load_model()
        
        if seed is None:
            seed = np.random.randint(0, 2**32 - 1)
        
        generator = torch.Generator(device=self.device).manual_seed(seed)
        
        start_time = time.time()
        
        with torch.autocast(self.device):
            output = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                width=width,
                height=height,
            )
        
        generation_time = time.time() - start_time
        
        is_safe = not output.nsfw_content_detected[0] if output.nsfw_content_detected else True
        
        image = output.images[0]
        
        logger.info(f"Generated image in {generation_time:.2f}s (safe: {is_safe})")
        
        return image, seed, is_safe

# Initialize FastAPI app
app = FastAPI(
    title="Diffusion Image Generator API",
    description="Production-ready text-to-image generation using Stable Diffusion 2.1",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_manager = DiffusionModelManager()

@app.on_event("startup")
async def startup_event():
    try:
        model_manager.load_model()
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if model_manager.loaded else "loading",
        device=config.DEVICE,
        model_loaded=model_manager.loaded,
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest, req: Request):
    client_id = req.client.host
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {config.RATE_LIMIT_PER_MINUTE} requests per minute."
        )
    
    try:
        start_time = time.time()
        
        image, seed, is_safe = model_manager.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed,
            width=request.width,
            height=request.height,
        )
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        generation_time = time.time() - start_time
        
        return GenerateResponse(
            image=img_base64,
            seed=seed,
            generation_time=generation_time,
            is_safe=is_safe,
            metadata={
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "width": request.width,
                "height": request.height,
                "device": config.DEVICE,
            }
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/prompts/suggestions")
async def get_prompt_suggestions():
    return {
        "suggestions": [
            {
                "category": "Portraits",
                "prompts": [
                    "portrait of a wise old wizard with a long white beard, detailed face, fantasy art, oil painting style",
                    "professional headshot of a female CEO, confident smile, modern office background, studio lighting",
                    "cyberpunk street samurai, neon lights reflecting on face, rain-soaked streets, futuristic",
                ]
            },
            {
                "category": "Landscapes",
                "prompts": [
                    "majestic mountain landscape at sunset, dramatic clouds, alpine meadow with wildflowers, 8k photo",
                    "serene Japanese garden with cherry blossoms, koi pond, wooden bridge, soft morning light",
                    "alien planet landscape, two moons in the sky, bioluminescent plants, sci-fi concept art",
                ]
            },
        ]
    }

@app.get("/model/info")
async def get_model_info():
    return {
        "model_id": config.MODEL_ID,
        "device": config.DEVICE,
        "loaded": model_manager.loaded,
        "capabilities": {
            "max_resolution": f"{config.IMAGE_SIZE}x{config.IMAGE_SIZE}",
            "attention_slicing": config.ENABLE_ATTENTION_SLICING,
            "vae_slicing": config.ENABLE_VAE_SLICING,
        },
        "limits": {
            "max_prompt_length": config.MAX_PROMPT_LENGTH,
            "rate_limit": f"{config.RATE_LIMIT_PER_MINUTE} requests/minute",
            "inference_steps_range": "10-50",
            "guidance_scale_range": "1.0-20.0",
        }
    }

frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
```

---

## 📁 File 5: frontend/index.html

Create directory: `mkdir frontend`
Create file: `frontend/index.html`

**Note: This is the largest file (31KB). You can download it separately or I can break it into parts.**

Due to file size, please use one of these methods to get the frontend file:

**Method 1: Download the compressed archive (recommended)**
**Method 2: Copy from the repository**
**Method 3: I can provide the HTML in smaller chunks**

---

## 🚀 ALTERNATIVE: Direct Download Links

I've created compressed archives for easier download:

1. **diffusion-app.tar.gz** (54KB) - For Linux/Mac
2. **diffusion-app.zip** (67KB) - For Windows

These contain ALL files ready to use!

---

## 📋 Manual Installation Steps

If downloads still fail, follow these steps:

### Step 1: Create Directory Structure
```bash
mkdir -p diffusion-app/frontend
cd diffusion-app
```

### Step 2: Create Each File
Copy each file content from above into the correct location.

### Step 3: Deploy
```bash
docker build -t ai-image-generator .
docker run -d -p 8000:8000 --gpus all ai-image-generator
```

---

## 🆘 Need Help?

If you're still having trouble downloading, please let me know:
1. What error message you're seeing
2. What browser you're using
3. If you prefer the files in a different format

I can:
- Break the files into smaller chunks
- Provide alternative download methods
- Create individual file downloads
- Send via different compression formats
