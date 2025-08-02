# 🏆 GenAI Tournament Calendar System - Comprehensive API Edition

## 🎯 Project Overview

An advanced AI-powered tournament data extraction system with **comprehensive API server functionality**. The system provides both batch processing and real-time API endpoints, leveraging cutting-edge APIs (Firecrawl, Serper, OpenAI) for tournament discovery, extraction, and processing. Perfect for frontend applications requiring tournament data.

## 🚀 **NEW: Comprehensive API Server**

### 🌟 **Two Execution Modes**

#### **1. API Server Mode (Recommended for Frontend)**
```bash
python api_server.py
```
- **Real-time API endpoints** for frontend integration
- **Two processing approaches**: Quick search + Comprehensive processing
- **Automatic file exports** (CSV/JSON)
- **CORS enabled** for web applications
- **Complete main.py functionality** accessible via API

#### **2. Batch Processing Mode (Traditional)**
```bash
python main.py  
```
- **One-time bulk processing** for complete datasets
- **Research and analysis** workflows
- **Scheduled batch jobs**

## 🔗 **API Endpoints**

### **📍 Quick Search Endpoint**
```http
GET /search?sport=Cricket&level=International
```
- **Purpose**: Fast, responsive frontend interactions
- **Processing**: Uses all available queries for comprehensive coverage
- **Features**: Complete pipeline + optional file export
- **Response**: JSON with tournament data + export files

### **📍 Comprehensive Processing Endpoint**
```http
GET /comprehensive?sport=Cricket&export=true
```
- **Purpose**: Complete dataset generation (identical to main.py)
- **Processing**: Full main.py workflow - all queries, all URLs
- **Features**: Guaranteed file export + complete processing pipeline
- **Response**: Comprehensive JSON with detailed statistics

### **📍 Health Check & Documentation**
```http
GET /health          # Service status
GET /                # API documentation
```

## ✨ Key Features

### 🎯 **Comprehensive API Integration**
- **Frontend-Ready API** - CORS enabled REST endpoints
- **Real-time Processing** - On-demand tournament extraction
- **File Export API** - Automatic CSV/JSON generation
- **Complete Pipeline** - Query→Search→Extract→Process→Filter→Export

### 🔄 **Dual Processing Approaches**
- **Quick Search** - Optimized for speed and frontend responsiveness
- **Comprehensive** - Full main.py functionality with maximum coverage
- **Flexible Configuration** - Choose approach based on use case

### ✨ Advanced Schema-Based Extraction
- **Firecrawl API Integration** - Clean, structured content extraction
- **Schema-Driven Processing** - Consistent data structure and quality
- **All URLs Processing** - No artificial limits (max_urls=None)

### 🎯 Smart Tournament Discovery
- **Comprehensive Query Coverage** - Uses all available sport-specific queries
- **Serper API Integration** - Google-quality search results
- **Relevance Scoring** - Prioritizes high-quality sources

### 📅 Intelligent Date Filtering
- **Recent & Future Focus** - Automatically filters tournaments to include:
  - Past 6 months tournaments (for reference)
  - All upcoming/future tournaments
- **Date Parsing & Validation** - Handles multiple date formats intelligently

### 🔄 Complete Automation Pipeline
- **End-to-End Processing** - Single command execution from search to export
- **Batch Processing** - Efficient handling of multiple tournaments
- **Deduplication** - Removes duplicate tournaments automatically
- **Error Recovery** - Robust error handling and retry mechanisms

## 🏗️ System Architecture

### **API Server Architecture (New)**
```
Frontend Request → API Endpoint → Complete Processing Pipeline → JSON Response + File Export
```

### **Traditional Batch Architecture**
```
Query Generation → Web Search → Content Extraction → Data Processing → Export
```

### **Core Components**

#### **1. API Server (api_server.py)**
- **Flask-based REST API** with comprehensive tournament processing
- **Two endpoints**: `/search` (quick) and `/comprehensive` (full)
- **CORS enabled** for frontend integration
- **Automatic file export** functionality

#### **2. Batch Processor (main.py)**
- **Traditional workflow** for bulk data processing
- **Research and analysis** use cases
- **Scheduled processing** capabilities

