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
    image: str  # base64 encoded
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
    """Simple in-memory rate limiting"""
    now = time.time()
    if client_id not in request_timestamps:
        request_timestamps[client_id] = []
    
    # Clean old timestamps
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
        """Load Stable Diffusion model with optimizations"""
        if self.loaded:
            return
        
        logger.info(f"Loading model on {self.device}...")
        start_time = time.time()
        
        try:
            # Load pipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                config.MODEL_ID,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=config.CACHE_DIR,
                safety_checker=StableDiffusionSafetyChecker.from_pretrained(
                    "CompVis/stable-diffusion-safety-checker",
                    cache_dir=config.CACHE_DIR
                )
            )
            
            # Use Euler scheduler for better quality/speed tradeoff
            self.pipe.scheduler = EulerDiscreteScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            # Move to device
            self.pipe = self.pipe.to(self.device)
            
            # Enable memory optimizations
            if config.ENABLE_ATTENTION_SLICING:
                self.pipe.enable_attention_slicing()
            if config.ENABLE_VAE_SLICING:
                self.pipe.enable_vae_slicing()
            
            # Enable xformers if available (GPU only)
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
        """Generate image from text prompt"""
        if not self.loaded:
            self.load_model()
        
        # Set seed for reproducibility
        if seed is None:
            seed = np.random.randint(0, 2**32 - 1)
        
        generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # Generate image
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
        
        # Check safety
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model manager
model_manager = DiffusionModelManager()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        model_manager.load_model()
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model_manager.loaded else "loading",
        device=config.DEVICE,
        model_loaded=model_manager.loaded,
        timestamp=datetime.utcnow().isoformat()
    )

# Generate endpoint
@app.post("/generate", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest, req: Request):
    """Generate image from text prompt"""
    
    # Rate limiting
    client_id = req.client.host
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {config.RATE_LIMIT_PER_MINUTE} requests per minute."
        )
    
    try:
        start_time = time.time()
        
        # Generate image
        image, seed, is_safe = model_manager.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed,
            width=request.width,
            height=request.height,
        )
        
        # Convert to base64
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

# Prompt suggestions endpoint
@app.get("/prompts/suggestions")
async def get_prompt_suggestions():
    """Get example prompts"""
    return {
        "suggestions": [
            {
                "category": "Portraits",
                "prompts": [
                    "portrait of a wise old wizard with a long white beard, detailed face, fantasy art, oil painting style",
                    "professional headshot of a female CEO, confident smile, modern office background, studio lighting",
                    "cyberpunk street samurai, neon lights reflecting on face, rain-soaked streets, futuristic",
                    "renaissance portrait of a noble woman, ornate dress, dramatic lighting, classical painting",
                ]
            },
            {
                "category": "Landscapes",
                "prompts": [
                    "majestic mountain landscape at sunset, dramatic clouds, alpine meadow with wildflowers, 8k photo",
                    "serene Japanese garden with cherry blossoms, koi pond, wooden bridge, soft morning light",
                    "alien planet landscape, two moons in the sky, bioluminescent plants, sci-fi concept art",
                    "cozy cabin in snowy forest, smoke from chimney, warm lights in windows, winter evening",
                ]
            },
            {
                "category": "Architecture",
                "prompts": [
                    "modern minimalist house, floor-to-ceiling windows, surrounded by nature, architectural photography",
                    "futuristic skyscraper with organic curves, sustainable design, rooftop gardens, day time",
                    "ancient temple ruins overgrown with vines, misty atmosphere, golden hour lighting",
                    "steampunk city street, Victorian architecture with industrial elements, brass and copper details",
                ]
            },
            {
                "category": "Fantasy & Sci-Fi",
                "prompts": [
                    "dragon perched on castle tower, wings spread, medieval fantasy, epic scene, cinematic lighting",
                    "space station orbiting a ringed planet, detailed sci-fi illustration, stars in background",
                    "enchanted forest with glowing mushrooms, fairy lights, magical atmosphere, fantasy art",
                    "robot uprising in cyberpunk city, neon signs, rain, dramatic action scene",
                ]
            },
            {
                "category": "Animals & Nature",
                "prompts": [
                    "majestic lion portrait, golden mane, intense gaze, professional wildlife photography",
                    "colorful tropical bird on branch, rainforest background, vibrant feathers, macro photography",
                    "underwater coral reef scene, tropical fish, clear blue water, marine life, nature documentary",
                    "arctic fox in snow, white fur, winter landscape, wildlife photography, natural lighting",
                ]
            },
            {
                "category": "Abstract & Artistic",
                "prompts": [
                    "abstract geometric shapes, vibrant colors, modern art style, composition balance",
                    "fluid art pour painting, swirling colors, marbling effect, artistic photography",
                    "mandala design, intricate patterns, symmetrical, spiritual art, detailed illustration",
                    "impressionist style painting of water lilies, soft brush strokes, pastel colors",
                ]
            },
            {
                "category": "Objects & Still Life",
                "prompts": [
                    "vintage camera on wooden desk, film rolls, nostalgic atmosphere, warm lighting, product photo",
                    "fresh fruits in ceramic bowl, natural lighting, food photography, rustic style",
                    "mechanical watch mechanism, intricate gears, macro photography, metallic details",
                    "stack of old books with tea cup, cozy reading nook, soft afternoon light",
                ]
            },
            {
                "category": "Seasonal",
                "prompts": [
                    "autumn forest path, fallen leaves, warm colors, peaceful atmosphere, nature photography",
                    "spring meadow full of wildflowers, butterflies, sunny day, vibrant colors",
                    "summer beach at sunset, palm trees, ocean waves, tropical paradise, golden hour",
                    "winter wonderland, snow-covered pine trees, northern lights, magical night scene",
                ]
            },
        ]
    }

# Model info endpoint
@app.get("/model/info")
async def get_model_info():
    """Get model information"""
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

# Mount static files (frontend)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve frontend index.html"""
        return FileResponse(str(frontend_path / "index.html"))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
