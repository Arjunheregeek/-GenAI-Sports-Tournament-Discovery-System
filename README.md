# 🏆 Tournament System - Complete Solution

> **Organized, Essential Tournament Data Extraction & Processing System**  
> Clean architecture with API server and web interface

## 🚀 **Quick Start - One Command Setup**

### **Windows Users:**
```bash
# Double-click or run this command
start.bat
```

### **Linux/Mac Users:**
```bash
# Make executable and run
chmod +x start.sh
./start.sh
```

### **Manual Setup (Alternative):**
```bash
# 1. Activate environment
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Start Backend (Terminal 1)
python run.py server --port 8000

# 3. Start Frontend (Terminal 2)
cd frontend
python -m http.server 3000
```

## 🌐 **Access Your Services**

| Service | URL | Description |
|---------|-----|-------------|
| **🖥️ Frontend** | http://localhost:3000 | Web interface for tournament search |
| **🚀 Backend API** | http://localhost:8000 | REST API server |
| **📊 Health Check** | http://localhost:8000/health | API status |
| **📋 API Docs** | http://localhost:8000/docs | API documentation |

## ✨ **Features**

### **🎯 Web Interface (Frontend)**
- **Beautiful UI** - Clean, responsive tournament search interface
- **Real-time Search** - Instant tournament discovery by sport/level
- **Live Results** - Dynamic tournament data display
- **Mobile Friendly** - Works on all devices

### **🚀 API Server (Backend)**
- **RESTful API** - Standard HTTP endpoints
- **Tournament Search** - `/search?sport=Cricket&level=International`
- **Health Monitoring** - Service status checking
- **CORS Enabled** - Frontend integration ready

### **📊 Data Processing**
- **AI-Powered Extraction** - Firecrawl + OpenAI integration
- **Smart Filtering** - Relevance-based tournament discovery
- **Deduplication** - Automatic duplicate removal
- **Export Ready** - CSV/JSON output formats

## 🔧 **System Architecture**

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Frontend      │◄───────────────►│   Backend API   │
│   (Port 3000)   │                 │   (Port 8000)   │
│                 │                 │                 │
│ • Search UI     │                 │ • Tournament    │
│ • Results       │                 │   Processing    │
│ • Export        │                 │ • Data Export   │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │  Core System    │
                                    │                 │
                                    │ • Query Gen     │
                                    │ • Web Scraping  │
                                    │ • AI Extraction │
                                    │ • Data Process  │
                                    └─────────────────┘
```

## 📋 **API Endpoints**

### **Search Tournaments**
```http
GET /search?sport=Cricket&level=International
```
**Response:**
```json
{
  "success": true,
  "count": 25,
  "tournaments": [
    {
      "tournament_name": "ICC World Cup 2024",
      "level": "International",
      "start_date": "2024-10-01",
      "venue": "India",
      "official_url": "https://icc-cricket.com"
    }
  ]
}
```

### **Health Check**
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "timestamp": "2025-08-02T10:30:00Z"
}
```

## 🛠️ **Development**

### **Project Structure**
```
tournament_system/           # Main package
├── core/                   # Core processing
│   ├── query_generator.py  # Search query generation
│   ├── search_collector.py # Web search collection
│   ├── content_extractor.py# Content extraction
│   └── data_processor.py   # Data processing
├── api/                    # API server
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   └── models/           # Data models
├── database/              # Database operations
├── exporters/            # Data export
└── utils/               # Utilities

frontend/                  # Web interface
├── index.html            # Main UI
└── index_fixed.html     # Production UI

archive/                  # Organized old files
└── [legacy files]       # Previous versions
```

### **Environment Setup**
```bash
# Dependencies already installed via UV
pip list | findstr tournament

# Environment variables required in .env:
SERPER_API_KEY=your_key_here
FIRECRAWL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## 🔍 **Troubleshooting**

### **Services Won't Start**
```bash
# Check if ports are free
netstat -an | findstr :3000
netstat -an | findstr :8000

# Kill existing processes if needed
taskkill /f /im python.exe    # Windows
pkill -f python              # Linux/Mac
```

### **API Connection Issues**
```bash
# Test backend directly
curl http://localhost:8000/health

# Check if CORS is working
# Frontend should automatically connect to backend
```

### **Environment Issues**
```bash
# Recreate environment if needed
uv venv
uv sync

# Check Python version
python --version  # Should be 3.12+
```

## 📊 **Usage Examples**

### **Web Interface Usage**
1. Open http://localhost:3000
2. Select "Cricket" from sport dropdown
3. Select "International" from level dropdown  
4. Click "Search Tournaments"
5. View results and export data

### **API Usage (Developers)**
```javascript
// Fetch tournaments
const response = await fetch(
  'http://localhost:8000/search?sport=Cricket&level=International'
);
const data = await response.json();
console.log(`Found ${data.count} tournaments`);
```

```python
# Python API usage
import requests

response = requests.get(
    'http://localhost:8000/search',
    params={'sport': 'Cricket', 'level': 'International'}
)
tournaments = response.json()['tournaments']
```

## 🎯 **Production Deployment**

### **Backend (API Server)**
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "tournament_system.api:create_app()"
```

### **Frontend (Static Files)**
```bash
# Serve via nginx, Apache, or cloud hosting
# Point to frontend/ directory
```

## 📈 **Performance**

| Component | Performance | Notes |
|-----------|------------|-------|
| **Frontend** | ⚡ Instant | Static HTML/JS |
| **API Server** | 🚀 Fast | Flask + optimized processing |
| **Data Processing** | 🔄 Variable | Depends on API rate limits |
| **Tournament Search** | ⭐ Excellent | Cached results |

## 🔒 **Security**

- **API Keys** - Stored in .env file (not committed)
- **CORS** - Enabled for frontend integration
- **Input Validation** - Parameter sanitization
- **Rate Limiting** - Respects external API limits

## 🚀 **Next Steps**

1. **Start Services**: Run `start.bat` (Windows) or `start.sh` (Linux/Mac)
2. **Open Frontend**: Visit http://localhost:3000
3. **Search Tournaments**: Use the web interface
4. **Integrate APIs**: Use endpoints for your applications
5. **Export Data**: Download results in CSV/JSON

---

## 📝 **Version Information**

- **Version**: 4.0.0 (Clean Architecture Edition)
- **Python**: 3.12.6
- **Package Manager**: UV (ultra-fast)
- **Last Updated**: August 2, 2025

**🎉 Your tournament system is ready to use!**
