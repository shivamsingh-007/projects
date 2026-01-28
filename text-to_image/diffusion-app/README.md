# AI Image Generator - Stable Diffusion 2.1

A production-ready web application for generating high-quality images from text prompts using Stable Diffusion 2.1.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## ✨ Features

- **🎨 High-Quality Image Generation**: Powered by Stable Diffusion 2.1
- **⚡ Fast Performance**: <10s generation on GPU, optimized CPU fallback
- **🎯 Professional UI**: Modern, responsive dark/light theme interface
- **📱 Mobile-Friendly**: Fully responsive design
- **🔒 Safety First**: Built-in NSFW content filtering
- **📊 Advanced Controls**: Fine-tune steps, guidance scale, resolution, and seed
- **📚 Prompt Library**: 50+ curated example prompts across 8 categories
- **💾 History**: View and download previous generations
- **🔄 One-Click Deployment**: Single Docker command to run
- **🚀 Production-Ready**: Rate limiting, error handling, health checks

## 🚀 Quick Start

### One-Command Deployment

```bash
docker run -p 8000:8000 --gpus all ai-image-generator
```

Then open http://localhost:8000 in your browser.

### Using Docker Compose (Recommended)

```bash
# Clone or download this directory
cd diffusion-app

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access the application at http://localhost:8000

## 📋 Prerequisites

### For GPU Support (Recommended)
- NVIDIA GPU with 6GB+ VRAM
- [NVIDIA Docker runtime](https://github.com/NVIDIA/nvidia-docker)
- CUDA 11.8+

### For CPU Support
- 16GB+ RAM recommended
- Generation time: 30-60s per image

## 🛠️ Installation

### Option 1: Docker (Easiest)

```bash
# Build the image
docker build -t ai-image-generator .

# Run with GPU
docker run -p 8000:8000 --gpus all ai-image-generator

# Run with CPU only
docker run -p 8000:8000 ai-image-generator
```

### Option 2: Local Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

On first run, the model (~5GB) will be automatically downloaded.

## 📖 Usage

### Web Interface

1. Open http://localhost:8000
2. Enter your text prompt (e.g., "a serene mountain landscape at sunset")
3. (Optional) Add negative prompt to avoid unwanted elements
4. (Optional) Adjust advanced settings
5. Click "Generate Image"
6. Download or save to history

### API Usage

#### Generate Image

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset over the ocean",
    "negative_prompt": "blurry, low quality",
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512
  }'
```

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Get Prompt Suggestions

```bash
curl http://localhost:8000/prompts/suggestions
```

## ⚙️ Configuration

### Environment Variables

```bash
# Model cache directory
export TRANSFORMERS_CACHE=/app/models
export HF_HOME=/app/models

# Performance
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Advanced Settings

Edit `app.py` to customize:

```python
class Config:
    MODEL_ID = "stabilityai/stable-diffusion-2-1-base"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    DEFAULT_NUM_INFERENCE_STEPS = 30
    IMAGE_SIZE = 512
    RATE_LIMIT_PER_MINUTE = 10
```

## 🏗️ Architecture

```
diffusion-app/
├── app.py                 # FastAPI backend
├── frontend/
│   └── index.html        # React frontend (single page)
├── models/               # Model cache (auto-created)
├── Dockerfile           # Container definition
├── docker-compose.yml   # Orchestration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📊 Performance Benchmarks

| Hardware | Resolution | Steps | Time |
|----------|-----------|-------|------|
| RTX 3090 | 512x512 | 30 | ~3s |
| RTX 3060 | 512x512 | 30 | ~6s |
| CPU (12-core) | 512x512 | 30 | ~45s |

## 🔧 Optimization Tips

### GPU Optimization
- Enable xformers: Automatic if available
- Use attention slicing: Enabled by default
- Reduce steps: 20-25 for faster generation
- Lower resolution: 256x256 or 384x384

### CPU Optimization
- Reduce inference steps to 20
- Use smaller resolution (256x256)
- Enable CPU threading (automatic)

## 🐛 Troubleshooting

### Automated Troubleshooter (Recommended)

We've included a **comprehensive automated troubleshooting tool** that can diagnose and fix most issues:

```bash
# Interactive mode - guides you through fixes
python troubleshoot.py

# Auto-fix mode - automatically fixes detected issues
python troubleshoot.py --auto

# Diagnostic mode - just checks for problems
python troubleshoot.py --check
```

**The script automatically detects and fixes:**
- Docker installation and configuration issues
- Container startup and runtime problems
- Port conflicts and network issues
- GPU detection and configuration
- Memory and resource problems
- Image building errors
- Model download issues
- And much more!

### Quick Fixes

**Out of Memory (GPU)**
```python
# In app.py, enable model offloading:
pipe.enable_model_cpu_offload()
```

**Slow Generation**
- Reduce `num_inference_steps` to 20
- Lower resolution to 256x256
- Check GPU availability: `nvidia-smi`

**Model Download Issues**
```bash
# Manually download models
huggingface-cli download stabilityai/stable-diffusion-2-1-base
```

**Container Won't Start**
```bash
# Remove and recreate
docker rm -f ai-image-generator
docker run -d -p 8000:8000 --gpus all ai-image-generator
```

**For complete troubleshooting guide, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

## 📝 API Reference

### POST /generate

Generate an image from a text prompt.

**Request Body:**
```json
{
  "prompt": "string (required, max 500 chars)",
  "negative_prompt": "string (optional)",
  "num_inference_steps": "integer (10-50, default: 30)",
  "guidance_scale": "float (1.0-20.0, default: 7.5)",
  "seed": "integer (optional, for reproducibility)",
  "width": "integer (256/512/768, default: 512)",
  "height": "integer (256/512/768, default: 512)"
}
```

**Response:**
```json
{
  "image": "base64_encoded_string",
  "seed": 12345,
  "generation_time": 5.23,
  "is_safe": true,
  "metadata": {
    "prompt": "...",
    "steps": 30,
    "device": "cuda"
  }
}
```

### GET /health

Check service health and status.

### GET /prompts/suggestions

Get curated prompt examples organized by category.

### GET /model/info

Get information about the loaded model and capabilities.

## 🔒 Security Features

- ✅ NSFW content filtering
- ✅ Rate limiting (10 requests/minute per client)
- ✅ Input sanitization
- ✅ Prompt length limits
- ✅ Parameter validation
- ✅ CORS protection

## 🚦 Rate Limits

- 10 requests per minute per IP address
- Configurable in `app.py`

## 📦 Model Information

- **Model**: Stable Diffusion 2.1 Base
- **Size**: ~5GB
- **Resolution**: 512x512 (native)
- **License**: CreativeML Open RAIL++-M License

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

The Stable Diffusion model is licensed under the CreativeML Open RAIL++-M License.

## 🙏 Acknowledgments

- [Stability AI](https://stability.ai/) for Stable Diffusion
- [Hugging Face](https://huggingface.co/) for the Diffusers library
- [FastAPI](https://fastapi.tiangolo.com/) framework
- [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [troubleshooting section](#-troubleshooting)
- Review [API documentation](#-api-reference)

## 🔮 Roadmap

- [ ] Multiple model support (SD 1.5, SDXL)
- [ ] Image-to-image generation
- [ ] Inpainting/outpainting
- [ ] LoRA model support
- [ ] Batch generation
- [ ] User authentication
- [ ] Persistent storage (S3, etc.)
- [ ] Advanced upscaling

---

**Made with ❤️ using Stable Diffusion, FastAPI, and React**

For the best experience, use a GPU-enabled system. Happy generating! 🎨
