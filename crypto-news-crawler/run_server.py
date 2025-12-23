#!/usr/bin/env python3
"""
run_server.py

Script to run the FastAPI server with the news UI
"""

import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CryptoNews Server Starting...")
    print("=" * 60)
    print("\n📱 Open your browser and go to:")
    print("   http://localhost:8000")
    print("\n📚 API Documentation:")
    print("   http://localhost:8000/docs")
    print("   http://localhost:8000/redoc")
    print("\n" + "=" * 60 + "\n")
    
    # Run the FastAPI app
    uvicorn.run(
        "app.api.main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
