# API Documentation

Complete API reference for the AI Image Generator service.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. Rate limiting is applied per IP address.

## Rate Limits

- **10 requests per minute** per IP address
- Returns HTTP 429 (Too Many Requests) when limit is exceeded

## Endpoints

### 1. Health Check

Check the health and status of the service.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "model_loaded": true,
  "timestamp": "2026-01-25T14:30:00.000Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Generate Image

Generate an image from a text prompt.

**Endpoint:** `POST /generate`

**Request Body:**
```json
{
  "prompt": "a serene mountain landscape at sunset, professional photography",
  "negative_prompt": "blurry, low quality, distorted",
  "num_inference_steps": 30,
  "guidance_scale": 7.5,
  "seed": 42,
  "width": 512,
  "height": 512
}
```

**Parameters:**

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `prompt` | string | Yes | - | 1-500 chars | Text description of desired image |
| `negative_prompt` | string | No | "" | 0-500 chars | Things to avoid in the image |
| `num_inference_steps` | integer | No | 30 | 10-50 | Number of denoising steps (higher = better quality, slower) |
| `guidance_scale` | float | No | 7.5 | 1.0-20.0 | How closely to follow the prompt (higher = more literal) |
| `seed` | integer | No | random | 0-2^32-1 | Random seed for reproducibility |
| `width` | integer | No | 512 | 256/512/768 | Image width in pixels |
| `height` | integer | No | 512 | 256/512/768 | Image height in pixels |

**Response:**
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",
  "seed": 42,
  "generation_time": 5.23,
  "is_safe": true,
  "metadata": {
    "prompt": "a serene mountain landscape at sunset...",
    "negative_prompt": "blurry, low quality, distorted",
    "steps": 30,
    "guidance_scale": 7.5,
    "width": 512,
    "height": 512,
    "device": "cuda"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `image` | string | Base64-encoded PNG image |
| `seed` | integer | Random seed used for generation |
| `generation_time` | float | Time taken to generate image (seconds) |
| `is_safe` | boolean | Whether image passed safety check |
| `metadata` | object | Generation parameters and info |

**Status Codes:**
- `200 OK` - Image generated successfully
- `422 Unprocessable Entity` - Invalid parameters
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Generation failed

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a beautiful sunset over the ocean",
    "num_inference_steps": 25,
    "guidance_scale": 7.5
  }'
```

**Example Python:**
```python
import requests
import base64

response = requests.post('http://localhost:8000/generate', json={
    'prompt': 'a beautiful sunset over the ocean',
    'num_inference_steps': 25,
    'guidance_scale': 7.5
})

if response.status_code == 200:
    data = response.json()
    
    # Decode and save image
    image_data = base64.b64decode(data['image'])
    with open('output.png', 'wb') as f:
        f.write(image_data)
    
    print(f"Generated in {data['generation_time']:.2f}s")
    print(f"Seed: {data['seed']}")
else:
    print(f"Error: {response.status_code}")
