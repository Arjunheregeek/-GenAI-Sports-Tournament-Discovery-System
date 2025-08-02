# Tournament Calendar System - Modular Structure

A comprehensive, modular Python package for collecting and managing tournament calendar information across 12 sports and 12 competition levels using AI-powered data extraction.

## 🏗️ Architecture Overview

This system follows a professional modular architecture with clear separation of concerns:

```
src/tournament_calendar/
├── core/                   # Core system components
│   ├── config.py          # Configuration management
│   └── pipeline.py        # Main pipeline orchestrator
├── extractors/            # Data extraction modules
│   ├── queries.py         # Query generation
│   ├── search.py          # Search data collection
│   └── content.py         # Content extraction
├── processors/            # Data processing modules
│   └── data_processor.py  # Data cleaning and processing
├── database/              # Database operations
│   └── manager.py         # Database management
├── exporters/            # Data export modules
│   └── exporter.py       # CSV/JSON export functionality
├── api/                  # Web API (bonus feature)
│   └── app.py            # Flask REST API
└── cli.py                # Command-line interface
```

## 🚀 Quick Start

### Installation

1. **Clone and navigate to the repository:**
   ```powershell
   git checkout feature/modular-structure
   cd path/to/tournament-calendar
   ```

2. **Install the package in development mode:**
   ```powershell
   pip install -e .
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```powershell
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your API keys
   notepad .env
   ```

### Configuration

Create a `.env` file with your API keys:

```env
# Required API Keys
SERPER_API_KEY=your_serper_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (optional - defaults to localhost)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tournament_calendar
DB_USER=root
DB_PASSWORD=your_mysql_password
```

## 🎯 Usage

### Command Line Interface

The system provides a comprehensive CLI for easy operation:

```powershell
# Run the complete pipeline
python -m tournament_calendar.cli run

# Run a single step
python -m tournament_calendar.cli step 1

# Skip specific steps
python -m tournament_calendar.cli run --skip-steps 2 4

# Check system status
python -m tournament_calendar.cli status

# Validate configuration
python -m tournament_calendar.cli config --validate

# Show current configuration
python -m tournament_calendar.cli config --show
```

### Python API

Use the system programmatically:

```python
from tournament_calendar.core.pipeline import TournamentPipeline
from tournament_calendar.core.config import config

# Initialize pipeline
pipeline = TournamentPipeline()

# Run complete pipeline
summary = pipeline.run_full_pipeline()
print(f"Completed {summary['steps_completed']}/{summary['total_steps']} steps")

# Run individual steps
pipeline.run_single_step(1)  # Query generation
pipeline.run_single_step(2)  # Search collection
# ... continue with other steps

# Access configuration
print(f"Configured for {len(config.SPORTS_LIST)} sports")
print(f"Across {len(config.LEVELS_LIST)} competition levels")
```

## 📊 Pipeline Steps

The system operates through 6 distinct steps:

### Step 1: Query Generation
- **Module**: `extractors.queries`
- **Purpose**: Generates optimized search queries for each sport/level combination
- **Output**: 144 unique search queries (12 sports × 12 levels)

### Step 2: Search Collection  
- **Module**: `extractors.search`
- **Purpose**: Executes searches using Serper API
- **Output**: Raw search results for each query

### Step 3: Content Extraction
- **Module**: `extractors.content`
- **Purpose**: Extracts detailed content from search results using Firecrawl API
- **Output**: Full webpage content for tournament information

### Step 4: Data Processing
- **Module**: `processors.data_processor`
- **Purpose**: Processes and structures extracted content using OpenAI API
- **Output**: Structured tournament data with standardized fields

### Step 5: Database Operations
- **Module**: `database.manager`
- **Purpose**: Stores processed data in MySQL database
- **Output**: Persistent tournament calendar database

### Step 6: Export & API
- **Module**: `exporters.exporter` & `api.app`
- **Purpose**: Exports data to CSV/JSON and provides REST API access
- **Output**: Exportable files and web API endpoints

## 🗄️ Database Schema

The system uses a comprehensive MySQL schema:

```sql
-- Sports and levels reference tables
CREATE TABLE sports (id, name, category, popularity_score);
CREATE TABLE levels (id, name, skill_level, age_group);

-- Main tournament data
CREATE TABLE tournaments (
    id, tournament_name, sport_id, level_id,
    start_date, end_date, location, country,
    prize_money, participant_count, 
    registration_deadline, website_url,
    created_at, updated_at
);