#### **3. Core Processing Pipeline**
- **Query Generation** - Sport-specific search queries
- **Search Collection** - Serper API integration
- **Content Extraction** - Firecrawl schema-based extraction
- **Data Processing** - Deduplication and validation
- **Export System** - CSV/JSON file generation

## 🔧 Technology Stack

### Core APIs
- **🔍 Serper API** - Advanced web search with Google-quality results
- **🌐 Firecrawl API** - Schema-based content extraction and web scraping
- **🤖 OpenAI API** - AI-powered query enhancement and data processing

### Web Framework
- **🌐 Flask** - Lightweight web framework for API server
- **🔄 Flask-CORS** - Cross-origin resource sharing for frontend integration
- **📊 JSON Response** - RESTful API responses

### Programming & Libraries
- **🐍 Python 3.12+** - Main programming language
- **📊 pandas** - Data processing and manipulation
- **🌐 requests** - HTTP client for API interactions
- **⚙️ python-dotenv** - Environment variable management
- **📁 pathlib** - Modern path handling

## ⚡ Quick Start

### 1. Prerequisites
```bash
# Python 3.12 or higher
python --version
```

### 2. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd tournament-calendar

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Configuration
Create a `.env` file in the project root:
```env
# Required API Keys
SERPER_API_KEY=your_serper_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. **Choose Your Execution Mode**

#### **🚀 API Server Mode (Recommended)**
```bash
# Start the API server
python api_server.py

# Server will start at http://localhost:8000
# API Documentation: http://localhost:8000/
```

#### **📊 Batch Processing Mode**
```bash
# Execute the complete pipeline
python main.py
```

## 🌐 **Frontend Integration**

### **JavaScript/React Usage**
```javascript
// Quick search for immediate results
const quickSearch = async (sport, level) => {
  const response = await fetch(
    `http://localhost:8000/search?sport=${sport}&level=${level}`
  );
  return response.json();
};

// Comprehensive processing (full main.py functionality)
const comprehensiveProcessing = async (sport) => {
  const response = await fetch(
    `http://localhost:8000/comprehensive?sport=${sport}&export=true`
  );
  return response.json();
};

// Example usage
const tournaments = await quickSearch('Cricket', 'International');
console.log(`Found ${tournaments.tournaments.length} tournaments`);
```

### **API Response Structure**
```json
{
  "status": "success",
  "sport": "Cricket",
  "tournaments": [...],
  "metadata": {
    "total_found": 15,
    "queries_used": 4,
    "search_results": 32,
    "extraction_method": "schema-based",
    "timestamp": "2025-08-02T..."
  },
  "export_info": {
    "csv_file": "cricket_tournaments_api.csv",
    "json_file": "cricket_tournaments_api.json",
    "export_timestamp": "2025-08-02T..."
  }
}
```

## 📊 Output Structure

### Tournament Data Fields
Each extracted tournament contains:
- **tournament_name** - Official tournament name
- **level** - Competition level (International/National/etc.)
- **start_date** - Tournament start date (YYYY-MM-DD format)
- **end_date** - Tournament end date (YYYY-MM-DD format)
- **venue** - Tournament location/venue
- **tournament_url** - Official tournament website
- **streaming_links** - Live streaming URLs (if available)
- **images** - Tournament poster/logo URLs
- **summary** - Brief tournament description
- **confidence_score** - Data quality assessment (0.0-1.0)

### **File Exports**
Both API endpoints automatically generate:
- **📄 CSV File** - `{sport}_tournaments_api.csv` or `{sport}_comprehensive.csv`
- **📋 JSON File** - `{sport}_tournaments_api.json` or `{sport}_comprehensive.json`
- **📊 Manifest** - Export metadata and statistics

## 🎯 **Use Case Scenarios**

### **1. Frontend Web Application**
```bash
# Start API server
python api_server.py

# Frontend calls /search for real-time results
# Frontend calls /comprehensive for complete datasets
```

### **2. Data Analysis & Research**
```bash
# Use comprehensive API endpoint
curl "http://localhost:8000/comprehensive?sport=Cricket&export=true"

