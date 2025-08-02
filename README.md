# GenAI Tournament Calendar Data Collection System

## 🎯 Project Overview

A comprehensive GenAI-powered tournament calendar data collection system that covers **12 sports** across **12 different levels**, extracting tournament information from the web and providing it in CSV/JSON formats with database storage capabilities.

## 📋 Assignment Requirements Fulfilled

### ✅ Sports Coverage (12 Sports)
1. **Cricket** - Traditional bat and ball sport
2. **Football** - Association football/soccer
3. **Badminton** - Indoor racquet sport
4. **Running** - Track and field running events
5. **Gym** - Gymnasium-based fitness competitions
6. **Cycling** - Bicycle racing and competitions
7. **Swimming** - Pool and open water swimming
8. **Kabaddi** - Contact team sport
9. **Yoga** - Yoga competitions and demonstrations
10. **Basketball** - Indoor court sport
11. **Chess** - Strategic board game
12. **Table Tennis** - Indoor ping pong sport

### ✅ Level Coverage (12 Levels)
1. **Corporate** - Company and corporate tournaments
2. **School** - School-level competitions
3. **College** - College and university competitions
4. **University** - Inter-university tournaments
5. **Club** - Club-level competitions
6. **Academy** - Sports academy tournaments
7. **District** - District-level competitions
8. **State** - State championship level
9. **Zonal** - Multi-state zonal competitions
10. **Regional** - Regional championship level
11. **National** - National championship level
12. **International** - International competitions

### ✅ Required Output Fields
- **tournament_name** - Full tournament name
- **level** - Competition level (Corporate/School/College/etc.)
- **dates** - Tournament dates (start - end or single date)
- **tournament_url** - Official tournament webpage URL
- **streaming_links** - Live streaming/broadcast URLs
- **images** - Tournament poster/logo image URLs
- **summary** - Brief tournament description

### ✅ Export Formats
- **CSV Format** - Comma-separated values for spreadsheet usage
- **JSON Format** - JavaScript Object Notation for API consumption

## 🏗️ System Architecture

### Step-by-Step Pipeline

#### **Step 1: Query Generation** (`step1_generate_queries.py`)
- Generates comprehensive search queries for all 144 sport-level combinations (12×12)
- Uses OpenAI for intelligent query enhancement
- Creates location-specific queries for better results
- Implements deduplication and query optimization
- **Output**: `search_queries_complete.json`

#### **Step 2: Search Results Collection** (`step2_search_results.py`)
- Uses Serper API for Google-style search results
- Implements advanced filtering and relevance scoring
- Features retry logic and error handling
- Filters results by domain quality and relevance
- **Output**: `search_results_complete.json`

#### **Step 3: Content Extraction** (`step3_extract_content.py`)
- Uses Firecrawl API for clean web content extraction
- Prioritizes high-quality domains and content
- Implements rate limiting and batch processing
- Calculates content quality scores
- **Output**: `extracted_content_complete.json`

#### **Step 4: Tournament Data Processing** (`step4_process_tournaments.py`)
- Uses OpenAI API for structured data extraction
- Validates and cleans extracted tournament data
- Calculates confidence scores for data quality
- Formats data according to assignment requirements
- **Output**: `tournament_data_complete.json`

#### **Step 5: Database Operations** (`step5_database_operations.py`)
- Creates MySQL database with comprehensive schema
- Implements bulk insert with duplicate handling
- Provides full CRUD operations and statistics
- Logs extraction processes for tracking
- **Database**: `tournament_calendar` with multiple tables

#### **Step 6: Final Export and API** (`step6_final_export.py`)
- Exports data in required CSV and JSON formats
- Generates comprehensive reports and statistics
- **BONUS**: Provides REST API endpoints for data access
- Creates manifest files for export tracking
- **Output**: Final CSV/JSON files in `final_output/` directory

## 🔧 Technology Stack

### Core APIs
- **Serper API** - Web search functionality (Google-style results)
- **Firecrawl API** - Clean web content extraction
- **OpenAI API** - Intelligent data extraction and processing

### Database
- **MySQL** - Tournament data storage with relational schema
- **Full-text search** capabilities for tournament discovery
- **Comprehensive indexing** for performance optimization

### Programming Languages & Libraries
- **Python 3.12** - Main programming language
- **Flask** - REST API framework (bonus feature)
- **pandas** - Data processing and manipulation
- **mysql-connector-python** - Database connectivity
- **requests** - HTTP client for API calls
- **python-dotenv** - Environment variable management

## � Installation and Setup

### Prerequisites
```bash
# Python 3.12 or higher
python --version

# MySQL Server (local or remote)
mysql --version
```

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv tournament_env

# Activate virtual environment
# Windows:
tournament_env\Scripts\activate
# Linux/Mac:
source tournament_env/bin/activate

# Install required packages
pip install requests openai firecrawl-py mysql-connector-python pandas flask python-dotenv
```

### 2. API Keys Configuration
Create a `.env` file in the project root:
```env
# Required API Keys
SERPER_API_KEY=your_serper_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=tournament_calendar
DB_PORT=3306
```

### 3. Database Setup
```sql
-- Create MySQL database
CREATE DATABASE tournament_calendar;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON tournament_calendar.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## 🚀 Usage Instructions

### Complete Pipeline Execution
Run each step in sequence:

