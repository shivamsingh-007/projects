# DiffusionForge - System Architecture & Design

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER DEVICE                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Web Browser (Any Device)                    │   │
│  │  • Desktop (Chrome, Firefox, Safari, Edge)              │   │
│  │  • Mobile (iOS Safari, Android Chrome)                  │   │
│  │  • Tablet                                               │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             │ Port 8000
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER CONTAINER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    FRONTEND LAYER                        │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │  Static Files (HTML/CSS/JS)                     │     │   │
│  │  │  • index.html (SPA)                            │     │   │
│  │  │  • Tailwind CSS                                │     │   │
│  │  │  • Vanilla JavaScript                          │     │   │
│  │  │  • Responsive Design                           │     │   │
│  │  │  • Dark/Light Theme                            │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           │ File Serving                         │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION LAYER                       │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │  FastAPI Backend (app.py)                      │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  REST API Endpoints                      │  │     │   │
│  │  │  │  • POST /api/generate                    │  │     │   │
│  │  │  │  • GET  /api/examples                   │  │     │   │
│  │  │  │  • GET  /api/stats                      │  │     │   │
│  │  │  │  • GET  /health                         │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  Middleware Stack                        │  │     │   │
│  │  │  │  • CORS Handler                          │  │     │   │
│  │  │  │  • Rate Limiter (SlowAPI)                │  │     │   │
│  │  │  │  • Request Validator (Pydantic)          │  │     │   │
│  │  │  │  • Error Handler                         │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  Business Logic                          │  │     │   │
│  │  │  │  • Input Sanitization                    │  │     │   │
│  │  │  │  • Prompt Processing                     │  │     │   │
│  │  │  │  • Image Encoding/Decoding               │  │     │   │
│  │  │  │  • File Management                       │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           │ Model Inference                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     AI/ML LAYER                          │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │  Diffusers Pipeline                            │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  Stable Diffusion 2.1 Base               │  │     │   │
│  │  │  │  • Text Encoder (CLIP)                   │  │     │   │
│  │  │  │  • U-Net Denoiser (865M params)          │  │     │   │
│  │  │  │  • VAE Decoder                           │  │     │   │
│  │  │  │  • Safety Checker (NSFW)                 │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  Scheduler                               │  │     │   │
│  │  │  │  • DPM++ Multistep                       │  │     │   │
│  │  │  │  • Adaptive timesteps                    │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  │  ┌──────────────────────────────────────────┐  │     │   │
│  │  │  │  Optimizations                           │  │     │   │
│  │  │  │  • xFormers attention                    │  │     │   │
│  │  │  │  • Attention slicing                     │  │     │   │
│  │  │  │  • VAE slicing                           │  │     │   │
│  │  │  │  • FP16 precision                        │  │     │   │
│  │  │  └──────────────────────────────────────────┘  │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           │ Hardware Acceleration                │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               COMPUTE LAYER                              │   │
│  │  ┌──────────────────┐      ┌──────────────────┐         │   │
│  │  │  CUDA/GPU        │  OR  │  CPU             │         │   │
│  │  │  • NVIDIA GPU    │      │  • Multi-core    │         │   │
│  │  │  • CUDA 11.8     │      │  • PyTorch       │         │   │
│  │  │  • cuDNN         │      │  • OpenMP        │         │   │
│  │  │  • 6-24GB VRAM   │      │  • 8-16GB RAM    │         │   │
│  │  └──────────────────┘      └──────────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  STORAGE LAYER                           │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │  Persistent Volumes (Host-mounted)             │     │   │
│  │  │  • /app/models  → Model cache (5GB)            │     │   │
│  │  │  • /app/outputs → Generated images (1-2MB ea)  │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flow Diagram