# Or traditional batch processing
python main.py
```

### **3. Scheduled Data Updates**
```bash
# API server can run continuously
# Frontend triggers /comprehensive on schedule
# Files automatically updated in final_output/
```

## 🔄 **Processing Pipeline Comparison**

### **API Server (/search endpoint)**
```
1. Generate sport-specific queries (all available)
2. Collect search results (8 per query)  
3. Extract tournaments (all URLs, schema-based)
4. Process & deduplicate
5. Filter recent/future tournaments
6. Export to files (optional)
7. Return JSON response
```

### **API Server (/comprehensive endpoint)**
```
1. Generate comprehensive queries (identical to main.py)
2. Collect all search results (8 per query)
3. Extract tournaments (all URLs, no limits)
4. Complete processing pipeline
5. Filter recent/future tournaments  
6. Export to files (guaranteed)
7. Return comprehensive JSON with statistics
```

### **Batch Processing (main.py)**
```
1. Generate comprehensive queries
2. Collect all search results
3. Extract tournaments (all URLs)
4. Complete processing pipeline
5. Filter recent/future tournaments
6. Export to final_output/ directory
```

## 🔍 Troubleshooting

### **API Server Issues**

**Server Won't Start**
```bash
❌ Service initialization error: Invalid Serper API key
💡 Solution: Verify all API keys are set correctly in .env file
```

**API Requests Failing**
```bash
❌ CORS Error in Frontend
💡 Solution: CORS is enabled - check if server is running on port 8000
```

**No Tournament Data**
```bash
❌ No tournaments could be extracted from search results
💡 Solution: Check API rate limits and Firecrawl API status
```

### **Batch Processing Issues**

**API Key Errors**
```bash
❌ Configuration error: Missing SERPER_API_KEY
💡 Solution: Verify all API keys are set in .env file
```

**Processing Failures**
```bash
❌ No tournament data was successfully extracted
💡 Solution: Check API rate limits and internet connectivity
```

## 🚀 Future Enhancements

### Planned API Features
- **🔐 Authentication** - API key-based access control
- **📊 Rate Limiting** - Request throttling and usage tracking
- **🔄 Webhooks** - Real-time notifications for data updates
- **🗄️ Database Integration** - Persistent storage and caching

### Architecture Improvements
- **⚡ Caching System** - Redis-based response caching
- **🔄 Background Jobs** - Async processing for large requests
- **📈 Monitoring** - API performance and usage analytics
- **🌐 Multi-Sport Support** - Expanded sports coverage

### Frontend Enhancements
- **🎨 Admin Dashboard** - Tournament management interface
- **📱 Mobile API** - Optimized mobile responses
- **🔍 Advanced Filtering** - Date range and location filters
- **📊 Analytics** - Tournament trends and statistics

## 📋 **Command Reference**

### **API Server Commands**
```bash
# Start comprehensive API server
python api_server.py

# Check server status
curl http://localhost:8000/health

# Quick tournament search
curl "http://localhost:8000/search?sport=Cricket&level=International"

# Comprehensive processing
curl "http://localhost:8000/comprehensive?sport=Cricket&export=true"
```

### **Batch Processing Commands**
```bash
# Traditional batch processing
python main.py

# Check system requirements
python --version

# View batch results
ls final_output/
```

## 📊 **System Information**

**Current Version**: 3.0.0 (Comprehensive API Edition)
**Last Updated**: August 2025
**License**: Private Project

**Key Improvements in v3.0**:
- 🆕 **Comprehensive API Server** - Full main.py functionality via API
- 🆕 **Frontend Integration** - CORS-enabled REST endpoints
- 🆕 **Dual Processing Modes** - Quick + Comprehensive approaches
- 🆕 **Automatic File Export** - CSV/JSON generation via API
- ✅ **Advanced schema-based extraction** using Firecrawl
- ✅ **All URLs processing** (max_urls=None)
- ✅ **Enhanced deduplication** algorithms
- ✅ **Improved error handling** and recovery

---

## 🎯 **Status: ✅ Production Ready**

**Advanced AI-powered tournament extraction system with comprehensive API server functionality. Perfect for frontend applications requiring real-time tournament data processing.**

### **Choose Your Approach:**
- **🚀 API Server**: `python api_server.py` (Frontend applications)
- **📊 Batch Processing**: `python main.py` (Data analysis & research)

**Both approaches provide identical data quality and processing capabilities!**
