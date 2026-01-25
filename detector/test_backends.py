#!/usr/bin/env python3
"""
Test script to verify all CyberSentryAI backends are running
"""
import requests
import sys

# Test configurations
TESTS = {
    'text': {
        'url': 'http://localhost:5001/detect-text',
        'data': {
            'text': 'URGENT! Your account will be locked. Click here immediately: http://fake-bank.com'
        }
    },
    'url': {
        'url': 'http://localhost:5002/detect-url',
        'data': {
            'url': 'http://secure-login@phishing.com/verify'
        }
    },
    'image': {
        'url': 'http://localhost:5003/',
        'data': None
    }
}

def test_backend(name, config):
    """Test a single backend"""
    print(f"\n{'='*50}")
    print(f"Testing {name.upper()} Backend")
    print('='*50)
    
    try:
        if config['data']:
            response = requests.post(
                config['url'],
                json=config['data'],
                timeout=5
            )
        else:
            # Just test if server is running
            response = requests.get(config['url'], timeout=5)
        
        if response.status_code == 200:
            print(f"✅ {name.upper()} backend is running!")
            if config['data']:
                result = response.json()
                print(f"\nSample Response:")
                for key, value in result.items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"  {key}:")
                        for item in value:
                            print(f"    - {item}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"❌ {name.upper()} backend returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {name.upper()} backend at {config['url']}")
        print(f"   Make sure the backend is running: python {name}_app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing {name.upper()} backend: {str(e)}")
        return False
    
    return True

def main():
    print("\n" + "="*50)
    print("CyberSentryAI Backend Test Suite")
    print("="*50)
    
    results = {}
    
    # Test each backend
    for name, config in TESTS.items():
        results[name] = test_backend(name, config)
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name.upper():10} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All backends are running successfully!")
        print("\nYou can now open frontend.html in your browser.")
        return 0
    else:
        print("⚠️  Some backends are not running.")
        print("\nPlease start the missing backends:")
        for name, passed in results.items():
            if not passed:
                print(f"  python {name}_app.py")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
