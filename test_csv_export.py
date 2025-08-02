"""
Step 4: CSV Integration Test
This script takes the OpenAI extracted tournament data and converts it to CSV format
as required by the assignment.
"""

import json
import csv
import os
from datetime import datetime
from config import OUTPUT_FIELDS, SPORTS_LIST, LEVELS_LIST

class CSVExporter:
    def __init__(self):
        self.output_fields = OUTPUT_FIELDS
        self.sample_output_dir = "sample_output"
        
        # Ensure sample_output directory exists
        if not os.path.exists(self.sample_output_dir):
            os.makedirs(self.sample_output_dir)
    
    def load_openai_results(self, filename="test_openai_extraction.json"):
        """Load the OpenAI extracted tournament data."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} tournaments from {filename}")
            return data
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run test_openai.py first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def clean_and_format_data(self, tournaments):
        """Clean and format tournament data for CSV output."""
        cleaned_tournaments = []
        
        for tournament in tournaments:
            # Create a clean record with all required fields
            cleaned_record = {}
            
            # Map all required output fields
            for field in self.output_fields:
                value = tournament.get(field, '')
                
                # Special handling for different field types
                if field == 'streaming_links':
                    # Convert array to comma-separated string
                    if isinstance(value, list):
                        cleaned_record[field] = ', '.join(value) if value else ''
                    else:
                        cleaned_record[field] = str(value) if value else ''
                elif field in ['start_date', 'end_date']:
                    # Ensure date format
                    cleaned_record[field] = value if value and value != 'TBD' else ''
                elif field == 'summary':
                    # Ensure summary is within 50 words
                    if value:
                        words = str(value).split()
                        if len(words) > 50:
                            cleaned_record[field] = ' '.join(words[:50]) + '...'
                        else:
                            cleaned_record[field] = str(value)
                    else:
                        cleaned_record[field] = ''
                else:
                    # Standard string fields
                    cleaned_record[field] = str(value) if value else ''
            
            # Add sport field (from internal data)
            cleaned_record['sport'] = tournament.get('sport', 'Cricket')
            
            cleaned_tournaments.append(cleaned_record)
        
        return cleaned_tournaments
    
    def export_to_csv(self, tournaments, filename="tournaments.csv"):
        """Export tournaments to CSV format."""
        
        if not tournaments:
            print("❌ No tournament data to export")
            return False
        
        filepath = os.path.join(self.sample_output_dir, filename)
        
        try:
            # Get all unique fieldnames from the data
            fieldnames = ['sport'] + self.output_fields
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write tournament data
                for tournament in tournaments:
                    writer.writerow(tournament)
            
            print(f"✅ Successfully exported {len(tournaments)} tournaments to {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, tournaments, filename="tournaments.json"):
        """Export tournaments to JSON format."""
        
        if not tournaments:
            print("❌ No tournament data to export")
            return False
        
        filepath = os.path.join(self.sample_output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(tournaments, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully exported {len(tournaments)} tournaments to {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return False
    
    def generate_sample_data_summary(self, tournaments):
        """Generate a summary of the exported data."""
        
        if not tournaments:
            return
        
        print("\n📊 Data Summary:")
        print(f"Total Tournaments: {len(tournaments)}")
        
        # Group by sport
        sports_count = {}
        for tournament in tournaments:
            sport = tournament.get('sport', 'Unknown')
            sports_count[sport] = sports_count.get(sport, 0) + 1
        
        print("\n🏆 Sports Distribution:")
        for sport, count in sports_count.items():
            print(f"   {sport}: {count} tournaments")
        
        # Group by level
        levels_count = {}
        for tournament in tournaments:
            level = tournament.get('level', 'Unknown')
            levels_count[level] = levels_count.get(level, 0) + 1
        
        print("\n🎯 Level Distribution:")
        for level, count in levels_count.items():
            print(f"   {level}: {count} tournaments")
        
        # Date range
        dates = []
        for tournament in tournaments:
            start_date = tournament.get('start_date', '')
            if start_date and start_date != 'TBD':
                dates.append(start_date)
        
        if dates:
            dates.sort()
            print(f"\n📅 Date Range: {dates[0]} to {dates[-1]}")
    
    def display_sample_records(self, tournaments, num_records=3):
        """Display sample records for verification."""
        
        if not tournaments:
            return
        
        print(f"\n📋 Sample Records (showing first {num_records}):")
        
        for i, tournament in enumerate(tournaments[:num_records], 1):
            print(f"\n🏆 Tournament {i}:")
            print(f"   Name: {tournament.get('tournament_name', 'N/A')}")
            print(f"   Sport: {tournament.get('sport', 'N/A')}")
            print(f"   Level: {tournament.get('level', 'N/A')}")
            print(f"   Dates: {tournament.get('start_date', 'N/A')} to {tournament.get('end_date', 'N/A')}")
            print(f"   Summary: {tournament.get('summary', 'N/A')[:100]}...")

def main():
    """Main function to test CSV export functionality."""
    print("🚀 Testing CSV Integration and Export")
    print("=" * 50)
    
    exporter = CSVExporter()
    
    # Step 1: Load OpenAI extracted data
    print("📂 Step 1: Loading OpenAI extracted tournament data...")
    tournaments = exporter.load_openai_results()
    
    if not tournaments:
        print("❌ No data found. Please run test_openai.py first.")
        return
    
    # Step 2: Clean and format data
    print("\n🧹 Step 2: Cleaning and formatting data...")
    cleaned_tournaments = exporter.clean_and_format_data(tournaments)
    print(f"✅ Processed {len(cleaned_tournaments)} tournament records")
    
    # Step 3: Export to CSV
    print("\n📄 Step 3: Exporting to CSV...")
    csv_success = exporter.export_to_csv(cleaned_tournaments, "tournaments_sample.csv")
    
    # Step 4: Export to JSON
    print("\n📄 Step 4: Exporting to JSON...")
    json_success = exporter.export_to_json(cleaned_tournaments, "tournaments_sample.json")
    
    # Step 5: Generate summary and display samples
    if csv_success or json_success:
        print("\n" + "="*50)
        exporter.generate_sample_data_summary(cleaned_tournaments)
        exporter.display_sample_records(cleaned_tournaments)
        
        print("\n" + "="*50)
        print("✅ CSV Integration Test completed successfully!")
        print(f"📁 Output files saved in: {exporter.sample_output_dir}/")
        print("📋 Files created:")
        if csv_success:
            print("   • tournaments_sample.csv")
        if json_success:
            print("   • tournaments_sample.json")
    else:
        print("\n❌ Export failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
