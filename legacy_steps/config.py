"""
Updated configuration for GenAI Tournament Calendar
Based on the complete assignment requirements.
"""

# All sports to cover as per assignment
SPORTS_LIST = [
    "Cricket", "Football", "Badminton", "Running", "Gym", 
    "Cycling", "Swimming", "Kabaddi", "Yoga", "Basketball", 
    "Chess", "Table Tennis"
]

# All levels to cover as per assignment
LEVELS_LIST = [
    "Corporate", "School", "College", "University", "Club", "Academy",
    "District", "State", "Zonal", "Regional", "National", "International"
]

# Output format fields as per assignment requirements
OUTPUT_FIELDS = [
    "tournament_name",      # Tournament Name
    "level",               # Level  
    "start_date",          # Start Date
    "end_date",           # End Date
    "official_url",       # Tournament Official URL
    "streaming_links",    # Streaming Partners/Links (array)
    "image_url",         # Tournament Image
    "summary"            # Summary of Tournament (max 50 words)
]

# Additional fields for internal use
INTERNAL_FIELDS = [
    "sport",             # Sport category
    "source_url",        # Source URL where data was found
    "extraction_date",   # When the data was extracted
    "confidence_score"   # AI confidence in extraction accuracy
]

# Database schema
DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_name TEXT NOT NULL,
    sport TEXT NOT NULL,
    level TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    official_url TEXT,
    streaming_links TEXT,  -- JSON array as text
    image_url TEXT,
    summary TEXT,
    source_url TEXT,
    extraction_date TEXT,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

print("✅ Configuration updated with complete assignment requirements")
print(f"📊 Sports to cover: {len(SPORTS_LIST)}")
print(f"🏆 Levels to cover: {len(LEVELS_LIST)}")
print(f"📋 Output fields: {len(OUTPUT_FIELDS)}")
