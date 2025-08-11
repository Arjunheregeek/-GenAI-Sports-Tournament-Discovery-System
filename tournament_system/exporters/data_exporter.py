"""
Tournament Data Exporter

Professional export functionality for tournament calendar data with multiple format support.
"""

import json
import os
import csv
import io
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from ..core.config import DatabaseConfig, SystemConfig
from ..database.manager import DatabaseManager


@dataclass
class TournamentExportFormat:
    """Standard tournament export format for assignment compliance."""
    tournament_name: str
    level: str
    dates: str
    tournament_url: str
    streaming_links: str
    images: str
    summary: str


class TournamentDataExporter:
    """
    Professional tournament data exporter with multiple format support.
    
    Features:
    - CSV export with assignment compliance
    - JSON export with metadata
    - Database integration
    - Fallback to JSON files
    - Statistical summaries
    - Export manifests
    """
    
    def __init__(self, output_directory: str = "final_output"):
        """
        Initialize the tournament data exporter.
        
        Args:
            output_directory: Directory for export files
        """
        self.db_manager = DatabaseManager()
        self.output_dir = output_directory
        self.system_config = SystemConfig()
        
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def load_tournaments_from_database(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Load tournaments from database with optional filters.
        
        Args:
            filters: Optional filters for tournaments
            
        Returns:
            List of tournament dictionaries
        """
        try:
            connection = self.db_manager.get_connection()
            if not connection:
                print("❌ Database connection failed, using fallback")
                return self._load_tournaments_from_json()
            
            cursor = connection.cursor(dictionary=True)
            
            # Base query for export format
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
            
            # Apply filters if provided
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
            
            # Order by confidence and date
            query += " ORDER BY confidence_score DESC, created_at DESC"
            
            # Apply limit if specified
            if filters and filters.get('limit'):
                query += " LIMIT %s"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            tournaments = cursor.fetchall()
            
            print(f"📊 Loaded {len(tournaments)} tournaments from database")
            return tournaments
            
        except Exception as e:
            print(f"❌ Error loading tournaments from database: {e}")
            return self._load_tournaments_from_json()
        finally:
            if connection:
                connection.close()
    
    def _load_tournaments_from_json(self, filename: str = "tournament_data_complete.json") -> List[Dict]:
        """
        Fallback method to load tournaments from JSON file.
        
        Args:
            filename: JSON file to load from
            
        Returns:
            List of tournament dictionaries
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new JSON formats
            if isinstance(data, dict) and 'tournaments' in data:
                tournaments = data['tournaments']
            else:
                tournaments = data
            
            # Standardize format for export
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
        """
        Format tournaments according to assignment requirements, including those with partial data.

        Args:
            tournaments: Raw tournament data

        Returns:
            Formatted tournaments for assignment compliance
        """
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

            # Include tournaments even if some fields are missing
            formatted_tournaments.append(formatted)

        print(f"✅ Formatted {len(formatted_tournaments)} tournaments for export")
        return formatted_tournaments
    
    def export_to_csv(self, tournaments: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export tournaments to CSV format.
        
        Args:
            tournaments: Tournament data to export
            filename: Optional custom filename
            
        Returns:
            Path to exported CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tournament_calendar_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Format for assignment requirements
        formatted_tournaments = self.format_for_assignment_requirements(tournaments)
        
        if not formatted_tournaments:
            print("❌ No tournaments to export")
            return ""
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['tournament_name', 'level', 'dates', 'tournament_url', 
                            'streaming_links', 'images', 'summary']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(formatted_tournaments)
            
            print(f"✅ Exported {len(formatted_tournaments)} tournaments to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return ""
    
    def export_to_json(self, tournaments: List[Dict], filename: Optional[str] = None) -> str:
        """
        Export tournaments to JSON format with metadata.
        
        Args:
            tournaments: Tournament data to export
            filename: Optional custom filename
            
        Returns:
            Path to exported JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tournament_calendar_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
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
                    "assignment_compliance": True,
                    "exporter": "TournamentDataExporter"
                },
                "tournaments": formatted_tournaments
            }
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported {len(formatted_tournaments)} tournaments to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return ""
    
    def generate_export_statistics(self, tournaments: List[Dict]) -> Dict:
        """
        Generate comprehensive statistics for export data.
        
        Args:
            tournaments: Tournament data
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total_tournaments': len(tournaments),
            'by_sport': {},
            'by_level': {},
            'by_sport_level': {},
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'date_range': {'earliest': None, 'latest': None},
            'export_timestamp': datetime.now().isoformat()
        }
        
        for tournament in tournaments:
            sport = tournament.get('sport', 'Unknown')
            level = tournament.get('level', 'Unknown')
            confidence = float(tournament.get('confidence_score', 0))
            
            # Count by sport
            stats['by_sport'][sport] = stats['by_sport'].get(sport, 0) + 1
            
            # Count by level
            stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
            
            # Count by sport-level combination
            sport_level_key = f"{sport}_{level}"
            stats['by_sport_level'][sport_level_key] = stats['by_sport_level'].get(sport_level_key, 0) + 1
            
            # Confidence distribution
            if confidence >= 0.7:
                stats['confidence_distribution']['high'] += 1
            elif confidence >= 0.4:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
        
        return stats
    
    def export_comprehensive_report(self, tournaments: Optional[List[Dict]] = None) -> str:
        """
        Generate comprehensive export with all formats and statistics.
        
        Args:
            tournaments: Optional tournament data (will load from DB if not provided)
            
        Returns:
            Export timestamp identifier
        """
        # Load tournaments if not provided
        if tournaments is None:
            tournaments = self.load_tournaments_from_database()
        
        if not tournaments:
            print("❌ No tournament data available for export")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export CSV
        csv_file = self.export_to_csv(tournaments, f"tournament_calendar_{timestamp}.csv")
        
        # Export JSON
        json_file = self.export_to_json(tournaments, f"tournament_calendar_{timestamp}.json")
        
        # Generate and export statistics
        stats = self.generate_export_statistics(tournaments)
        stats_file = os.path.join(self.output_dir, f"tournament_statistics_{timestamp}.json")
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            print(f"✅ Exported statistics to {stats_file}")
        except Exception as e:
            print(f"❌ Error exporting statistics: {e}")
        
        # Create export manifest
        manifest = {
            "export_metadata": {
                "timestamp": timestamp,
                "exporter_version": "1.0",
                "total_tournaments": len(tournaments)
            },
            "files": {
                "csv_export": os.path.basename(csv_file) if csv_file else None,
                "json_export": os.path.basename(json_file) if json_file else None,
                "statistics_report": os.path.basename(stats_file)
            },
            "assignment_compliance": {
                "required_fields": ["tournament_name", "level", "dates", "tournament_url", 
                                  "streaming_links", "images", "summary"],
                "formats_provided": ["CSV", "JSON"],
                "statistics_included": True
            },
            "data_summary": stats
        }
        
        manifest_file = os.path.join(self.output_dir, f"export_manifest_{timestamp}.json")
        try:
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            print(f"✅ Created export manifest: {manifest_file}")
        except Exception as e:
            print(f"❌ Error creating manifest: {e}")
        
        return timestamp
    
    def export_in_memory_csv(self, tournaments: List[Dict]) -> io.StringIO:
        """
        Create in-memory CSV for API responses.
        
        Args:
            tournaments: Tournament data
            
        Returns:
            StringIO object with CSV data
        """
        output = io.StringIO()
        formatted_tournaments = self.format_for_assignment_requirements(tournaments)
        
        if formatted_tournaments:
            fieldnames = ['tournament_name', 'level', 'dates', 'tournament_url', 
                        'streaming_links', 'images', 'summary']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(formatted_tournaments)
        
        return output
    
    def get_export_summary(self, tournaments: List[Dict]) -> Dict:
        """
        Get a quick summary of exportable data.
        
        Args:
            tournaments: Tournament data
            
        Returns:
            Summary dictionary
        """
        formatted = self.format_for_assignment_requirements(tournaments)
        stats = self.generate_export_statistics(tournaments)
        
        return {
            "total_raw_tournaments": len(tournaments),
            "total_exportable_tournaments": len(formatted),
            "coverage": {
                "sports": len(stats['by_sport']),
                "levels": len(stats['by_level'])
            },
            "quality": stats['confidence_distribution'],
            "ready_for_export": len(formatted) > 0
        }
    
    def export_tournaments(self, tournaments: List[Dict], sport: str) -> Dict[str, str]:
        """
        Export tournaments to both CSV and JSON formats.

        Args:
            tournaments: List of processed tournament data.
            sport: The sport for which tournaments are being exported.

        Returns:
            A dictionary containing paths to the exported files.
        """
        export_results = {}

        # Export to CSV
        csv_filename = f"{sport}_tournaments.csv"
        csv_path = self.export_to_csv(tournaments, csv_filename)
        if csv_path:
            export_results['csv_file'] = csv_path

        # Export to JSON
        json_filename = f"{sport}_tournaments.json"
        json_path = self.export_to_json(tournaments, json_filename)
        if json_path:
            export_results['json_file'] = json_path

        return export_results
