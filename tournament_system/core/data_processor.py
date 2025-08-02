"""
Tournament Data Processor Module

Processes extracted content using OpenAI API to extract structured tournament data.
Supports validation, enrichment, and standardization of tournament information.
"""

import json
import os
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
from .config import APIConfig, OUTPUT_FIELDS

# Load environment variables
load_dotenv()

@dataclass
class TournamentData:
    """Structure for tournament data validation."""
    name: str
    sport: str
    level: str
    dates: str
    venue: str
    url: str
    streaming_links: List[str]
    images: List[str]
    summary: str

class TournamentDataProcessor:
    """Processes extracted content to extract structured tournament data."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.client = OpenAI(api_key=self.api_config.openai_api_key)
        self.rate_limit_delay = self.api_config.openai_rate_limit
        self.max_retries = self.api_config.max_retries
        self.output_fields = OUTPUT_FIELDS
    
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key."""
        if not self.api_config.openai_api_key or self.api_config.openai_api_key == 'your_openai_api_key_here':
            print("❌ OPENAI_API_KEY not found or not set in .env file")
            return False
        return True
    
    def create_extraction_prompt(self, content: str, search_metadata: Dict) -> str:
        """Create extraction prompt for OpenAI."""
        
        prompt = f'''
        Extract tournament information from the following content and return it as a JSON object.

        Content to analyze:
        ---
        {content[:4000]}  # Limit content to avoid token limits
        ---

        Search metadata:
        - Sport: {search_metadata.get('sport', 'Unknown')}
        - Level: {search_metadata.get('level', 'Unknown')}
        - Original Query: {search_metadata.get('original_query', '')}

        Extract the following information and return as JSON:
        {{
            "tournament_name": "Full tournament name",
            "level": "Tournament level (School/College/University/Club/District/State/National/International/Corporate)",
            "start_date": "Start date in YYYY-MM-DD format (if available)",
            "end_date": "End date in YYYY-MM-DD format (if available)",
            "official_url": "Official tournament website URL",
            "streaming_links": ["Array of streaming/broadcast URLs"],
            "image_url": "Tournament poster/banner image URL",
            "summary": "Brief tournament summary (max 50 words)",
            "venue": "Tournament venue/location",
            "registration_info": "Registration details and deadlines",
            "contact_info": "Contact information",
            "eligibility": "Eligibility criteria",
            "prizes": "Prize information",
            "entry_fee": "Entry fee details"
        }}

        Guidelines:
        1. Extract only factual information present in the content
        2. Use "N/A" for missing information
        3. Ensure dates are in YYYY-MM-DD format
        4. Include only valid URLs
        5. Keep summary under 50 words
        6. Infer level from content if not explicitly mentioned
        7. Look for tournament names, dates, venues, contact details
        8. Extract any streaming/broadcast information
        9. Find registration deadlines and procedures
        10. Identify prize money or awards mentioned

        Return only the JSON object, no additional text.
        '''
        
        return prompt
    
    def extract_tournament_data(self, content_item: Dict, retries: int = 0) -> Optional[Dict]:
        """Extract tournament data from a single content item."""
        
        content_text = content_item.get('content', '') or content_item.get('markdown', '')
        if not content_text or len(content_text) < 50:
            return None
        
        # Create extraction prompt
        prompt = self.create_extraction_prompt(content_text, content_item)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured tournament information from web content. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            # Parse JSON
            tournament_data = json.loads(result_text)
            
            # Enrich with source metadata
            tournament_data.update({
                'source_url': content_item.get('url', ''),
                'source_title': content_item.get('title', ''),
                'extraction_date': datetime.now().isoformat(),
                'content_quality_score': content_item.get('quality_score', 0),
                'word_count': content_item.get('word_count', 0),
                'sport': content_item.get('sport', tournament_data.get('sport', 'Unknown')),
                'original_search_query': content_item.get('original_query', '')
            })
            
            # Validate and clean data
            cleaned_data = self.validate_and_clean_data(tournament_data)
            
            return cleaned_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error for {content_item.get('url', 'unknown')}: {e}")
            if retries < self.max_retries:
                time.sleep(1)
                return self.extract_tournament_data(content_item, retries + 1)
            return None
            
        except Exception as e:
            print(f"❌ Error extracting tournament data: {e}")
            if retries < self.max_retries:
                time.sleep(2)
                return self.extract_tournament_data(content_item, retries + 1)
            return None
    
    def validate_and_clean_data(self, data: Dict) -> Dict:
        """Validate and clean extracted tournament data."""
        
        cleaned = {}
        
        # Tournament name - required
        name = data.get('tournament_name', '').strip()
        if name and name != 'N/A':
            cleaned['tournament_name'] = name
        else:
            # Try to extract from source title
            source_title = data.get('source_title', '')
            if source_title:
                cleaned['tournament_name'] = source_title[:100]
            else:
                cleaned['tournament_name'] = 'Unknown Tournament'
        
        # Level - standardize
        level = data.get('level', '').strip()
        standard_levels = ['School', 'College', 'University', 'Club', 'Academy', 'District', 
                          'State', 'Zonal', 'Regional', 'National', 'International', 'Corporate']
        
        level_found = None
        for std_level in standard_levels:
            if std_level.lower() in level.lower():
                level_found = std_level
                break
        
        cleaned['level'] = level_found or level or 'Unknown'
        
        # Dates - validate format
        start_date = self.validate_date(data.get('start_date', ''))
        end_date = self.validate_date(data.get('end_date', ''))
        
        cleaned['start_date'] = start_date
        cleaned['end_date'] = end_date
        
        # URLs - validate
        official_url = data.get('official_url', '').strip()
        if self.validate_url(official_url):
            cleaned['official_url'] = official_url
        else:
            cleaned['official_url'] = data.get('source_url', '')
        
        # Streaming links - validate and clean
        streaming_links = data.get('streaming_links', [])
        if isinstance(streaming_links, str):
            streaming_links = [streaming_links] if streaming_links.strip() else []
        
        valid_streaming_links = []
        for link in streaming_links:
            if isinstance(link, str) and self.validate_url(link.strip()):
                valid_streaming_links.append(link.strip())
        
        cleaned['streaming_links'] = json.dumps(valid_streaming_links)
        
        # Image URL
        image_url = data.get('image_url', '').strip()
        if self.validate_url(image_url):
            cleaned['image_url'] = image_url
        else:
            cleaned['image_url'] = ''
        
        # Summary - limit length
        summary = data.get('summary', '').strip()
        if summary and summary != 'N/A':
            # Limit to 50 words
            words = summary.split()[:50]
            cleaned['summary'] = ' '.join(words)
        else:
            cleaned['summary'] = ''
        
        # Copy additional fields
        additional_fields = ['sport', 'source_url', 'source_title', 'extraction_date', 
                           'content_quality_score', 'word_count', 'original_search_query',
                           'venue', 'registration_info', 'contact_info', 'eligibility', 
                           'prizes', 'entry_fee']
        
        for field in additional_fields:
            if field in data:
                cleaned[field] = data[field]
        
        # Calculate confidence score
        cleaned['confidence_score'] = self.calculate_confidence_score(cleaned)
        
        return cleaned
    
    def validate_date(self, date_str: str) -> str:
        """Validate and format date string."""
        if not date_str or date_str == 'N/A':
            return ''
        
        # Try to parse various date formats
        date_formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%B %d, %Y',
            '%d %B %Y',
            '%b %d, %Y',
            '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If parsing fails, return original string if it looks like a date
        if re.search(r'\d{4}|\d{1,2}[/-]\d{1,2}', date_str):
            return date_str.strip()
        
        return ''
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url:
            return False
        
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def calculate_confidence_score(self, data: Dict) -> float:
        """Calculate confidence score for extracted data."""
        score = 0.0
        total_possible = 0.0
        
        # Required fields (high weight)
        required_fields = {
            'tournament_name': 2.0,
            'start_date': 1.5,
            'end_date': 1.5,
            'official_url': 1.0
        }
        
        for field, weight in required_fields.items():
            total_possible += weight
            value = data.get(field, '')
            if value and value.strip() and value != 'Unknown Tournament':
                score += weight
        
        # Optional fields (medium weight)
        optional_fields = {
            'level': 1.0,
            'summary': 0.5,
            'streaming_links': 0.5,
            'image_url': 0.5
        }
        
        for field, weight in optional_fields.items():
            total_possible += weight
            value = data.get(field, '')
            if value and value.strip():
                if field == 'streaming_links':
                    try:
                        links = json.loads(value) if isinstance(value, str) else value
                        if links:
                            score += weight
                    except:
                        pass
                else:
                    score += weight
        
        # Quality bonus
        quality_score = data.get('content_quality_score', 0)
        if quality_score > 5:
            score += 1.0
            total_possible += 1.0
        
        # Calculate percentage
        if total_possible > 0:
            confidence = (score / total_possible) * 100
            return round(min(100.0, confidence), 2)
        
        return 0.0
    
    def load_extracted_content(self, filename: str = "extracted_content_complete.json") -> List[Dict]:
        """Load extracted content from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both old and new format
            if isinstance(data, dict) and 'content' in data:
                content = data['content']
                print(f"✅ Loaded {len(content)} content items from {filename}")
            else:
                content = data
                print(f"✅ Loaded {len(content)} content items from {filename}")
            
            return content
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run content extraction first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def process_all_content(self, content_list: List[Dict], max_items: int = None) -> List[Dict]:
        """Process all extracted content to get tournament data."""
        
        if not self.validate_api_key():
            return []
        
        if max_items:
            content_list = content_list[:max_items]
            print(f"🔢 Limited to first {max_items} content items for processing")
        
        # Filter high-quality content first
        high_quality_content = [c for c in content_list if c.get('quality_score', 0) >= 2.0]
        if len(high_quality_content) < len(content_list):
            print(f"🔍 Filtered to {len(high_quality_content)} high-quality content items")
            content_list = high_quality_content
        
        processed_tournaments = []
        total_items = len(content_list)
        successful_extractions = 0
        failed_extractions = 0
        
        print(f"🤖 Starting tournament data extraction for {total_items} content items...")
        print(f"⏱️  Estimated time: {total_items * self.rate_limit_delay / 60:.1f} minutes")
        
        for i, content_item in enumerate(content_list):
            # Progress indicator
            if i % 10 == 0 or i == total_items - 1:
                print(f"📊 Progress: {i+1}/{total_items} ({((i+1)/total_items)*100:.1f}%)")
            
            # Extract tournament data
            tournament_data = self.extract_tournament_data(content_item)
            
            if tournament_data:
                processed_tournaments.append(tournament_data)
                successful_extractions += 1
            else:
                failed_extractions += 1
            
            # Rate limiting
            if i < total_items - 1:
                time.sleep(self.rate_limit_delay)
        
        print(f"✅ Tournament data extraction completed: {successful_extractions} successful, {failed_extractions} failed")
        return processed_tournaments
    
    def deduplicate_tournaments(self, tournaments: List[Dict]) -> List[Dict]:
        """Remove duplicate tournaments based on name and dates."""
        unique_tournaments = []
        seen_tournaments = set()
        
        for tournament in tournaments:
            # Create identifier from name and start date
            name = tournament.get('tournament_name', '').lower().strip()
            start_date = tournament.get('start_date', '')
            
            identifier = f"{name}_{start_date}"
            
            if identifier not in seen_tournaments:
                seen_tournaments.add(identifier)
                unique_tournaments.append(tournament)
        
        removed_count = len(tournaments) - len(unique_tournaments)
        if removed_count > 0:
            print(f"🧹 Removed {removed_count} duplicate tournaments")
        
        return unique_tournaments
    
    def save_tournament_data(self, tournaments: List[Dict], filename: str = "tournament_data_complete.json") -> str:
        """Save processed tournament data with metadata."""
        
        # Generate statistics
        stats = self.generate_processing_statistics(tournaments)
        
        # Prepare data with metadata
        tournament_data = {
            "metadata": {
                "total_tournaments": len(tournaments),
                "processing_date": datetime.now().isoformat(),
                "processor": "OpenAI GPT-3.5-turbo",
                "version": "1.0",
                "statistics": stats
            },
            "tournaments": tournaments
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tournament_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(tournaments)} tournaments to {filename}")
        return filename
    
    def generate_processing_statistics(self, tournaments: List[Dict]) -> Dict:
        """Generate statistics about processed tournament data."""
        if not tournaments:
            return {}
        
        stats = {
            "total_tournaments": len(tournaments),
            "by_sport": {},
            "by_level": {},
            "confidence_distribution": {},
            "average_confidence": 0.0,
            "with_dates": 0,
            "with_streaming": 0,
            "with_images": 0
        }
        
        confidence_scores = []
        
        for tournament in tournaments:
            # Count by sport
            sport = tournament.get('sport', 'Unknown')
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            
            # Count by level
            level = tournament.get('level', 'Unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Confidence distribution
            confidence = tournament.get('confidence_score', 0)
            confidence_range = f"{int(confidence//10)*10}-{int(confidence//10)*10+10}"
            stats["confidence_distribution"][confidence_range] = stats["confidence_distribution"].get(confidence_range, 0) + 1
            
            if confidence > 0:
                confidence_scores.append(confidence)
            
            # Feature availability
            if tournament.get('start_date') or tournament.get('end_date'):
                stats["with_dates"] += 1
            
            streaming_links = tournament.get('streaming_links', '[]')
            try:
                links = json.loads(streaming_links) if isinstance(streaming_links, str) else streaming_links
                if links:
                    stats["with_streaming"] += 1
            except:
                pass
            
            if tournament.get('image_url'):
                stats["with_images"] += 1
        
        # Calculate average confidence
        if confidence_scores:
            stats["average_confidence"] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        return stats

def main():
    """Main function to process all extracted content."""
    print("=" * 60)
    print("🚀 Complete Tournament Data Processing")
    print("=" * 60)
    
    processor = TournamentDataProcessor()
    
    # Load extracted content from Step 3
    print("📂 Loading extracted content...")
    content_list = processor.load_extracted_content()
    if not content_list:
        return
    
    print(f"🔍 Loaded {len(content_list)} content items")
    
    # For testing, limit items (remove this for full run)
    # max_items = 20  # Uncomment to test with fewer items
    max_items = None
    
    # Process all content
    print("\n🤖 Starting comprehensive tournament data extraction...")
    tournaments = processor.process_all_content(content_list, max_items)
    
    if not tournaments:
        print("❌ No tournament data extracted. Check API key and content quality.")
        return
    
    print(f"\n📊 Total tournaments extracted: {len(tournaments)}")
    
    # Remove duplicates
    print("🧹 Removing duplicate tournaments...")
    unique_tournaments = processor.deduplicate_tournaments(tournaments)
    print(f"✅ Unique tournaments: {len(unique_tournaments)}")
    
    # Sort by confidence score
    unique_tournaments = sorted(unique_tournaments, key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    # Save tournament data
    print("💾 Saving tournament data...")
    filename = processor.save_tournament_data(unique_tournaments)
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Tournament Data Processing Complete!")
    print(f"📁 Saved to: {filename}")
    print(f"🎯 Ready for Step 5: Database Operations")
    
    # Show sample high-confidence tournaments
    print("\n🏆 Top 5 Tournaments by Confidence Score:")
    for i, tournament in enumerate(unique_tournaments[:5], 1):
        print(f"\n{i}. {tournament.get('tournament_name', 'N/A')}")
        print(f"   Sport: {tournament.get('sport')} | Level: {tournament.get('level')}")
        print(f"   Dates: {tournament.get('start_date')} to {tournament.get('end_date')}")
        print(f"   Confidence: {tournament.get('confidence_score', 0)}% | URL: {tournament.get('official_url', 'N/A')}")

if __name__ == "__main__":
    main()
