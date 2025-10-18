#!/usr/bin/env python3
import pytest
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ == "__main__":
    # Run tests with verbose output
    exit_code = pytest.main([
        "-v",
        "--tb=short",
        "--color=yes",
        os.path.dirname(__file__)
    ])
    
    sys.exit(exit_code)
