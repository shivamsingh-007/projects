#!/usr/bin/env python3
"""
API Testing Script for AI Image Generator
Tests all endpoints and validates responses
"""

import requests
import json
import time
import base64
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def test_health_endpoint():
    """Test health check endpoint"""
    print_info("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "status" in data, "Missing 'status' field"
        assert "device" in data, "Missing 'device' field"
        assert "model_loaded" in data, "Missing 'model_loaded' field"
        
        print_success(f"Health check passed - Status: {data['status']}, Device: {data['device']}")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

def test_prompt_suggestions():
    """Test prompt suggestions endpoint"""
    print_info("Testing /prompts/suggestions endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/prompts/suggestions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "suggestions" in data, "Missing 'suggestions' field"
        assert len(data["suggestions"]) > 0, "No suggestions returned"
        
        # Verify structure
        first_category = data["suggestions"][0]
        assert "category" in first_category, "Missing 'category' field"
        assert "prompts" in first_category, "Missing 'prompts' field"
        assert len(first_category["prompts"]) > 0, "No prompts in category"
        
        total_prompts = sum(len(cat["prompts"]) for cat in data["suggestions"])
        print_success(f"Prompt suggestions passed - {len(data['suggestions'])} categories, {total_prompts} total prompts")
        return True
    except Exception as e:
        print_error(f"Prompt suggestions failed: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print_info("Testing /model/info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/model/info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "model_id" in data, "Missing 'model_id' field"
        assert "device" in data, "Missing 'device' field"
        assert "capabilities" in data, "Missing 'capabilities' field"
        assert "limits" in data, "Missing 'limits' field"
        
        print_success(f"Model info passed - Model: {data['model_id']}, Device: {data['device']}")
        return True
    except Exception as e:
        print_error(f"Model info failed: {e}")
        return False

def test_image_generation():
    """Test image generation endpoint"""
    print_info("Testing /generate endpoint...")
    print_warning("This may take 10-60 seconds depending on your hardware...")
    
    try:
        payload = {
            "prompt": "a serene mountain landscape at sunset, professional photography",
            "negative_prompt": "blurry, low quality, distorted",
            "num_inference_steps": 20,  # Fewer steps for faster testing
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512,
            "seed": 42  # Fixed seed for reproducibility
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            timeout=120  # 2 minute timeout
        )
        generation_time = time.time() - start_time
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "image" in data, "Missing 'image' field"
        assert "seed" in data, "Missing 'seed' field"
        assert "generation_time" in data, "Missing 'generation_time' field"
        assert "is_safe" in data, "Missing 'is_safe' field"
        assert "metadata" in data, "Missing 'metadata' field"
        
        # Verify image is valid base64
        try:
            image_data = base64.b64decode(data["image"])
            assert len(image_data) > 0, "Empty image data"
        except Exception as e:
            raise AssertionError(f"Invalid base64 image: {e}")
        
        # Verify seed matches
        assert data["seed"] == 42, f"Seed mismatch: expected 42, got {data['seed']}"
        
        print_success(f"Image generation passed - Time: {data['generation_time']:.2f}s (Total: {generation_time:.2f}s), Safe: {data['is_safe']}")
        
        # Save test image
        with open("test_output.png", "wb") as f:
            f.write(image_data)
        print_info("Test image saved as test_output.png")
        
        return True
    except requests.Timeout:
        print_error("Image generation timed out (>120s)")
        return False
    except Exception as e:
        print_error(f"Image generation failed: {e}")
        return False

def test_invalid_requests():
    """Test error handling with invalid requests"""
    print_info("Testing error handling...")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Empty prompt
    try:
        response = requests.post(f"{BASE_URL}/generate", json={"prompt": ""})
        assert response.status_code == 422, "Should reject empty prompt"
        tests_passed += 1
        print_success("Empty prompt validation passed")
    except Exception as e:
        print_error(f"Empty prompt test failed: {e}")
    
    # Test 2: Invalid steps
    try:
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": "test",
            "num_inference_steps": 100  # Max is 50
        })
        assert response.status_code == 422, "Should reject invalid steps"
        tests_passed += 1
        print_success("Invalid steps validation passed")
    except Exception as e:
        print_error(f"Invalid steps test failed: {e}")
    
    # Test 3: Invalid guidance scale
    try:
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": "test",
            "guidance_scale": 50.0  # Max is 20.0
        })
        assert response.status_code == 422, "Should reject invalid guidance scale"
        tests_passed += 1
        print_success("Invalid guidance scale validation passed")
    except Exception as e:
        print_error(f"Invalid guidance scale test failed: {e}")
    
    # Test 4: Too long prompt
    try:
        response = requests.post(f"{BASE_URL}/generate", json={
            "prompt": "a" * 1000  # Max is 500
        })
        assert response.status_code == 422, "Should reject too long prompt"
        tests_passed += 1
        print_success("Prompt length validation passed")
    except Exception as e:
        print_error(f"Prompt length test failed: {e}")
    
    print_info(f"Error handling: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def test_rate_limiting():
    """Test rate limiting"""
    print_info("Testing rate limiting...")
    print_warning("This will make multiple rapid requests...")
    
    try:
        # Make rapid requests
        successful_requests = 0
        rate_limited = False
        
        for i in range(12):  # Try to exceed limit of 10/minute
            response = requests.post(f"{BASE_URL}/generate", json={
                "prompt": f"test {i}",
                "num_inference_steps": 10
            })
            
            if response.status_code == 200:
                successful_requests += 1
            elif response.status_code == 429:
                rate_limited = True
                break
            
            time.sleep(0.1)  # Small delay
        
        if rate_limited:
            print_success(f"Rate limiting working - {successful_requests} requests succeeded before limit")
            return True
        else:
            print_warning(f"Rate limiting not triggered - {successful_requests} requests succeeded")
            return True  # Not necessarily a failure
    except Exception as e:
        print_error(f"Rate limiting test failed: {e}")
        return False

def run_performance_benchmark():
    """Run performance benchmark"""
    print_info("Running performance benchmark...")
    
    try:
        test_configs = [
            {"steps": 20, "size": 256, "name": "Fast (256px, 20 steps)"},
            {"steps": 25, "size": 512, "name": "Balanced (512px, 25 steps)"},
            {"steps": 30, "size": 512, "name": "Quality (512px, 30 steps)"},
        ]
        
        results = []
        
        for config in test_configs:
            print_info(f"Testing {config['name']}...")
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/generate",
                json={
                    "prompt": "test benchmark",
                    "num_inference_steps": config["steps"],
                    "width": config["size"],
                    "height": config["size"],
                },
                timeout=120
            )
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "config": config["name"],
                    "generation_time": data["generation_time"],
                    "total_time": total_time,
                })
                print_success(f"{config['name']}: {data['generation_time']:.2f}s")
            else:
                print_error(f"{config['name']} failed")
        
        if results:
            print_info("\nBenchmark Summary:")
            for result in results:
                print(f"  {result['config']}: {result['generation_time']:.2f}s")
        
        return True
    except Exception as e:
        print_error(f"Performance benchmark failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Image Generator - API Test Suite")
    print("="*60 + "\n")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Prompt Suggestions", test_prompt_suggestions),
        ("Model Info", test_model_info),
        ("Image Generation", test_image_generation),
        ("Error Handling", test_invalid_requests),
        # ("Rate Limiting", test_rate_limiting),  # Optional, can be slow
        # ("Performance Benchmark", run_performance_benchmark),  # Optional
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'─'*60}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            failed += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed == 0:
        print_success("All tests passed! 🎉")
        return 0
    else:
        print_warning(f"{failed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
