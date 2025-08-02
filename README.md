# GenAI Tournament Calendar - Data Collection System

A comprehensive data collection system for discovering and organizing tournament information across various sports in India using AI-powered web scraping and data extraction.

## 🎯 Project Overview

This system automatically discovers, scrapes, and structures tournament information from across the web, focusing on Indian sports tournaments at various levels (School, College, Corporate, State, National, etc.).

## 🛠️ Tech Stack

- **Python 3.12+**
- **Serper API** - Google-style search results
- **Firecrawl API** - Clean web content extraction  
- **OpenAI API** - AI-powered data extraction and structuring
- **SQLite** - Local data storage
- **Pandas** - Data processing and export

## 📋 Features

### ✅ Completed
- **Step 1**: Search query generation for sports tournaments
- **Step 2**: Web search results collection via Serper API
- **Step 3**: Web content extraction via Firecrawl API
- **API Testing**: Verified functionality of Serper and Firecrawl APIs

### 🚧 In Progress
- **Step 4**: LLM-powered tournament data extraction
- **Step 5**: Data normalization and SQLite storage
- **Step 6**: CSV/JSON export functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- API Keys for:
  - Serper API
  - Firecrawl API  
  - OpenAI API

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:Arjunheregeek/Gen-AI.git
   cd Gen-AI
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy .env.example to .env and add your API keys
   cp .env.example .env
   ```
   
   Add your API keys to `.env`:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

## 🧪 Testing

### Test Individual APIs
```bash
# Test Serper API
python test_serper.py

# Test Firecrawl API
python test_firecrawl.py
```

## 📊 Project Structure

```
Gen-AI/
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (not in repo)
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── test_serper.py          # Serper API testing
├── test_firecrawl.py       # Firecrawl API testing
├── step1_generate_queries.py    # Query generation
├── step2_search_results.py      # Search results collection
├── sample_output/          # Final output directory
└── venv/                   # Virtual environment (not in repo)
```

## 🎮 Sports Covered

- **Cricket** (✅ Tested)
- **Football** 
- **Badminton**
- **Basketball**
- **Tennis**
- **Volleyball**
- **Kabaddi**
- **Hockey**
- **Table Tennis**
- **Chess**

## 🏆 Tournament Levels

- School Level
- College Level  
- University Level
- Corporate Level
- Inter-college
- State Level
- National Level
- District Level
- Regional Level
- Amateur Level

## 📈 Development Progress

- [x] **Environment Setup** - Virtual environment, dependencies
- [x] **API Integration** - Serper and Firecrawl APIs tested and working
- [x] **Search Query Generation** - Multi-sport, multi-level query creation
- [x] **Web Search** - Automated tournament discovery via Serper
- [x] **Content Extraction** - Clean content extraction via Firecrawl
- [ ] **AI Data Extraction** - OpenAI-powered tournament detail extraction
- [ ] **Database Storage** - SQLite integration with normalized data
- [ ] **Export System** - CSV and JSON output generation
- [ ] **Full Pipeline** - End-to-end automated system

## 🔄 Workflow

1. **Generate Queries** → Create sport-specific search queries
2. **Search Web** → Find tournament pages via Serper API  
3. **Extract Content** → Get clean text via Firecrawl API
4. **Process with AI** → Extract structured data via OpenAI
5. **Store Data** → Save to SQLite database
6. **Export Results** → Generate CSV/JSON outputs

## 🤝 Contributing

This is an assignment project for GenAI internship evaluation.

## 📄 License

Private project for assignment purposes.

## 🔧 API Usage Notes

- **Free Tier Limitations**: All APIs are on free tier with rate limits
- **Content Quality**: Firecrawl provides clean markdown extraction
- **Search Accuracy**: Serper delivers Google-quality search results
- **AI Processing**: OpenAI used for structured data extraction

---

**Status**: 🚧 **Active Development** - Core APIs tested and working, proceeding with full pipeline implementation.