```
User Action (Web UI)
        │
        ▼
┌───────────────────────┐
│  1. Enter Prompt      │
│  2. Set Parameters    │
│  3. Click Generate    │
└───────┬───────────────┘
        │
        │ POST /api/generate
        │ {prompt, steps, guidance, ...}
        ▼
┌─────────────────────────────────┐
│   FastAPI Routing               │
│   • Match endpoint              │
│   • Extract request body        │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Rate Limiter                  │
│   • Check IP request count      │
│   • 10 requests/minute limit    │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Request Validation            │
│   • Pydantic model validation   │
│   • Check ranges (steps, size)  │
│   • Sanitize prompt             │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Pipeline Preparation          │
│   • Load SD pipeline            │
│   • Set device (GPU/CPU)        │
│   • Configure scheduler         │
│   • Set seed                    │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Text Encoding                 │
│   • CLIP text encoder           │
│   • Convert to embeddings       │
│   • Process negative prompt     │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Denoising Loop                │
│   • Initialize random noise     │
│   • For each timestep:          │
│     - U-Net forward pass        │
│     - Scheduler step            │
│     - Update latents            │
│   • 10-100 iterations           │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   VAE Decoding                  │
│   • Decode latents to pixels    │
│   • Upscale to target size      │
│   • Apply color correction      │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   NSFW Check                    │
│   • Safety checker model        │
│   • Flag inappropriate content  │
│   • Return black image if NSFW  │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Post-processing               │
│   • Convert to PIL Image        │
│   • Encode as PNG               │
│   • Base64 encode               │
│   • Save to disk                │
└───────┬─────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Response Construction         │
│   • Create JSON response        │
│   • Include seed, time, etc.    │
│   • Send to client              │
└───────┬─────────────────────────┘
        │
        │ JSON Response
        │ {image: base64, seed, time}
        ▼
┌─────────────────────────────────┐
│   Frontend Display              │
│   • Decode base64               │
│   • Display image               │
│   • Add to gallery              │
│   • Enable download/share       │
└─────────────────────────────────┘

Total Time: 3-10s (GPU) or 2-5min (CPU)
```

---

## Data Flow

### Input Processing
```
User Prompt Text
        ↓
[Sanitization]
        ↓
[Tokenization]
        ↓
CLIP Text Encoder
        ↓
Text Embeddings (77 × 1024)
        ↓
U-Net Conditioning
```

### Image Generation
```
Random Noise (latents)
        ↓
┌─────────────────┐
│  Timestep Loop  │
│  (10-100 steps) │
└────────┬────────┘
         ↓
    U-Net Prediction
         ↓
    Scheduler Update
         ↓
    Updated Latents
         ↓
    [Repeat]
         ↓
Final Latents (64 × 64 × 4)
         ↓
VAE Decoder
         ↓
RGB Image (512 × 512 × 3)
         ↓
PNG Encoding
         ↓
Base64 String
         ↓
Client Display
```

---

## Component Details

### 1. Frontend (index.html)

**Technology**: HTML5 + Tailwind CSS + Vanilla JS

**Key Components**:
- Header with branding and theme toggle
- Prompt input textarea
- Negative prompt input
- Advanced settings panel (collapsible)
- Parameter sliders (steps, guidance)
- Size selector dropdown
- Generate button
- Progress indicator
- Image display with zoom
- Gallery grid
- Examples modal
- Stats modal

**State Management**:
- Local storage for theme preference
- In-memory gallery array (last 12 images)
- Current image for download/share

**API Communication**:
- Fetch API for HTTP requests
- JSON request/response
- Base64 image handling

### 2. Backend (app.py)

**Framework**: FastAPI 0.109.0

**Key Features**:
- Async request handling
- Pydantic data validation
- CORS middleware
- Rate limiting (SlowAPI)
- Static file serving
- Error handling
- Logging

**Endpoints**:
1. `GET /` - Serve frontend
2. `GET /health` - Health check
3. `GET /api/examples` - Get prompts
4. `GET /api/stats` - System info
5. `POST /api/generate` - Generate image

**Request Processing**:
- Validate with Pydantic models
- Enforce parameter limits
- Sanitize inputs
- Set defaults

### 3. AI Pipeline

**Library**: Diffusers 0.25.1

**Components**:

1. **Text Encoder** (CLIP ViT-H/14)
   - Input: Text prompt (max 77 tokens)
   - Output: 77 × 1024 embeddings
   - Purpose: Convert text to latent space

2. **U-Net** (865M parameters)
   - Input: Noisy latents + text embeddings + timestep
   - Output: Noise prediction
   - Architecture: Cross-attention layers
   - Purpose: Iterative denoising

3. **VAE Decoder**
   - Input: 64 × 64 × 4 latents
   - Output: 512 × 512 × 3 RGB image
   - Purpose: Convert latents to pixels

4. **Safety Checker**
   - Input: Generated image
   - Output: NSFW flag
   - Purpose: Content moderation

**Scheduler** (DPM++ Multistep):
- Fast convergence
- High quality at 20-30 steps
- Adaptive timesteps

**Optimizations**:
- xFormers: Memory-efficient attention
- Attention slicing: Reduce VRAM
- VAE slicing: Further memory savings
- FP16: Half precision on GPU

### 4. Docker Container

**Base Image**: nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

**Multi-stage Build**:
1. Base: System dependencies
2. Dependencies: Python packages + model
3. Production: Final optimized image

**Volumes**:
- `/app/models`: Model cache (persisted)
- `/app/outputs`: Generated images (persisted)

**Exposed Ports**:
- 8000: HTTP server

**Health Check**:
- Endpoint: `/health`
- Interval: 30s
- Timeout: 10s

---

