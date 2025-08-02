#!/usr/bin/env python3
"""
API Module Runner

Run the Tournament Calendar API server using UV.
"""

from api import create_app

def main():
    """Run the Flask application."""
    app = create_app()
    
    print("🚀 Starting Tournament Calendar API Server")
    print("=" * 50)
    print(f"📡 Server: http://localhost:5000")
    print(f"📊 Health: http://localhost:5000/health")
    print(f"🔧 Version: {app.config.get('VERSION', '3.0.0')}")
    print("=" * 50)
    
    # Run in development mode
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

if __name__ == '__main__':
    main()