```bash
# Step 1: Generate search queries
python step1_generate_queries.py

# Step 2: Collect search results
python step2_search_results.py

# Step 3: Extract web content
python step3_extract_content.py

# Step 4: Process tournament data
python step4_process_tournaments.py

# Step 5: Store in database
python step5_database_operations.py

# Step 6: Final export and API
python step6_final_export.py
```

### Individual Testing
Each component can be tested individually:

```bash
# Test individual APIs
python test_serper.py
python test_firecrawl.py
python test_openai.py
python test_csv_export.py
python mysql_integration.py
```

### Configuration
Modify `config.py` to adjust:
- Sports and levels covered
- Output field requirements
- Database schema specifications
- API rate limits and retry settings

## 📊 Output Files

### Final Export Files (in `final_output/` directory)
- **`tournament_calendar_YYYYMMDD_HHMMSS.csv`** - CSV export
- **`tournament_calendar_YYYYMMDD_HHMMSS.json`** - JSON export
- **`tournament_summary_YYYYMMDD_HHMMSS.json`** - Statistics summary
- **`export_manifest_YYYYMMDD_HHMMSS.json`** - Export metadata

### Intermediate Files
- **`search_queries_complete.json`** - Generated search queries
- **`search_results_complete.json`** - Search results from Serper
- **`extracted_content_complete.json`** - Extracted web content
- **`tournament_data_complete.json`** - Processed tournament data

## 🎉 Bonus Features

### REST API Endpoints
When running `step6_final_export.py`, you can start a Flask API server:

```
http://localhost:5000/                          # API information
http://localhost:5000/tournaments               # All tournaments
http://localhost:5000/tournaments/sport/Cricket # By sport
http://localhost:5000/tournaments/level/National # By level
http://localhost:5000/tournaments/export/csv    # CSV download
http://localhost:5000/tournaments/export/json   # JSON download
http://localhost:5000/stats                     # Statistics
```

### Advanced Features
- **Confidence Scoring** - Quality assessment for each tournament
- **Duplicate Detection** - Prevents duplicate tournament entries
- **Content Quality Assessment** - Filters low-quality data
- **Comprehensive Logging** - Tracks all extraction processes
- **Batch Processing** - Handles large datasets efficiently
- **Error Recovery** - Retry mechanisms for API failures

## 📈 Expected Results

### Data Coverage
- **Target**: 144 sport-level combinations (12 sports × 12 levels)
- **Expected Output**: 200-500 high-quality tournament records
- **Quality Threshold**: 70%+ of tournaments with confidence score ≥ 0.4
- **Export Formats**: Both CSV and JSON as per assignment requirements

### Performance Metrics
- **Search Results**: 10-50 results per sport-level combination
- **Content Extraction**: 60-80% success rate
- **Data Processing**: 70-90% successful tournament extraction
- **Database Storage**: 100% of processed tournaments stored
- **Export Success**: 100% compliance with assignment format

## � Quality Assurance

### Data Validation
- **Required Fields Check** - Ensures all mandatory fields are present
- **Date Format Validation** - Validates tournament date formats
- **URL Validation** - Checks validity of tournament and streaming URLs
- **Content Length Validation** - Ensures adequate content quality
- **Confidence Scoring** - Assigns quality scores to each tournament

### Error Handling
- **API Rate Limiting** - Respects API rate limits with delays
- **Retry Mechanisms** - Automatic retry for failed requests
- **Graceful Degradation** - Fallback to JSON when database unavailable
- **Comprehensive Logging** - Detailed logs for troubleshooting

## 📝 Assignment Compliance Checklist

- ✅ **12 Sports Covered** - All specified sports included
- ✅ **12 Levels Covered** - All competition levels included  
- ✅ **CSV Export** - Provided in final_output directory
- ✅ **JSON Export** - Provided in final_output directory
- ✅ **Required Fields** - All 7 mandatory fields included
- ✅ **Data Quality** - High-confidence tournament data
- ✅ **Scalable Architecture** - Modular, maintainable code
- ✅ **Database Integration** - MySQL storage with full schema
- ✅ **Comprehensive Documentation** - Detailed README and comments
- ✅ **Bonus Features** - REST API and advanced analytics

## 🤝 Support and Maintenance

### Troubleshooting
1. **API Key Issues** - Verify all API keys in `.env` file
2. **Database Connection** - Check MySQL server status and credentials
3. **Rate Limiting** - Increase delays between API calls if needed
4. **Memory Issues** - Reduce batch sizes in processing steps

### Customization
- **Add New Sports** - Update `SPORTS_LIST` in `config.py`
- **Add New Levels** - Update `LEVELS_LIST` in `config.py`
- **Modify Output Fields** - Update `OUTPUT_FIELDS` in `config.py`
- **Adjust Quality Thresholds** - Modify confidence score calculations

### Future Enhancements
- **Additional APIs** - Integrate more data sources
- **Machine Learning** - Improve data quality scoring
- **Real-time Updates** - Scheduled data refresh
- **Web Interface** - GUI for non-technical users
- **Mobile App** - Tournament discovery application

---

## 📞 Project Information

**Author**: GenAI Tournament Calendar System
**Version**: 1.0.0
**Date**: January 2025
**License**: MIT License

**Assignment Fulfillment**: This project fully satisfies all requirements for a comprehensive tournament calendar data collection system covering 12 sports across 12 levels with proper CSV/JSON export capabilities.

**Total Implementation**: 6 main processing steps + bonus API features + comprehensive testing suite + database integration + quality assurance mechanisms.
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