## Security Architecture

### Input Validation
```
User Input
    ↓
Length Checks (1-500 chars)
    ↓
Character Sanitization
    ↓
Parameter Range Validation
    ↓
Pydantic Type Checking
    ↓
Proceed to Generation
```

### Rate Limiting
```
Request → Extract IP → Check Counter
                              ↓
                    Within Limit? ━━ No ━━→ 429 Error
                              ↓
                             Yes
                              ↓
                       Increment Counter
                              ↓
                       Process Request
```

### NSFW Filtering
```
Generated Image
        ↓
Safety Checker Model
        ↓
NSFW Detected? ━━ Yes ━━→ Return Black Image
        ↓
       No
        ↓
Return Original Image
```

---

## Performance Optimization

### Memory Hierarchy
```
GPU VRAM (fastest)
    ↓ [4-6 GB]
Model Weights + Activations
    ↓
System RAM
    ↓ [8-16 GB]
CPU Processing + OS
    ↓
Disk (SSD)
    ↓ [5 GB]
Model Cache
```

### Optimization Layers

1. **Model Level**:
   - FP16 precision (50% memory)
   - Model pruning (future)
   - Quantization (future)

2. **Attention Level**:
   - xFormers (30% faster)
   - Flash Attention (future)
   - Sliding window

3. **Pipeline Level**:
   - Attention slicing
   - VAE slicing
   - CPU offloading (if needed)

4. **Scheduler Level**:
   - DPM++ (fewer steps)
   - Adaptive timesteps
   - Optimal step count

---

## Scalability Considerations

### Horizontal Scaling
```
Load Balancer (Nginx)
        |
   ┌────┴────┬────────┬────────┐
   ▼         ▼        ▼        ▼
Instance1 Instance2 Instance3 Instance4
(GPU 0)   (GPU 1)  (GPU 2)  (GPU 3)
```

### Vertical Scaling
```
Better GPU → More VRAM → Larger Images + Batch Size
More CPU Cores → Faster CPU Mode
More RAM → More Caching
Faster Storage → Faster Model Loading
```

### Queue System (Future)
```
Client Request
      ↓
   Redis Queue
      ↓
   Worker Pool
      ↓
   GPU Processing
      ↓
   Result Storage
      ↓
   Webhook Callback
```

---

## Monitoring & Observability

### Metrics to Track
- Request rate (requests/minute)
- Generation time (percentiles)
- Error rate
- GPU utilization
- VRAM usage
- Queue length
- Response size

### Logging Levels
- INFO: Request start/end
- WARNING: Rate limits, slow requests
- ERROR: Generation failures
- DEBUG: Detailed pipeline info

---

## Deployment Topologies

### Single Server (Current)
```
┌─────────────────────┐
│   Docker Host       │
│  ┌──────────────┐   │
│  │ DiffusionForge│  │
│  │    :8000      │  │
│  └──────────────┘   │
└─────────────────────┘
```

### Production (Recommended)
```
     Internet
        ↓
    [Cloudflare]
        ↓
    [Nginx/SSL]
        ↓
    [DiffusionForge]
        ↓
    [PostgreSQL] (users/auth)
```

### High Availability
```
    Load Balancer
    /    |    \
   ↓     ↓     ↓
  App1  App2  App3
   |     |     |
   └─────┴─────┘
         ↓
   Shared Storage
```

---

## Technology Choices Rationale

### Why FastAPI?
- Modern async framework
- Automatic API documentation
- Pydantic validation
- High performance
- Type hints support

### Why Stable Diffusion 2.1?
- Open source (RAIL-M license)
- Production-ready
- Good quality/speed balance
- Active community
- 5GB size (manageable)

### Why Docker?
- Consistent environments
- Easy deployment
- Isolation
- Version control
- Scalability

### Why Tailwind CSS?
- Rapid development
- Small file size
- No build step needed
- Responsive utilities
- Professional look

### Why No Database?
- Stateless design
- Simpler deployment
- No user accounts (yet)
- File-based storage sufficient
- Easy to add later

---

## Future Architecture Evolution

### Phase 2: Authentication
```
Add JWT/OAuth2
      ↓
User Management
      ↓
PostgreSQL DB
      ↓
Per-user quotas
```

### Phase 3: Advanced Features
```
Add Redis Cache
      ↓
Queue System
      ↓
WebSocket Support
      ↓
Real-time Progress
```

### Phase 4: Multi-Model
```
Model Registry
      ↓
Dynamic Model Loading
      ↓
User Model Selection
      ↓
LoRA Support
```

---

This architecture provides:
- ✅ High performance
- ✅ Scalability
- ✅ Reliability
- ✅ Security
- ✅ Maintainability
- ✅ Extensibility
