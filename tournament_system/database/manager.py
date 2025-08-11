"""
Database Manager Module

Handles MySQL database operations for tournament data storage and retrieval.
Supports batch operations, data validation, and comprehensive error handling.
"""

import json
import os
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from dotenv import load_dotenv
from ..core.config import DatabaseConfig, DATABASE_SCHEMA

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration structure."""
    host: str
    user: str
    password: str
    database: str
    port: int = 3306

class DatabaseManager:
    """Manages MySQL database operations for tournament data."""
    
    def __init__(self):
        self.config = DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'tournament_calendar'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                port=self.config.port,
                autocommit=True,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print(f"✅ Connected to MySQL server at {self.config.host}:{self.config.port}")
                return True
                
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create database if it doesn't exist."""
        try:
            if not self.connection:
                return False
            
            # Create database
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{self.config.database}' created/verified")
            
            # Use the database
            self.cursor.execute(f"USE {self.config.database}")
            
            return True
            
        except Error as e:
            print(f"❌ Error creating database: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create tournament table with proper schema."""
        try:
            if not self.cursor:
                return False
            
            # Create tournaments table
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS tournaments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tournament_name VARCHAR(255) NOT NULL,
                sport VARCHAR(100) NOT NULL,
                level VARCHAR(100) NOT NULL,
                start_date DATE NULL,
                end_date DATE NULL,
                official_url TEXT NULL,
                streaming_links JSON NULL,
                image_url TEXT NULL,
                summary TEXT NULL,
                source_url TEXT NULL,
                extraction_date DATETIME NULL,
                confidence_score DECIMAL(5,2) NULL,
                venue TEXT NULL,
                registration_info TEXT NULL,
                contact_info TEXT NULL,
                eligibility TEXT NULL,
                prizes TEXT NULL,
                entry_fee TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_sport (sport),
                INDEX idx_level (level),
                INDEX idx_start_date (start_date),
                INDEX idx_confidence (confidence_score),
                FULLTEXT idx_tournament_name (tournament_name),
                FULLTEXT idx_summary (summary)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            
            self.cursor.execute(create_table_query)
            print("✅ Tournament table created/verified")
            
            # Create statistics table
            stats_table_query = '''
            CREATE TABLE IF NOT EXISTS import_statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                import_date DATETIME NOT NULL,
                total_tournaments INT NOT NULL,
                successful_imports INT NOT NULL,
                failed_imports INT NOT NULL,
                duplicate_count INT NOT NULL,
                average_confidence DECIMAL(5,2) NULL,
                import_file VARCHAR(255) NULL,
                notes TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
            
            self.cursor.execute(stats_table_query)
            print("✅ Statistics table created/verified")
            
            return True
            
        except Error as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def validate_tournament_data(self, tournament: Dict) -> Dict:
        """Validate and clean tournament data before insertion."""
        
        validated = {}
        
        # Required fields
        validated['tournament_name'] = str(tournament.get('tournament_name', 'Unknown'))[:255]
        validated['sport'] = str(tournament.get('sport', 'Unknown'))[:100]
        validated['level'] = str(tournament.get('level', 'Unknown'))[:100]
        
        # Date fields
        validated['start_date'] = self.validate_date(tournament.get('start_date'))
        validated['end_date'] = self.validate_date(tournament.get('end_date'))
        
        # URL fields
        validated['official_url'] = tournament.get('official_url', '')
        validated['source_url'] = tournament.get('source_url', '')
        validated['image_url'] = tournament.get('image_url', '')
        
        # JSON field for streaming links
        streaming_links = tournament.get('streaming_links', [])
        if isinstance(streaming_links, str):
            try:
                streaming_links = json.loads(streaming_links)
            except:
                streaming_links = []
        validated['streaming_links'] = json.dumps(streaming_links) if streaming_links else None
        
        # Text fields
        validated['summary'] = tournament.get('summary', '')
        validated['venue'] = tournament.get('venue', '')
        validated['registration_info'] = tournament.get('registration_info', '')
        validated['contact_info'] = tournament.get('contact_info', '')
        validated['eligibility'] = tournament.get('eligibility', '')
        validated['prizes'] = tournament.get('prizes', '')
        validated['entry_fee'] = tournament.get('entry_fee', '')
        
        # Numeric fields
        confidence_score = tournament.get('confidence_score', 0)
        try:
            validated['confidence_score'] = float(confidence_score) if confidence_score else None
        except:
            validated['confidence_score'] = None
        
        # DateTime field
        extraction_date = tournament.get('extraction_date')
        if extraction_date:
            try:
                if isinstance(extraction_date, str):
                    # Parse ISO format
                    dt = datetime.fromisoformat(extraction_date.replace('Z', '+00:00'))
                    validated['extraction_date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    validated['extraction_date'] = None
            except:
                validated['extraction_date'] = None
        else:
            validated['extraction_date'] = None
        
        return validated
    
    def validate_date(self, date_value) -> Optional[str]:
        """Validate and format date for MySQL."""
        if not date_value:
            return None
        
        if isinstance(date_value, str):
            if date_value.strip() == '' or date_value.strip().lower() == 'n/a':
                return None
            
            # Try to parse date
            try:
                # Handle YYYY-MM-DD format
                if re.match(r'\d{4}-\d{2}-\d{2}', date_value):
                    dt = datetime.strptime(date_value[:10], '%Y-%m-%d')
                    return dt.strftime('%Y-%m-%d')
                
                # Handle other formats
                date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%B %d, %Y', '%d %B %Y']
                for fmt in date_formats:
                    try:
                        dt = datetime.strptime(date_value.strip(), fmt)
                        return dt.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            except:
                pass
        
        return None
    
    def insert_tournament(self, tournament: Dict) -> bool:
        """Insert a single tournament into the database."""
        try:
            if not self.cursor:
                return False
            
            # Validate data
            validated_tournament = self.validate_tournament_data(tournament)
            
            # Check for duplicates
            if self.is_duplicate(validated_tournament):
                return False
            
            # Prepare insert query
            insert_query = '''
            INSERT INTO tournaments (
                tournament_name, sport, level, start_date, end_date,
                official_url, streaming_links, image_url, summary,
                source_url, extraction_date, confidence_score,
                venue, registration_info, contact_info, eligibility,
                prizes, entry_fee
            ) VALUES (
                %(tournament_name)s, %(sport)s, %(level)s, %(start_date)s, %(end_date)s,
                %(official_url)s, %(streaming_links)s, %(image_url)s, %(summary)s,
                %(source_url)s, %(extraction_date)s, %(confidence_score)s,
                %(venue)s, %(registration_info)s, %(contact_info)s, %(eligibility)s,
                %(prizes)s, %(entry_fee)s
            )
            '''
            
            self.cursor.execute(insert_query, validated_tournament)
            return True
            
        except Error as e:
            print(f"❌ Error inserting tournament '{tournament.get('tournament_name', 'Unknown')}': {e}")
            return False
    
    def is_duplicate(self, tournament: Dict) -> bool:
        """Check if tournament already exists in database."""
        try:
            if not self.cursor:
                return False
            
            # Check based on name and start date
            check_query = '''
            SELECT COUNT(*) FROM tournaments 
            WHERE tournament_name = %s 
            AND (start_date = %s OR (start_date IS NULL AND %s IS NULL))
            '''
            
            self.cursor.execute(check_query, (
                tournament['tournament_name'],
                tournament['start_date'],
                tournament['start_date']
            ))
            
            count = self.cursor.fetchone()[0]
            return count > 0
            
        except Error as e:
            print(f"❌ Error checking for duplicates: {e}")
            return False
    
    def insert_tournaments_batch(self, tournaments: List[Dict]) -> Dict:
        """Insert multiple tournaments with statistics tracking."""
        
        stats = {
            'total_tournaments': len(tournaments),
            'successful_imports': 0,
            'failed_imports': 0,
            'duplicate_count': 0,
            'average_confidence': 0.0
        }
        
        confidence_scores = []
        
        print(f"📊 Starting batch import of {len(tournaments)} tournaments...")
        
        for i, tournament in enumerate(tournaments):
            # Progress indicator
            if i % 50 == 0 or i == len(tournaments) - 1:
                print(f"📈 Progress: {i+1}/{len(tournaments)} ({((i+1)/len(tournaments))*100:.1f}%)")
            
            # Check for duplicate first
            validated_tournament = self.validate_tournament_data(tournament)
            if self.is_duplicate(validated_tournament):
                stats['duplicate_count'] += 1
                continue
            
            # Insert tournament
            if self.insert_tournament(tournament):
                stats['successful_imports'] += 1
                
                # Track confidence scores
                confidence = tournament.get('confidence_score', 0)
                if confidence and confidence > 0:
                    confidence_scores.append(float(confidence))
            else:
                stats['failed_imports'] += 1
        
        # Calculate average confidence
        if confidence_scores:
            stats['average_confidence'] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        return stats
    
    def record_import_statistics(self, stats: Dict, import_file: str = None) -> bool:
        """Record import statistics in the database."""
        try:
            if not self.cursor:
                return False
            
            insert_stats_query = '''
            INSERT INTO import_statistics (
                import_date, total_tournaments, successful_imports,
                failed_imports, duplicate_count, average_confidence, import_file
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            
            self.cursor.execute(insert_stats_query, (
                datetime.now(),
                stats['total_tournaments'],
                stats['successful_imports'],
                stats['failed_imports'],
                stats['duplicate_count'],
                stats['average_confidence'],
                import_file
            ))
            
            return True
            
        except Error as e:
            print(f"❌ Error recording statistics: {e}")
            return False
    
    def get_tournaments(self, limit: int = None, sport: str = None, level: str = None) -> List[Dict]:
        """Retrieve tournaments from database with optional filtering."""
        try:
            if not self.cursor:
                return []
            
            # Build query
            query = "SELECT * FROM tournaments WHERE 1=1"
            params = []
            
            if sport:
                query += " AND sport = %s"
                params.append(sport)
            
            if level:
                query += " AND level = %s"
                params.append(level)
            
            query += " ORDER BY confidence_score DESC, created_at DESC"
            
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            self.cursor.execute(query, params)
            
            # Fetch results and convert to dict
            columns = [desc[0] for desc in self.cursor.description]
            tournaments = []
            
            for row in self.cursor.fetchall():
                tournament = dict(zip(columns, row))
                
                # Parse JSON fields
                if tournament.get('streaming_links'):
                    try:
                        tournament['streaming_links'] = json.loads(tournament['streaming_links'])
                    except:
                        tournament['streaming_links'] = []
                
                tournaments.append(tournament)
            
            return tournaments
            
        except Error as e:
            print(f"❌ Error retrieving tournaments: {e}")
            return []
    
    def get_database_statistics(self) -> Dict:
        """Get comprehensive database statistics."""
        try:
            if not self.cursor:
                return {}
            
            stats = {}
            
            # Total tournaments
            self.cursor.execute("SELECT COUNT(*) FROM tournaments")
            stats['total_tournaments'] = self.cursor.fetchone()[0]
            
            # By sport
            self.cursor.execute("SELECT sport, COUNT(*) FROM tournaments GROUP BY sport")
            stats['by_sport'] = dict(self.cursor.fetchall())
            
            # By level
            self.cursor.execute("SELECT level, COUNT(*) FROM tournaments GROUP BY level")
            stats['by_level'] = dict(self.cursor.fetchall())
            
            # Average confidence
            self.cursor.execute("SELECT AVG(confidence_score) FROM tournaments WHERE confidence_score IS NOT NULL")
            avg_confidence = self.cursor.fetchone()[0]
            stats['average_confidence'] = round(float(avg_confidence), 2) if avg_confidence else 0.0
            
            # Date range
            self.cursor.execute("SELECT MIN(start_date), MAX(start_date) FROM tournaments WHERE start_date IS NOT NULL")
            date_range = self.cursor.fetchone()
            stats['date_range'] = {
                'earliest': str(date_range[0]) if date_range[0] else None,
                'latest': str(date_range[1]) if date_range[1] else None
            }
            
            # Recent imports
            self.cursor.execute("SELECT * FROM import_statistics ORDER BY import_date DESC LIMIT 5")
            columns = [desc[0] for desc in self.cursor.description]
            recent_imports = []
            for row in self.cursor.fetchall():
                recent_imports.append(dict(zip(columns, row)))
            stats['recent_imports'] = recent_imports
            
            return stats
            
        except Error as e:
            print(f"❌ Error getting database statistics: {e}")
            return {}
    
    def load_tournament_data(self, filename: str = "tournament_data_complete.json") -> List[Dict]:
        """Load tournament data from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both old and new format
            if isinstance(data, dict) and 'tournaments' in data:
                tournaments = data['tournaments']
                print(f"✅ Loaded {len(tournaments)} tournaments from {filename}")
            else:
                tournaments = data
                print(f"✅ Loaded {len(tournaments)} tournaments from {filename}")
            
            return tournaments
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run tournament data processing first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("✅ Database connection closed")
        except Error as e:
            print(f"❌ Error closing connection: {e}")

def main():
    """Main function to import tournament data into database."""
    print("=" * 60)
    print("🚀 Complete Database Import")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    # Connect to database
    print("📡 Connecting to database...")
    if not db_manager.connect():
        return
    
    # Create database and tables
    print("🏗️  Setting up database...")
    if not db_manager.create_database():
        return
    
    if not db_manager.create_tables():
        return
    
    # Load tournament data from Step 4
    print("📂 Loading tournament data...")
    tournaments = db_manager.load_tournament_data()
    if not tournaments:
        return
    
    print(f"🔍 Loaded {len(tournaments)} tournaments")
    
    # Import tournaments
    print("\n📊 Starting database import...")
    stats = db_manager.insert_tournaments_batch(tournaments)
    
    # Record statistics
    db_manager.record_import_statistics(stats, "tournament_data_complete.json")
    
    # Display results
    print("\n" + "=" * 60)
    print("✅ Database Import Complete!")
    print("=" * 60)
    print(f"📊 Import Statistics:")
    print(f"   Total tournaments: {stats['total_tournaments']}")
    print(f"   Successfully imported: {stats['successful_imports']}")
    print(f"   Failed imports: {stats['failed_imports']}")
    print(f"   Duplicates skipped: {stats['duplicate_count']}")
    print(f"   Average confidence: {stats['average_confidence']}%")
    
    # Show database statistics
    print(f"\n📈 Database Statistics:")
    db_stats = db_manager.get_database_statistics()
    print(f"   Total in database: {db_stats.get('total_tournaments', 0)}")
    print(f"   Sports covered: {len(db_stats.get('by_sport', {}))}")
    print(f"   Levels covered: {len(db_stats.get('by_level', {}))}")
    
    print(f"\n🎯 Ready for Step 6: Final Export and API")
    
    # Close connection
    db_manager.close()

if __name__ == "__main__":
    main()
