#!/usr/bin/env python3
"""
Tournament System - Development Server Manager

Simple script to manage both frontend and backend servers.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_services():
    """Start both frontend and backend services."""
    print("🚀 Starting Tournament System - Frontend and Backend")
    print("=" * 53)
    
    # Check if virtual environment is active
    if 'VIRTUAL_ENV' not in os.environ and not Path('.venv').exists():
        print("❌ Virtual environment not found. Please run:")
        print("   uv venv && uv sync")
        return
    
    try:
        print("\n🖥️ Starting Backend API Server (Port 8000)...")
        backend = subprocess.Popen([
            sys.executable, "run.py", "server", "--port", "8000"
        ], cwd=Path.cwd())
        
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)
        
        print("\n🌐 Starting Frontend Server (Port 3000)...")
        frontend = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=Path.cwd() / "frontend")
        
        print("\n✅ Both services are running!")
        print("=" * 53)
        print("🌐 Frontend: http://localhost:3000")
        print("🚀 Backend:  http://localhost:8000")
        print("📊 Health:   http://localhost:8000/health")
        print("=" * 53)
        print("\n💡 Press Ctrl+C to stop both services")
        
        # Wait for user interruption
        try:
            backend.wait()
            frontend.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend.terminate()
            frontend.terminate()
            print("✅ Services stopped.")
            
    except FileNotFoundError:
        print("❌ Python not found. Please ensure Python is installed and in PATH.")
    except Exception as e:
        print(f"❌ Error starting services: {e}")

if __name__ == "__main__":
    start_services()
