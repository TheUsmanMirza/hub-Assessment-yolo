#!/usr/bin/env python3
"""
Test runner for the YOLO backend application.
Runs simplified tests for the actual endpoints defined in router.py.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the simplified endpoint tests."""
    print("🧪 Running Backend Endpoint Tests")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Install test dependencies
    print("Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"
        ], check=True, capture_output=True)
        print("Test dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install test dependencies: {e}")
        print(f"Error output: {e.stderr.decode()}")
        return False
    
    # Run the simplified endpoint tests
    print("\nRunning endpoint tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_simple_endpoints.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=True)
        
        print("\nAll endpoint tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nSome tests failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error running tests: {e}")
        return False

def run_specific_test(test_name):
    """Run a specific test or test class."""
    print(f"Running specific test: {test_name}")
    print("=" * 50)
    
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            f"tests/test_simple_endpoints.py::{test_name}",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=True)
        
        print(f"\nTest {test_name} passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nTest {test_name} failed with exit code: {e.returncode}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all simplified endpoint tests
        success = run_tests()
    
    sys.exit(0 if success else 1) 