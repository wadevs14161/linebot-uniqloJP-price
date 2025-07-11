#!/usr/bin/env python3
"""
Test script to verify the unified app works correctly
"""

import requests
import time
import sys
import subprocess

def wait_for_app(host="localhost", port=5000, timeout=30):
    """Wait for the app to become available"""
    print(f"Waiting for app to start on {host}:{port}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://{host}:{port}/", timeout=2)
            if response.status_code == 200:
                print("✅ App is running and responding!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("❌ App failed to start within timeout")
    return False

def test_endpoints():
    """Test various endpoints"""
    base_url = "http://localhost:5000"
    
    tests = [
        {
            "name": "Home page",
            "url": f"{base_url}/",
            "expected_status": 200
        },
        {
            "name": "Health check",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "API status",
            "url": f"{base_url}/api/status",
            "expected_status": 200
        }
    ]
    
    print("\nTesting endpoints...")
    for test in tests:
        try:
            response = requests.get(test["url"], timeout=5)
            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']}: OK")
            else:
                print(f"❌ {test['name']}: Expected {test['expected_status']}, got {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: Request failed - {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "docker":
        # Test with Docker
        print("Testing with Docker...")
        print("Starting container...")
        
        # Stop any existing containers
        subprocess.run(["docker", "stop", "uniqlo-test"], capture_output=True)
        subprocess.run(["docker", "rm", "uniqlo-test"], capture_output=True)
        
        # Start new container with minimal environment
        cmd = [
            "docker", "run", "-d", "--name", "uniqlo-test",
            "-p", "5000:5000",
            "-e", "LINE_CHANNEL_SECRET=test_secret",
            "-e", "LINE_CHANNEL_ACCESS_TOKEN=test_token",
            "uniqlo-app"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to start Docker container: {result.stderr}")
            return False
        
        container_id = result.stdout.strip()
        print(f"Container started: {container_id}")
        
        try:
            if wait_for_app():
                test_endpoints()
                return True
            else:
                # Show container logs for debugging
                logs_result = subprocess.run(["docker", "logs", "uniqlo-test"], 
                                           capture_output=True, text=True)
                print("Container logs:")
                print(logs_result.stdout)
                print(logs_result.stderr)
                return False
        finally:
            # Cleanup
            subprocess.run(["docker", "stop", "uniqlo-test"], capture_output=True)
            subprocess.run(["docker", "rm", "uniqlo-test"], capture_output=True)
    
    else:
        # Test local development server
        print("Testing local development server...")
        print("Make sure to start the app first: python app.py")
        
        if wait_for_app():
            test_endpoints()
            return True
        else:
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