```

**Example JavaScript:**
```javascript
fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'a beautiful sunset over the ocean',
    num_inference_steps: 25,
    guidance_scale: 7.5
  })
})
.then(response => response.json())
.then(data => {
  const img = document.createElement('img');
  img.src = `data:image/png;base64,${data.image}`;
  document.body.appendChild(img);
  
  console.log(`Generated in ${data.generation_time}s`);
  console.log(`Seed: ${data.seed}`);
})
.catch(error => console.error('Error:', error));
```

---

### 3. Get Prompt Suggestions

Get curated example prompts organized by category.

**Endpoint:** `GET /prompts/suggestions`

**Response:**
```json
{
  "suggestions": [
    {
      "category": "Portraits",
      "prompts": [
        "portrait of a wise old wizard...",
        "professional headshot of a female CEO..."
      ]
    },
    {
      "category": "Landscapes",
      "prompts": [
        "majestic mountain landscape at sunset...",
        "serene Japanese garden..."
      ]
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Suggestions retrieved successfully

---

### 4. Get Model Information

Get information about the loaded model and capabilities.

**Endpoint:** `GET /model/info`

**Response:**
```json
{
  "model_id": "stabilityai/stable-diffusion-2-1-base",
  "device": "cuda",
  "loaded": true,
  "capabilities": {
    "max_resolution": "512x512",
    "attention_slicing": true,
    "vae_slicing": true
  },
  "limits": {
    "max_prompt_length": 500,
    "rate_limit": "10 requests/minute",
    "inference_steps_range": "10-50",
    "guidance_scale_range": "1.0-20.0"
  }
}
```

**Status Codes:**
- `200 OK` - Model info retrieved successfully

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**429 Too Many Requests**
```json
{
  "detail": "Rate limit exceeded. Maximum 10 requests per minute."
}
```

**500 Internal Server Error**
```json
{
  "detail": "Generation failed: CUDA out of memory"
}
```

---

## Best Practices

### Prompt Engineering

**Good Prompts:**
- Be specific and descriptive
- Include style keywords (e.g., "oil painting", "photorealistic", "anime style")
- Mention lighting and mood
- Specify quality (e.g., "highly detailed", "8k", "professional")

**Example:**
```
"a serene mountain landscape at golden hour, snow-capped peaks, 
alpine lake reflection, professional landscape photography, 
highly detailed, 8k resolution"
```

**Negative Prompts:**
Common things to exclude:
```
"blurry, low quality, distorted, ugly, deformed, watermark, 
text, signature, cropped"
```

### Parameter Tuning

**Inference Steps:**
- 10-15: Fast preview (lower quality)
- 20-25: Good balance
- 30-40: High quality (recommended)
- 40-50: Maximum quality (slow)

**Guidance Scale:**
- 3.0-5.0: More creative, varied results
- 7.0-8.0: Balanced (recommended)
- 10.0-15.0: Very literal to prompt
- 15.0+: May reduce quality

**Resolution:**
- 256x256: Fast preview
- 512x512: Standard quality (recommended)
- 768x768: High detail (slow, requires more VRAM)

### Performance Tips

1. **Use fixed seeds** for reproducible results
2. **Start with lower steps** (20-25) for testing
3. **Use 512x512** for best quality/speed balance
4. **Batch similar requests** if possible
5. **Monitor generation times** and adjust parameters

### Safety

1. **Content Filtering**: All images pass through NSFW filter
2. **Rate Limiting**: Respect the 10 requests/minute limit
3. **Error Handling**: Always handle potential errors
4. **Validation**: Validate inputs before sending

---

## WebSocket API (Future)

*Coming soon: Real-time progress updates via WebSocket*

---

## SDK Examples

### Python SDK Wrapper

```python
import requests
import base64
from pathlib import Path

class ImageGenerator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def generate(self, prompt, **kwargs):
        """Generate an image from a prompt"""
        payload = {"prompt": prompt, **kwargs}
        response = requests.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def save_image(self, image_data, filename):
        """Save base64 image to file"""
        image_bytes = base64.b64decode(image_data)
        Path(filename).write_bytes(image_bytes)
    
    def health_check(self):
        """Check service health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
generator = ImageGenerator()

# Check if service is healthy
health = generator.health_check()
print(f"Service status: {health['status']}")

# Generate image
result = generator.generate(
    prompt="a beautiful sunset over the ocean",
    num_inference_steps=30,
    guidance_scale=7.5
)

# Save image
generator.save_image(result['image'], 'output.png')
print(f"Generated in {result['generation_time']:.2f}s with seed {result['seed']}")
```

---

## Changelog

### Version 1.0.0 (2026-01-25)
- Initial release
- Stable Diffusion 2.1 integration
- GPU and CPU support
- NSFW filtering
- Rate limiting
- Web interface

---

## Support

For issues and questions:
- Check the main [README.md](README.md)
- Review [PERFORMANCE.md](PERFORMANCE.md) for optimization tips
- Open an issue on GitHub

---

**Last Updated:** 2026-01-25  
**API Version:** 1.0.0
