"""
MySQL Integration for Tournament Calendar
This script creates MySQL database schema and inserts tournament data.
"""

import mysql.connector
import json
import csv
import os
from datetime import datetime
from config import OUTPUT_FIELDS, DATABASE_SCHEMA

class MySQLTournamentDB:
    def __init__(self, host='localhost', user='root', password='', database='tournament_calendar'):
        """Initialize MySQL connection parameters."""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
    def connect(self):
        """Connect to MySQL server."""
        try:
            # First connect without database to create it if needed
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            print("✅ Connected to MySQL server")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error connecting to MySQL: {err}")
            return False
    
    def create_database(self):
        """Create database if it doesn't exist."""
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            print(f"✅ Database '{self.database}' created/selected")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error creating database: {err}")
            return False
    
    def create_tournament_table(self):
        """Create tournaments table with proper schema."""
        if not self.connection:
            return False
            
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tournaments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tournament_name VARCHAR(255) NOT NULL,
            sport VARCHAR(100) NOT NULL,
            level VARCHAR(100) NOT NULL,
            start_date DATE NULL,
            end_date DATE NULL,
            official_url TEXT NULL,
            streaming_links TEXT NULL,
            image_url TEXT NULL,
            summary TEXT NULL,
            source_url TEXT NULL,
            extraction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_sport (sport),
            INDEX idx_level (level),
            INDEX idx_start_date (start_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            print("✅ Tournaments table created successfully")
            return True
        except mysql.connector.Error as err:
            print(f"❌ Error creating table: {err}")
            return False
    
    def insert_tournament(self, tournament_data):
        """Insert a single tournament record."""
        if not self.connection:
            return False
        
        insert_query = """
        INSERT INTO tournaments (
            tournament_name, sport, level, start_date, end_date,
            official_url, streaming_links, image_url, summary, source_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare data
            values = (
                tournament_data.get('tournament_name', ''),
                tournament_data.get('sport', ''),
                tournament_data.get('level', ''),
                tournament_data.get('start_date') if tournament_data.get('start_date') else None,
                tournament_data.get('end_date') if tournament_data.get('end_date') else None,
                tournament_data.get('official_url', ''),
                tournament_data.get('streaming_links', ''),
                tournament_data.get('image_url', ''),
                tournament_data.get('summary', ''),
                tournament_data.get('source_url', '')
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            return cursor.lastrowid
            
        except mysql.connector.Error as err:
            print(f"❌ Error inserting tournament: {err}")
            return False
    
    def load_csv_data(self, csv_file_path):
        """Load tournament data from CSV file."""
        tournaments = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    tournaments.append(row)
            print(f"✅ Loaded {len(tournaments)} tournaments from CSV")
            return tournaments
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return []
    
    def import_tournaments_from_csv(self, csv_file_path):
        """Import all tournaments from CSV file to MySQL."""
        tournaments = self.load_csv_data(csv_file_path)
        
        if not tournaments:
            return False
        
        success_count = 0
        for tournament in tournaments:
            if self.insert_tournament(tournament):
                success_count += 1
        
        print(f"✅ Successfully imported {success_count}/{len(tournaments)} tournaments")
        return success_count > 0
    
    def get_tournament_stats(self):
        """Get statistics about tournaments in database."""
        if not self.connection:
            return None
        
        try:
            cursor = self.connection.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM tournaments")
            total_count = cursor.fetchone()[0]
            
            # By sport
            cursor.execute("SELECT sport, COUNT(*) FROM tournaments GROUP BY sport")
            sport_stats = cursor.fetchall()
            
            # By level
            cursor.execute("SELECT level, COUNT(*) FROM tournaments GROUP BY level")
            level_stats = cursor.fetchall()
            
            return {
                'total': total_count,
                'by_sport': sport_stats,
                'by_level': level_stats
            }
            
        except mysql.connector.Error as err:
            print(f"❌ Error getting stats: {err}")
            return None
    
    def close_connection(self):
        """Close MySQL connection."""
        if self.connection:
            self.connection.close()
            print("✅ MySQL connection closed")

def main():
    """Main function to test MySQL integration."""
    print("🚀 MySQL Integration for Tournament Calendar")
    print("=" * 50)
    
    # Configuration - Update these with your MySQL credentials
    print("📋 MySQL Configuration:")
    print("   Host: localhost")
    print("   User: root")
    print("   Database: tournament_calendar")
    print("\n⚠️  Make sure MySQL is running and credentials are correct!")
    
    # Get MySQL password
    mysql_password = input("\n🔐 Enter MySQL root password (or press Enter if no password): ")
    
    # Initialize database connection
    db = MySQLTournamentDB(password=mysql_password)
    
    # Step 1: Connect to MySQL
    print("\n🔌 Step 1: Connecting to MySQL...")
    if not db.connect():
        print("❌ Failed to connect to MySQL. Please check if MySQL is running.")
        return
    
    # Step 2: Create database
    print("\n🗄️  Step 2: Creating database...")
    if not db.create_database():
        print("❌ Failed to create database")
        return
    
    # Step 3: Create table
    print("\n📋 Step 3: Creating tournaments table...")
    if not db.create_tournament_table():
        print("❌ Failed to create table")
        return
    
    # Step 4: Import CSV data
    csv_file = "sample_output/tournaments_sample.csv"
    if os.path.exists(csv_file):
        print(f"\n📤 Step 4: Importing data from {csv_file}...")
        if db.import_tournaments_from_csv(csv_file):
            print("✅ Data import successful!")
        else:
            print("❌ Data import failed")
    else:
        print(f"❌ CSV file not found: {csv_file}")
        print("Please run test_csv_export.py first to generate the CSV file")
    
    # Step 5: Show statistics
    print("\n📊 Step 5: Database Statistics...")
    stats = db.get_tournament_stats()
    if stats:
        print(f"Total Tournaments: {stats['total']}")
        
        print("\n🏆 By Sport:")
        for sport, count in stats['by_sport']:
            print(f"   {sport}: {count}")
        
        print("\n🎯 By Level:")
        for level, count in stats['by_level']:
            print(f"   {level}: {count}")
    
    # Close connection
    db.close_connection()
    
    print("\n" + "=" * 50)
    print("✅ MySQL integration completed!")
    print("🎯 Next steps:")
    print("   • Use MySQL Workbench to view the data")
    print("   • Query: SELECT * FROM tournament_calendar.tournaments;")

if __name__ == "__main__":
    main()
