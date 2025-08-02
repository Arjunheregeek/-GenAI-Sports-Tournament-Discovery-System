"""
Step 5: Database Operations - Store Tournament Data in MySQL
Complete production version with advanced database operations and data management.
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

class TournamentDatabase:
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
        """Establish connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                port=self.config.port,
                autocommit=False
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                print(f"✅ Connected to MySQL server at {self.config.host}")
                return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_database_and_tables(self) -> bool:
        """Create database and all required tables with proper schema."""
        try:
            # Create database if not exists
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.database}")
            self.cursor.execute(f"USE {self.config.database}")
            self.connection.commit()
            print(f"✅ Database '{self.config.database}' ready")
            
            # Create tournaments table with comprehensive schema
            tournaments_table = """
            CREATE TABLE IF NOT EXISTS tournaments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(500) NOT NULL,
                sport VARCHAR(100) NOT NULL,
                level VARCHAR(100) NOT NULL,
                dates TEXT,
                venue TEXT,
                url TEXT,
                streaming_links JSON,
                images JSON,
                summary TEXT,
                registration_deadline VARCHAR(200),
                entry_fee VARCHAR(200),
                contact_info TEXT,
                eligibility TEXT,
                prizes TEXT,
                source_url TEXT,
                source_domain VARCHAR(200),
                extraction_date DATETIME,
                content_quality_score DECIMAL(3,2),
                confidence_score DECIMAL(3,2),
                source_title TEXT,
                original_query TEXT,
                search_position INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_sport (sport),
                INDEX idx_level (level),
                INDEX idx_dates (dates(100)),
                INDEX idx_venue (venue(100)),
                INDEX idx_confidence (confidence_score),
                INDEX idx_created (created_at),
                FULLTEXT idx_search (name, summary, venue)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.cursor.execute(tournaments_table)
            
            # Create sports table for reference
            sports_table = """
            CREATE TABLE IF NOT EXISTS sports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.cursor.execute(sports_table)
            
            # Create levels table for reference
            levels_table = """
            CREATE TABLE IF NOT EXISTS levels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                hierarchy_order INT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.cursor.execute(levels_table)
            
            # Create extraction_log table for tracking
            extraction_log_table = """
            CREATE TABLE IF NOT EXISTS extraction_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                extraction_date DATETIME,
                total_pages_processed INT,
                successful_extractions INT,
                failed_extractions INT,
                total_tournaments_found INT,
                high_confidence_tournaments INT,
                processing_time_minutes DECIMAL(8,2),
                api_calls_made INT,
                average_confidence_score DECIMAL(3,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.cursor.execute(extraction_log_table)
            
            self.connection.commit()
            print("✅ All database tables created successfully")
            
            # Initialize reference data
            self.initialize_reference_data()
            
            return True
            
        except Error as e:
            print(f"❌ Error creating database/tables: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def initialize_reference_data(self):
        """Initialize sports and levels reference tables."""
        try:
            # Sports data
            sports_data = [
                ('Cricket', 'Team Sport', 'Traditional bat and ball sport'),
                ('Football', 'Team Sport', 'Association football/soccer'),
                ('Badminton', 'Racquet Sport', 'Indoor racquet sport'),
                ('Running', 'Athletics', 'Track and field running events'),
                ('Gym', 'Fitness', 'Gymnasium-based fitness competitions'),
                ('Cycling', 'Endurance Sport', 'Bicycle racing and competitions'),
                ('Swimming', 'Aquatic Sport', 'Pool and open water swimming'),
                ('Kabaddi', 'Traditional Sport', 'Contact team sport'),
                ('Yoga', 'Mind-Body Sport', 'Yoga competitions and demonstrations'),
                ('Basketball', 'Team Sport', 'Indoor court sport'),
                ('Chess', 'Mind Sport', 'Strategic board game'),
                ('Table Tennis', 'Racquet Sport', 'Indoor ping pong sport')
            ]
            
            # Insert sports data
            sports_query = """
            INSERT IGNORE INTO sports (name, category, description) 
            VALUES (%s, %s, %s)
            """
            
            self.cursor.executemany(sports_query, sports_data)
            
            # Levels data
            levels_data = [
                ('Corporate', 1, 'Company and corporate tournaments'),
                ('School', 2, 'School-level competitions'),
                ('College', 3, 'College and university competitions'),
                ('University', 4, 'Inter-university tournaments'),
                ('Club', 5, 'Club-level competitions'),
                ('Academy', 6, 'Sports academy tournaments'),
                ('District', 7, 'District-level competitions'),
                ('State', 8, 'State championship level'),
                ('Zonal', 9, 'Multi-state zonal competitions'),
                ('Regional', 10, 'Regional championship level'),
                ('National', 11, 'National championship level'),
                ('International', 12, 'International competitions')
            ]
            
            # Insert levels data
            levels_query = """
            INSERT IGNORE INTO levels (name, hierarchy_order, description) 
            VALUES (%s, %s, %s)
            """
            
            self.cursor.executemany(levels_query, levels_data)
            
            self.connection.commit()
            print("✅ Reference data initialized")
            
        except Error as e:
            print(f"⚠️  Warning: Could not initialize reference data: {e}")
    
    def load_tournament_data(self, filename: str = "tournament_data_complete.json") -> Tuple[List[Dict], Dict]:
        """Load tournament data from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and 'tournaments' in data:
                tournaments = data['tournaments']
                metadata = data.get('metadata', {})
                print(f"✅ Loaded {len(tournaments)} tournaments from {filename}")
                print(f"📊 Source metadata: Total tournaments: {metadata.get('total_tournaments', 'N/A')}")
            else:
                tournaments = data
                metadata = {}
                print(f"✅ Loaded {len(tournaments)} tournaments from {filename}")
            
            return tournaments, metadata
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run step4_process_tournaments.py first.")
            return [], {}
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return [], {}
    
    def prepare_tournament_data(self, tournament: Dict) -> Tuple:
        """Prepare tournament data for database insertion."""
        
        # Convert JSON arrays to JSON strings for MySQL
        streaming_links = json.dumps(tournament.get('streaming_links', []))
        images = json.dumps(tournament.get('images', []))
        
        # Parse extraction date
        extraction_date = tournament.get('extraction_date', '')
        if extraction_date:
            try:
                extraction_date = datetime.fromisoformat(extraction_date.replace('Z', '+00:00'))
                extraction_date = extraction_date.replace(tzinfo=None)  # Remove timezone for MySQL
            except:
                extraction_date = datetime.now()
        else:
            extraction_date = datetime.now()
        
        return (
            tournament.get('name', '')[:500],  # Truncate to fit VARCHAR(500)
            tournament.get('sport', '')[:100],
            tournament.get('level', '')[:100],
            tournament.get('dates', ''),
            tournament.get('venue', ''),
            tournament.get('url', ''),
            streaming_links,
            images,
            tournament.get('summary', ''),
            tournament.get('registration_deadline', '')[:200],
            tournament.get('entry_fee', '')[:200],
            tournament.get('contact_info', ''),
            tournament.get('eligibility', ''),
            tournament.get('prizes', ''),
            tournament.get('source_url', ''),
            tournament.get('source_domain', '')[:200],
            extraction_date,
            float(tournament.get('content_quality_score', 0.0)),
            float(tournament.get('confidence_score', 0.0)),
            tournament.get('source_title', ''),
            tournament.get('original_query', ''),
            int(tournament.get('search_position', 0))
        )
    
    def check_duplicate_tournament(self, tournament: Dict) -> Optional[int]:
        """Check if tournament already exists in database."""
        try:
            # Check by name and sport combination
            query = """
            SELECT id FROM tournaments 
            WHERE name = %s AND sport = %s AND level = %s
            LIMIT 1
            """
            
            self.cursor.execute(query, (
                tournament.get('name', '')[:500],
                tournament.get('sport', '')[:100],
                tournament.get('level', '')[:100]
            ))
            
            result = self.cursor.fetchone()
            return result[0] if result else None
            
        except Error as e:
            print(f"⚠️  Error checking duplicates: {e}")
            return None
    
    def insert_tournament(self, tournament: Dict, update_duplicates: bool = True) -> bool:
        """Insert a single tournament into database."""
        try:
            # Check for duplicates
            existing_id = self.check_duplicate_tournament(tournament)
            
            if existing_id and not update_duplicates:
                print(f"⏭️  Skipping duplicate: {tournament.get('name', 'N/A')}")
                return False
            
            # Prepare data
            tournament_data = self.prepare_tournament_data(tournament)
            
            if existing_id:
                # Update existing tournament
                update_query = """
                UPDATE tournaments SET
                    name = %s, sport = %s, level = %s, dates = %s, venue = %s,
                    url = %s, streaming_links = %s, images = %s, summary = %s,
                    registration_deadline = %s, entry_fee = %s, contact_info = %s,
                    eligibility = %s, prizes = %s, source_url = %s, source_domain = %s,
                    extraction_date = %s, content_quality_score = %s, confidence_score = %s,
                    source_title = %s, original_query = %s, search_position = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """
                
                self.cursor.execute(update_query, tournament_data + (existing_id,))
                print(f"🔄 Updated: {tournament.get('name', 'N/A')}")
                
            else:
                # Insert new tournament
                insert_query = """
                INSERT INTO tournaments (
                    name, sport, level, dates, venue, url, streaming_links, images,
                    summary, registration_deadline, entry_fee, contact_info,
                    eligibility, prizes, source_url, source_domain, extraction_date,
                    content_quality_score, confidence_score, source_title,
                    original_query, search_position
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                self.cursor.execute(insert_query, tournament_data)
                print(f"➕ Inserted: {tournament.get('name', 'N/A')}")
            
            return True
            
        except Error as e:
            print(f"❌ Error inserting tournament '{tournament.get('name', 'N/A')}': {e}")
            return False
    
    def bulk_insert_tournaments(self, tournaments: List[Dict], batch_size: int = 100) -> Dict:
        """Insert multiple tournaments in batches."""
        
        total_tournaments = len(tournaments)
        successful_inserts = 0
        failed_inserts = 0
        updated_tournaments = 0
        
        print(f"📥 Starting bulk insert of {total_tournaments} tournaments...")
        
        # Process in batches to manage memory and transactions
        for batch_start in range(0, total_tournaments, batch_size):
            batch_end = min(batch_start + batch_size, total_tournaments)
            batch = tournaments[batch_start:batch_end]
            
            print(f"📦 Processing batch {batch_start//batch_size + 1}: tournaments {batch_start + 1}-{batch_end}")
            
            try:
                # Start transaction for batch
                self.connection.start_transaction()
                
                for i, tournament in enumerate(batch):
                    if self.insert_tournament(tournament, update_duplicates=True):
                        successful_inserts += 1
                    else:
                        failed_inserts += 1
                    
                    # Progress indicator
                    global_index = batch_start + i
                    if global_index % 50 == 0:
                        print(f"📊 Progress: {global_index + 1}/{total_tournaments} ({((global_index + 1)/total_tournaments)*100:.1f}%)")
                
                # Commit batch transaction
                self.connection.commit()
                print(f"✅ Batch {batch_start//batch_size + 1} committed successfully")
                
            except Error as e:
                print(f"❌ Error in batch {batch_start//batch_size + 1}: {e}")
                self.connection.rollback()
                failed_inserts += len(batch)
        
        results = {
            'total_processed': total_tournaments,
            'successful_inserts': successful_inserts,
            'failed_inserts': failed_inserts,
            'success_rate': (successful_inserts / total_tournaments) * 100 if total_tournaments > 0 else 0
        }
        
        print(f"\n✅ Bulk insert completed:")
        print(f"   💚 Successful: {successful_inserts}")
        print(f"   ❌ Failed: {failed_inserts}")
        print(f"   📊 Success rate: {results['success_rate']:.1f}%")
        
        return results
    
    def log_extraction_process(self, metadata: Dict, processing_results: Dict):
        """Log the extraction process for tracking."""
        try:
            log_query = """
            INSERT INTO extraction_log (
                extraction_date, total_pages_processed, successful_extractions,
                failed_extractions, total_tournaments_found, high_confidence_tournaments,
                processing_time_minutes, api_calls_made, average_confidence_score, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Calculate processing time (approximate)
            total_tournaments = metadata.get('total_tournaments', 0)
            processing_time = total_tournaments * 1.5 / 60  # Rough estimate
            
            # Count high confidence tournaments
            high_confidence = processing_results.get('successful_inserts', 0)
            
            log_data = (
                datetime.now(),
                total_tournaments,
                processing_results.get('successful_inserts', 0),
                processing_results.get('failed_inserts', 0),
                total_tournaments,
                high_confidence,
                processing_time,
                total_tournaments,  # Approximate API calls
                metadata.get('statistics', {}).get('average_confidence', 0.0),
                f"Batch processing completed. Success rate: {processing_results.get('success_rate', 0):.1f}%"
            )
            
            self.cursor.execute(log_query, log_data)
            self.connection.commit()
            print("📋 Extraction process logged successfully")
            
        except Error as e:
            print(f"⚠️  Warning: Could not log extraction process: {e}")
    
    def get_database_statistics(self) -> Dict:
        """Get comprehensive database statistics."""
        try:
            stats = {}
            
            # Total tournaments
            self.cursor.execute("SELECT COUNT(*) FROM tournaments WHERE is_active = TRUE")
            stats['total_tournaments'] = self.cursor.fetchone()[0]
            
            # Count by sport
            self.cursor.execute("""
                SELECT sport, COUNT(*) 
                FROM tournaments 
                WHERE is_active = TRUE 
                GROUP BY sport 
                ORDER BY COUNT(*) DESC
            """)
            stats['by_sport'] = dict(self.cursor.fetchall())
            
            # Count by level
            self.cursor.execute("""
                SELECT level, COUNT(*) 
                FROM tournaments 
                WHERE is_active = TRUE 
                GROUP BY level 
                ORDER BY COUNT(*) DESC
            """)
            stats['by_level'] = dict(self.cursor.fetchall())
            
            # Confidence score distribution
            self.cursor.execute("""
                SELECT 
                    CASE 
                        WHEN confidence_score >= 0.7 THEN 'High (0.7+)'
                        WHEN confidence_score >= 0.4 THEN 'Medium (0.4-0.7)'
                        ELSE 'Low (0.0-0.4)'
                    END as confidence_range,
                    COUNT(*)
                FROM tournaments 
                WHERE is_active = TRUE
                GROUP BY confidence_range
            """)
            stats['confidence_distribution'] = dict(self.cursor.fetchall())
            
            # Average confidence score
            self.cursor.execute("""
                SELECT AVG(confidence_score) 
                FROM tournaments 
                WHERE is_active = TRUE
            """)
            result = self.cursor.fetchone()
            stats['average_confidence'] = round(float(result[0]) if result[0] else 0.0, 2)
            
            # Recent additions
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM tournaments 
                WHERE is_active = TRUE 
                AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)
            stats['added_last_24h'] = self.cursor.fetchone()[0]
            
            # Top domains
            self.cursor.execute("""
                SELECT source_domain, COUNT(*) 
                FROM tournaments 
                WHERE is_active = TRUE 
                AND source_domain != ''
                GROUP BY source_domain 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            """)
            stats['top_domains'] = dict(self.cursor.fetchall())
            
            return stats
            
        except Error as e:
            print(f"❌ Error getting database statistics: {e}")
            return {}
    
    def close_connection(self):
        """Close database connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("✅ Database connection closed")
        except Error as e:
            print(f"⚠️  Warning: Error closing connection: {e}")

def main():
    """Main function to store all tournament data in database."""
    print("=" * 60)
    print("📥 Complete Database Integration")
    print("=" * 60)
    
    db = TournamentDatabase()
    
    # Connect to database
    print("🔌 Connecting to database...")
    if not db.connect():
        return
    
    # Create database and tables
    print("🏗️  Setting up database schema...")
    if not db.create_database_and_tables():
        db.close_connection()
        return
    
    # Load tournament data from Step 4
    print("📂 Loading tournament data...")
    tournaments, metadata = db.load_tournament_data()
    if not tournaments:
        db.close_connection()
        return
    
    print(f"🎯 Processing {len(tournaments)} tournaments for database storage")
    
    # Insert tournaments into database
    print("\n📥 Starting bulk database insertion...")
    processing_results = db.bulk_insert_tournaments(tournaments)
    
    # Log the extraction process
    print("📋 Logging extraction process...")
    db.log_extraction_process(metadata, processing_results)
    
    # Get and display database statistics
    print("📊 Generating database statistics...")
    stats = db.get_database_statistics()
    
    # Display comprehensive results
    print("\n" + "=" * 60)
    print("✅ Database Integration Complete!")
    print("=" * 60)
    
    print(f"📊 Database Statistics:")
    print(f"   Total tournaments: {stats.get('total_tournaments', 0)}")
    print(f"   Added in last 24h: {stats.get('added_last_24h', 0)}")
    print(f"   Average confidence: {stats.get('average_confidence', 0)}")
    
    print(f"\n🏆 Top Sports:")
    for sport, count in list(stats.get('by_sport', {}).items())[:5]:
        print(f"   {sport}: {count} tournaments")
    
    print(f"\n📈 Top Levels:")
    for level, count in list(stats.get('by_level', {}).items())[:5]:
        print(f"   {level}: {count} tournaments")
    
    print(f"\n🎯 Confidence Distribution:")
    for range_name, count in stats.get('confidence_distribution', {}).items():
        print(f"   {range_name}: {count} tournaments")
    
    print(f"\n🌐 Top Source Domains:")
    for domain, count in list(stats.get('top_domains', {}).items())[:5]:
        print(f"   {domain}: {count} tournaments")
    
    print(f"\n🎯 Ready for Step 6: Final Export and API")
    
    # Close database connection
    db.close_connection()

if __name__ == "__main__":
    main()
