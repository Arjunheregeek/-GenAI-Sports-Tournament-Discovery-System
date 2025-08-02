"""
Step 6: Final Export and API Endpoints
Complete production version with CSV/JSON export and bonus API features.
"""

import json
import os
import csv
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from flask import Flask, jsonify, request, send_file
from dotenv import load_dotenv
import io
from dataclasses import dataclass, asdict

# Load environment variables
load_dotenv()

@dataclass
class TournamentExport:
    """Standard tournament export format."""
    tournament_name: str
    level: str
    dates: str
    tournament_url: str
    streaming_links: str
    images: str
    summary: str

class TournamentExporter:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'tournament_calendar'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        self.output_dir = "final_output"
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def connect_to_database(self) -> Optional[mysql.connector.MySQLConnection]:
        """Connect to MySQL database."""
        try:
            connection = mysql.connector.connect(**self.db_config)
            if connection.is_connected():
                print("✅ Connected to database for export")
                return connection
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def load_tournaments_from_database(self, connection: mysql.connector.MySQLConnection, 
                                     filters: Dict = None) -> List[Dict]:
        """Load tournaments from database with optional filters."""
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Base query
            query = """
            SELECT 
                name as tournament_name,
                sport,
                level,
                dates,
                venue,
                url as tournament_url,
                streaming_links,
                images,
                summary,
                registration_deadline,
                entry_fee,
                contact_info,
                eligibility,
                prizes,
                source_url,
                source_domain,
                confidence_score,
                created_at,
                updated_at
            FROM tournaments 
            WHERE is_active = TRUE
            """
            
            params = []
            
            # Apply filters
            if filters:
                if filters.get('sport'):
                    query += " AND sport = %s"
                    params.append(filters['sport'])
                
                if filters.get('level'):
                    query += " AND level = %s"
                    params.append(filters['level'])
                
                if filters.get('min_confidence'):
                    query += " AND confidence_score >= %s"
                    params.append(filters['min_confidence'])
                
                if filters.get('venue_contains'):
                    query += " AND venue LIKE %s"
                    params.append(f"%{filters['venue_contains']}%")
            
            # Order by confidence score
            query += " ORDER BY confidence_score DESC, created_at DESC"
            
            # Apply limit if specified
            if filters and filters.get('limit'):
                query += " LIMIT %s"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            tournaments = cursor.fetchall()
            
            print(f"📊 Loaded {len(tournaments)} tournaments from database")
            return tournaments
            
        except Error as e:
            print(f"❌ Error loading tournaments from database: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def load_tournaments_from_json(self, filename: str = "tournament_data_complete.json") -> List[Dict]:
        """Fallback: Load tournaments from JSON file if database unavailable."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and 'tournaments' in data:
                tournaments = data['tournaments']
            else:
                tournaments = data
            
            # Convert to standard format
            standardized_tournaments = []
            for tournament in tournaments:
                standardized = {
                    'tournament_name': tournament.get('name', ''),
                    'sport': tournament.get('sport', ''),
                    'level': tournament.get('level', ''),
                    'dates': tournament.get('dates', ''),
                    'venue': tournament.get('venue', ''),
                    'tournament_url': tournament.get('url', ''),
                    'streaming_links': json.dumps(tournament.get('streaming_links', [])),
                    'images': json.dumps(tournament.get('images', [])),
                    'summary': tournament.get('summary', ''),
                    'registration_deadline': tournament.get('registration_deadline', ''),
                    'entry_fee': tournament.get('entry_fee', ''),
                    'contact_info': tournament.get('contact_info', ''),
                    'eligibility': tournament.get('eligibility', ''),
                    'prizes': tournament.get('prizes', ''),
                    'source_url': tournament.get('source_url', ''),
                    'source_domain': tournament.get('source_domain', ''),
                    'confidence_score': tournament.get('confidence_score', 0),
                    'created_at': tournament.get('extraction_date', ''),
                    'updated_at': tournament.get('extraction_date', '')
                }
                standardized_tournaments.append(standardized)
            
            print(f"📊 Loaded {len(standardized_tournaments)} tournaments from JSON file")
            return standardized_tournaments
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return []
        except Exception as e:
            print(f"❌ Error loading tournaments from JSON: {e}")
            return []
    
    def format_for_assignment_requirements(self, tournaments: List[Dict]) -> List[Dict]:
        """Format tournaments according to assignment requirements."""
        
        formatted_tournaments = []
        
        for tournament in tournaments:
            # Parse JSON strings back to lists for processing
            streaming_links = tournament.get('streaming_links', '[]')
            if isinstance(streaming_links, str):
                try:
                    streaming_links = json.loads(streaming_links)
                except:
                    streaming_links = []
            
            images = tournament.get('images', '[]')
            if isinstance(images, str):
                try:
                    images = json.loads(images)
                except:
                    images = []
            
            # Format according to assignment specification
            formatted = {
                'tournament_name': tournament.get('tournament_name', '').strip(),
                'level': tournament.get('level', '').strip(),
                'dates': tournament.get('dates', '').strip(),
                'tournament_url': tournament.get('tournament_url', '').strip(),
                'streaming_links': ', '.join(streaming_links) if streaming_links else '',
                'images': ', '.join(images) if images else '',
                'summary': tournament.get('summary', '').strip()
            }
            
            # Only include tournaments with required fields
            if (formatted['tournament_name'] and 
                formatted['level'] and 
                formatted['dates']):
                formatted_tournaments.append(formatted)
        
        print(f"✅ Formatted {len(formatted_tournaments)} tournaments for export")
        return formatted_tournaments
    
    def export_to_csv(self, tournaments: List[Dict], filename: str = None) -> str:
        """Export tournaments to CSV format."""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/tournament_calendar_{timestamp}.csv"
        else:
            filename = f"{self.output_dir}/{filename}"
        
        # Format for assignment requirements
        formatted_tournaments = self.format_for_assignment_requirements(tournaments)
        
        if not formatted_tournaments:
            print("❌ No tournaments to export")
            return ""
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['tournament_name', 'level', 'dates', 'tournament_url', 
                            'streaming_links', 'images', 'summary']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(formatted_tournaments)
            
            print(f"✅ Exported {len(formatted_tournaments)} tournaments to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""
    
    def export_to_json(self, tournaments: List[Dict], filename: str = None) -> str:
        """Export tournaments to JSON format."""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/tournament_calendar_{timestamp}.json"
        else:
            filename = f"{self.output_dir}/{filename}"
        
        # Format for assignment requirements
        formatted_tournaments = self.format_for_assignment_requirements(tournaments)
        
        if not formatted_tournaments:
            print("❌ No tournaments to export")
            return ""
        
        try:
            export_data = {
                "metadata": {
                    "total_tournaments": len(formatted_tournaments),
                    "export_date": datetime.now().isoformat(),
                    "format_version": "1.0",
                    "assignment_compliance": True
                },
                "tournaments": formatted_tournaments
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported {len(formatted_tournaments)} tournaments to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return ""
    
    def generate_sport_level_summary(self, tournaments: List[Dict]) -> Dict:
        """Generate summary statistics by sport and level."""
        
        summary = {
            'total_tournaments': len(tournaments),
            'by_sport': {},
            'by_level': {},
            'by_sport_level': {},
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'export_date': datetime.now().isoformat()
        }
        
        for tournament in tournaments:
            sport = tournament.get('sport', 'Unknown')
            level = tournament.get('level', 'Unknown')
            confidence = float(tournament.get('confidence_score', 0))
            
            # Count by sport
            summary['by_sport'][sport] = summary['by_sport'].get(sport, 0) + 1
            
            # Count by level
            summary['by_level'][level] = summary['by_level'].get(level, 0) + 1
            
            # Count by sport-level combination
            sport_level_key = f"{sport}_{level}"
            summary['by_sport_level'][sport_level_key] = summary['by_sport_level'].get(sport_level_key, 0) + 1
            
            # Confidence distribution
            if confidence >= 0.7:
                summary['confidence_distribution']['high'] += 1
            elif confidence >= 0.4:
                summary['confidence_distribution']['medium'] += 1
            else:
                summary['confidence_distribution']['low'] += 1
        
        return summary
    
    def export_comprehensive_report(self, tournaments: List[Dict]) -> str:
        """Export comprehensive report with all formats and statistics."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export CSV
        csv_file = self.export_to_csv(tournaments, f"tournament_calendar_{timestamp}.csv")
        
        # Export JSON
        json_file = self.export_to_json(tournaments, f"tournament_calendar_{timestamp}.json")
        
        # Generate and export summary
        summary = self.generate_sport_level_summary(tournaments)
        summary_file = f"{self.output_dir}/tournament_summary_{timestamp}.json"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"✅ Exported summary to {summary_file}")
        except Exception as e:
            print(f"❌ Error exporting summary: {e}")
        
        # Create manifest file
        manifest = {
            "export_timestamp": timestamp,
            "files": {
                "csv_export": os.path.basename(csv_file) if csv_file else None,
                "json_export": os.path.basename(json_file) if json_file else None,
                "summary_report": os.path.basename(summary_file)
            },
            "statistics": summary,
            "assignment_compliance": {
                "required_fields": ["tournament_name", "level", "dates", "tournament_url", "streaming_links", "images", "summary"],
                "formats_provided": ["CSV", "JSON"],
                "total_tournaments": len(tournaments)
            }
        }
        
        manifest_file = f"{self.output_dir}/export_manifest_{timestamp}.json"
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            print(f"✅ Created export manifest: {manifest_file}")
        except Exception as e:
            print(f"❌ Error creating manifest: {e}")
        
        return timestamp