-- Data tracking and analytics
CREATE TABLE data_collection_log (id, step, status, timestamp, details);
CREATE TABLE search_queries (id, sport, level, query_text, results_count);
```

## 🧪 Testing

The system includes comprehensive testing:

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=tournament_calendar

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m api         # API tests only

# Run tests for specific modules
pytest tests/test_config.py
pytest tests/test_pipeline.py
```

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **API Tests**: External API integration testing
- **Database Tests**: Database operation validation

## 📈 Monitoring & Analytics

### Execution Tracking
The system provides detailed execution monitoring:

```python
# Get execution summary
summary = pipeline.run_full_pipeline()
print(f"Success rate: {summary['success_rate']}%")
print(f"Execution time: {summary['execution_time']}")
print(f"Errors: {len(summary['errors'])}")

# Step-by-step status
for step, status in summary['step_status'].items():
    print(f"{step}: {'✅' if status else '❌'}")
```

### Data Quality Metrics
- **Coverage**: Tracks tournaments found per sport/level
- **Completeness**: Monitors required field population
- **Freshness**: Tracks data collection timestamps
- **Accuracy**: Validates data format and consistency

## 🔧 Configuration Management

### Sports Configuration
Currently configured for 12 major sports:
- Soccer, Basketball, Tennis, Baseball, American Football
- Ice Hockey, Volleyball, Golf, Swimming, Athletics
- Boxing, MMA

### Competition Levels
Supports 12 competition levels:
- Professional, Semi-Professional, Amateur, Youth
- College, High School, Regional, National
- International, Olympic, Paralympic, Masters

### Customization
Easily customize the system for different sports/levels:

```python
from tournament_calendar.core.config import TournamentConfig

# Custom configuration
custom_config = TournamentConfig(
    sports_list=['tennis', 'golf', 'swimming'],
    levels_list=['professional', 'amateur', 'youth']
)
```

## 🌐 API Endpoints (Bonus Feature)

The Flask REST API provides programmatic access:

```
GET /api/tournaments                 # All tournaments
GET /api/tournaments/sport/{sport}   # By sport
GET /api/tournaments/level/{level}   # By level
GET /api/sports                      # Available sports
GET /api/levels                      # Available levels
GET /api/stats                       # Collection statistics
```

### API Usage Examples
```python
import requests

# Get all tournaments
response = requests.get('http://localhost:5000/api/tournaments')
tournaments = response.json()

# Get soccer tournaments
response = requests.get('http://localhost:5000/api/tournaments/sport/soccer')
soccer_tournaments = response.json()

# Get statistics
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
```

## 🚦 Error Handling & Recovery

### Robust Error Management
- **API Failures**: Automatic retry with exponential backoff
- **Network Issues**: Connection timeout and recovery
- **Data Issues**: Validation and sanitization
- **Database Issues**: Transaction rollback and recovery

### Logging & Debugging
Comprehensive logging at multiple levels:
```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Pipeline execution logs
pipeline.run_full_pipeline()  # Automatically logs progress
```

## 📦 Deployment

### Development Deployment
```powershell
# Install in development mode
pip install -e .

# Run with auto-reload
python -m tournament_calendar.cli run
```

### Production Deployment
```powershell
# Install from package
pip install .

# Run with production settings
export PYTHONPATH=/path/to/tournament_calendar
python -m tournament_calendar.cli run
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "tournament_calendar.cli", "run"]
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install development dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

### Code Style
- **Black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Linting
- **mypy**: Type checking

```powershell
# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/
mypy src/
```

## 📋 Requirements

### System Requirements
- **Python**: 3.8+ (recommended: 3.12)
- **MySQL**: 5.7+ or 8.0+
- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ free space

### API Requirements
- **Serper Account**: For search functionality
- **Firecrawl Account**: For content extraction  
- **OpenAI Account**: For data processing

### Network Requirements
- Stable internet connection for API calls
- Outbound HTTPS access (ports 443, 80)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. **Check the documentation** in this README
2. **Run diagnostics**: `python -m tournament_calendar.cli status`
3. **Validate configuration**: `python -m tournament_calendar.cli config --validate`
4. **Check logs** for detailed error information
5. **Create an issue** on GitHub with full error details

## 🎯 Roadmap

### Version 1.1
- [ ] Real-time data updates
- [ ] Advanced filtering and search
- [ ] Email notifications for new tournaments
- [ ] Data visualization dashboard

### Version 1.2  
- [ ] Machine learning for tournament prediction
- [ ] Integration with calendar applications
- [ ] Mobile API for tournament apps
- [ ] Advanced analytics and reporting

---

**Tournament Calendar System v1.0.0** - Professional tournament data collection made simple.