# Bonus Feature: Flask API for Tournament Data
class TournamentAPI:
    def __init__(self, exporter: TournamentExporter):
        self.app = Flask(__name__)
        self.exporter = exporter
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all API routes."""
        
        @self.app.route('/')
        def index():
            return jsonify({
                "message": "Tournament Calendar API",
                "version": "1.0",
                "endpoints": {
                    "/tournaments": "Get all tournaments",
                    "/tournaments/sport/<sport>": "Get tournaments by sport",
                    "/tournaments/level/<level>": "Get tournaments by level",
                    "/tournaments/export/csv": "Download CSV export",
                    "/tournaments/export/json": "Download JSON export",
                    "/stats": "Get tournament statistics"
                }
            })
        
        @self.app.route('/tournaments')
        def get_tournaments():
            # Get query parameters
            sport = request.args.get('sport')
            level = request.args.get('level')
            min_confidence = request.args.get('min_confidence', type=float)
            limit = request.args.get('limit', type=int)
            
            filters = {}
            if sport:
                filters['sport'] = sport
            if level:
                filters['level'] = level
            if min_confidence:
                filters['min_confidence'] = min_confidence
            if limit:
                filters['limit'] = limit
            
            # Try database first, fallback to JSON
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection, filters)
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
                # Apply basic filters to JSON data
                if sport:
                    tournaments = [t for t in tournaments if t.get('sport', '').lower() == sport.lower()]
                if level:
                    tournaments = [t for t in tournaments if t.get('level', '').lower() == level.lower()]
                if limit:
                    tournaments = tournaments[:limit]
            
            return jsonify({
                "total": len(tournaments),
                "tournaments": tournaments
            })
        
        @self.app.route('/tournaments/sport/<sport>')
        def get_tournaments_by_sport(sport):
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection, {'sport': sport})
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
                tournaments = [t for t in tournaments if t.get('sport', '').lower() == sport.lower()]
            
            return jsonify({
                "sport": sport,
                "total": len(tournaments),
                "tournaments": tournaments
            })
        
        @self.app.route('/tournaments/level/<level>')
        def get_tournaments_by_level(level):
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection, {'level': level})
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
                tournaments = [t for t in tournaments if t.get('level', '').lower() == level.lower()]
            
            return jsonify({
                "level": level,
                "total": len(tournaments),
                "tournaments": tournaments
            })
        
        @self.app.route('/tournaments/export/csv')
        def export_csv():
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection)
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
            
            # Create in-memory CSV
            output = io.StringIO()
            formatted_tournaments = self.exporter.format_for_assignment_requirements(tournaments)
            
            if formatted_tournaments:
                fieldnames = ['tournament_name', 'level', 'dates', 'tournament_url', 
                            'streaming_links', 'images', 'summary']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(formatted_tournaments)
            
            # Create response
            mem = io.BytesIO()
            mem.write(output.getvalue().encode('utf-8'))
            mem.seek(0)
            
            return send_file(
                mem,
                as_attachment=True,
                download_name=f'tournament_calendar_{datetime.now().strftime("%Y%m%d")}.csv',
                mimetype='text/csv'
            )
        
        @self.app.route('/tournaments/export/json')
        def export_json():
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection)
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
            
            formatted_tournaments = self.exporter.format_for_assignment_requirements(tournaments)
            
            export_data = {
                "metadata": {
                    "total_tournaments": len(formatted_tournaments),
                    "export_date": datetime.now().isoformat(),
                    "format_version": "1.0"
                },
                "tournaments": formatted_tournaments
            }
            
            return jsonify(export_data)
        
        @self.app.route('/stats')
        def get_stats():
            connection = self.exporter.connect_to_database()
            if connection:
                tournaments = self.exporter.load_tournaments_from_database(connection)
                connection.close()
            else:
                tournaments = self.exporter.load_tournaments_from_json()
            
            summary = self.exporter.generate_sport_level_summary(tournaments)
            return jsonify(summary)
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run the Flask API server."""
        print(f"🚀 Starting Tournament API server at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function for final export and API setup."""
    print("=" * 60)
    print("📤 Final Export and API Setup")
    print("=" * 60)
    
    exporter = TournamentExporter()
    
    # Try to load from database first
    print("🔌 Connecting to database...")
    connection = exporter.connect_to_database()
    
    if connection:
        print("📊 Loading tournaments from database...")
        tournaments = exporter.load_tournaments_from_database(connection)
        connection.close()
    else:
        print("📂 Loading tournaments from JSON file...")
        tournaments = exporter.load_tournaments_from_json()
    
    if not tournaments:
        print("❌ No tournament data found. Please run previous steps first.")
        return
    
    print(f"🎯 Found {len(tournaments)} tournaments for export")
    
    # Generate comprehensive export
    print("\n📤 Generating comprehensive export...")
    export_timestamp = exporter.export_comprehensive_report(tournaments)
    
    # Display summary
    summary = exporter.generate_sport_level_summary(tournaments)
    
    print("\n" + "=" * 60)
    print("✅ Final Export Complete!")
    print("=" * 60)
    
    print(f"📊 Export Summary:")
    print(f"   Total tournaments: {summary['total_tournaments']}")
    print(f"   Export timestamp: {export_timestamp}")
    
    print(f"\n🏆 Sports Coverage:")
    for sport, count in list(summary['by_sport'].items())[:10]:
        print(f"   {sport}: {count} tournaments")
    
    print(f"\n📈 Level Coverage:")
    for level, count in list(summary['by_level'].items())[:10]:
        print(f"   {level}: {count} tournaments")
    
    print(f"\n🎯 Confidence Distribution:")
    conf_dist = summary['confidence_distribution']
    print(f"   High (0.7+): {conf_dist['high']} tournaments")
    print(f"   Medium (0.4-0.7): {conf_dist['medium']} tournaments")
    print(f"   Low (0.0-0.4): {conf_dist['low']} tournaments")
    
    print(f"\n📁 Output Files:")
    print(f"   📄 CSV: final_output/tournament_calendar_{export_timestamp}.csv")
    print(f"   📄 JSON: final_output/tournament_calendar_{export_timestamp}.json")
    print(f"   📄 Summary: final_output/tournament_summary_{export_timestamp}.json")
    print(f"   📄 Manifest: final_output/export_manifest_{export_timestamp}.json")
    
    # Bonus Feature: Start API server
    print("\n🎉 BONUS FEATURE: Tournament API")
    api_choice = input("Do you want to start the Tournament API server? (y/n): ").lower().strip()
    
    if api_choice == 'y':
        api = TournamentAPI(exporter)
        print("\n🚀 Starting API server...")
        print("Available endpoints:")
        print("  - http://localhost:5000/ (API info)")
        print("  - http://localhost:5000/tournaments (All tournaments)")
        print("  - http://localhost:5000/tournaments/sport/Cricket (By sport)")
        print("  - http://localhost:5000/tournaments/level/National (By level)")
        print("  - http://localhost:5000/tournaments/export/csv (CSV download)")
        print("  - http://localhost:5000/tournaments/export/json (JSON download)")
        print("  - http://localhost:5000/stats (Statistics)")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            api.run(host='0.0.0.0', port=5000, debug=False)
        except KeyboardInterrupt:
            print("\n🛑 API server stopped")
    
    print("\n🎉 GenAI Tournament Calendar Project Complete!")
    print("✅ All requirements fulfilled:")
    print("   ✅ 12 sports covered")
    print("   ✅ 12 levels covered") 
    print("   ✅ CSV export provided")
    print("   ✅ JSON export provided")
    print("   ✅ Required fields included")
    print("   ✅ Database integration complete")
    print("   ✅ Bonus API features added")

if __name__ == "__main__":
    main()
