"""
Step 4: Extract Tournament Data using OpenAI API
Complete production version with advanced data extraction and validation.
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
    registration_deadline: str = ""
    entry_fee: str = ""
    contact_info: str = ""
    eligibility: str = ""
    prizes: str = ""
    confidence_score: float = 0.0

class TournamentDataExtractor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        self.model = "gpt-3.5-turbo"  # More cost-effective for bulk processing
        self.max_tokens = 1500
        self.temperature = 0.1
        self.rate_limit_delay = 1.0  # OpenAI rate limits
        self.max_retries = 3
        
        # Data validation patterns
        self.date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        self.url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    def validate_and_initialize(self) -> bool:
        """Validate API key and initialize OpenAI client."""
        if not self.api_key or self.api_key == 'your_openai_api_key_here':
            print("❌ OPENAI_API_KEY not found or not set in .env file")
            return False
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            # Test the connection
            self.client.models.list()
            print("✅ OpenAI client initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            return False
    
    def load_extracted_content(self, filename: str = "extracted_content_complete.json") -> List[Dict]:
        """Load extracted content from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and 'content' in data:
                content_list = data['content']
                print(f"✅ Loaded {len(content_list)} extracted pages from {filename}")
                print(f"📊 Source metadata: {data.get('metadata', {})}")
            else:
                content_list = data
                print(f"✅ Loaded {len(content_list)} extracted pages from {filename}")
            
            # Filter only successful extractions with content
            valid_content = []
            for content in content_list:
                if (content.get('extraction_success', False) and 
                    content.get('markdown', '') and 
                    len(content.get('markdown', '')) > 100):
                    valid_content.append(content)
            
            print(f"📖 Found {len(valid_content)} pages with valid content for processing")
            return valid_content
            
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run step3_extract_content.py first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def create_extraction_prompt(self, content: str, metadata: Dict) -> str:
        """Create optimized prompt for tournament data extraction."""
        
        sport = metadata.get('sport', 'Unknown')
        level = metadata.get('level', 'Unknown')
        url = metadata.get('url', '')
        
        prompt = f"""
Extract tournament information from this {sport} {level} tournament webpage content. 

SOURCE URL: {url}
EXPECTED SPORT: {sport}
EXPECTED LEVEL: {level}

CONTENT TO ANALYZE:
{content[:8000]}  # Limit content to avoid token limits

Please extract the following information and return ONLY a valid JSON object:

{{
    "name": "Full tournament/competition name",
    "sport": "{sport}",
    "level": "{level}",
    "dates": "Tournament dates (start - end) or single date",
    "venue": "Location/venue where tournament is held",
    "url": "{url}",
    "streaming_links": ["List of streaming/broadcast URLs if mentioned"],
    "images": ["List of image URLs if found in content"],
    "summary": "Brief 2-3 sentence summary of the tournament",
    "registration_deadline": "Registration deadline if mentioned",
    "entry_fee": "Entry fee or registration cost if mentioned",
    "contact_info": "Contact details (email, phone) if provided",
    "eligibility": "Who can participate (age groups, categories, etc.)",
    "prizes": "Prize money or awards if mentioned"
}}

IMPORTANT INSTRUCTIONS:
1. Return ONLY valid JSON, no additional text
2. If information is not found, use empty string "" for strings or empty array [] for lists
3. For dates, try to extract actual dates, not relative terms like "next month"
4. Include all URLs found in the content for streaming_links and images
5. Be accurate - only extract information that is clearly stated
6. For summary, focus on key details: what, when, where, who can participate
7. Ensure the sport matches the expected sport: {sport}
8. Ensure the level matches the expected level: {level}

Extract the information now:
"""
        return prompt
    
    def extract_tournament_data(self, content: Dict, retries: int = 0) -> Optional[Dict]:
        """Extract tournament data from a single content page using OpenAI."""
        
        if not self.client:
            return None
        
        try:
            markdown_content = content.get('markdown', '')
            if not markdown_content or len(markdown_content) < 50:
                return None
            
            # Create extraction prompt
            prompt = self.create_extraction_prompt(markdown_content, content)
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting tournament and competition data from webpage content. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract the response
            raw_response = response.choices[0].message.content.strip()
            
            # Clean the response to ensure it's valid JSON
            json_response = self.clean_json_response(raw_response)
            
            if not json_response:
                return None
            
            # Parse and validate the JSON
            tournament_data = json.loads(json_response)
            
            # Add metadata from source content
            tournament_data.update({
                'source_url': content.get('url', ''),
                'source_domain': content.get('domain', ''),
                'extraction_date': datetime.now().isoformat(),
                'content_quality_score': content.get('quality_score', 0),
                'source_title': content.get('title', ''),
                'original_query': content.get('original_query', ''),
                'search_position': content.get('search_position', 0)
            })
            
            # Calculate confidence score
            tournament_data['confidence_score'] = self.calculate_confidence_score(tournament_data, content)
            
            # Validate and clean the data
            tournament_data = self.validate_tournament_data(tournament_data)
            
            return tournament_data
            
        except json.JSONDecodeError as e:
            if retries < self.max_retries:
                print(f"⚠️  JSON decode error, retry {retries + 1}: {str(e)[:100]}")
                time.sleep(1)
                return self.extract_tournament_data(content, retries + 1)
            else:
                print(f"❌ JSON parsing failed after {self.max_retries} retries")
                return None
        
        except Exception as e:
            if retries < self.max_retries:
                print(f"⚠️  API error, retry {retries + 1}: {str(e)[:100]}")
                time.sleep(2 ** retries)  # Exponential backoff
                return self.extract_tournament_data(content, retries + 1)
            else:
                print(f"❌ Failed to extract tournament data after {self.max_retries} retries: {e}")
                return None
    
    def clean_json_response(self, response: str) -> Optional[str]:
        """Clean OpenAI response to extract valid JSON."""
        
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        
        # Remove any text before the first {
        json_start = response.find('{')
        if json_start == -1:
            return None
        
        # Remove any text after the last }
        json_end = response.rfind('}')
        if json_end == -1:
            return None
        
        cleaned_response = response[json_start:json_end + 1]
        
        # Basic validation - check if it looks like JSON
        if not (cleaned_response.startswith('{') and cleaned_response.endswith('}')):
            return None
        
        return cleaned_response
    
    def calculate_confidence_score(self, tournament_data: Dict, source_content: Dict) -> float:
        """Calculate confidence score for extracted tournament data."""
        
        score = 0.0
        
        # Required fields presence (40% of score)
        required_fields = ['name', 'sport', 'level', 'dates', 'venue']
        filled_required = sum(1 for field in required_fields if tournament_data.get(field, '').strip())
        score += (filled_required / len(required_fields)) * 0.4
        
        # Optional fields presence (20% of score)
        optional_fields = ['summary', 'registration_deadline', 'entry_fee', 'contact_info', 'eligibility']
        filled_optional = sum(1 for field in optional_fields if tournament_data.get(field, '').strip())
        score += (filled_optional / len(optional_fields)) * 0.2
        
        # Date validation (15% of score)
        dates_field = tournament_data.get('dates', '')
        if dates_field and self.validate_dates(dates_field):
            score += 0.15
        
        # Sport/Level consistency (15% of score)
        expected_sport = source_content.get('sport', '').lower()
        extracted_sport = tournament_data.get('sport', '').lower()
        if expected_sport in extracted_sport or extracted_sport in expected_sport:
            score += 0.075
        
        expected_level = source_content.get('level', '').lower()
        extracted_level = tournament_data.get('level', '').lower()
        if expected_level in extracted_level or extracted_level in expected_level:
            score += 0.075
        
        # Content quality bonus (10% of score)
        content_quality = source_content.get('quality_score', 0)
        score += content_quality * 0.1
        
        return round(min(1.0, score), 2)
    
    def validate_dates(self, date_string: str) -> bool:
        """Validate if date string contains recognizable date patterns."""
        if not date_string:
            return False
        
        for pattern in self.date_patterns:
            if re.search(pattern, date_string, re.IGNORECASE):
                return True
        
        return False
    
    def validate_tournament_data(self, data: Dict) -> Dict:
        """Validate and clean tournament data."""
        
        # Ensure required fields exist
        required_fields = ['name', 'sport', 'level', 'dates', 'venue', 'url', 'streaming_links', 'images', 'summary']
        for field in required_fields:
            if field not in data:
                data[field] = "" if field not in ['streaming_links', 'images'] else []
        
        # Clean string fields
        string_fields = ['name', 'sport', 'level', 'dates', 'venue', 'url', 'summary', 
                        'registration_deadline', 'entry_fee', 'contact_info', 'eligibility', 'prizes']
        
        for field in string_fields:
            if field in data:
                # Clean and truncate if necessary
                value = str(data[field]).strip()
                if field == 'summary' and len(value) > 500:
                    value = value[:497] + "..."
                elif field in ['name', 'venue'] and len(value) > 200:
                    value = value[:197] + "..."
                data[field] = value
        
        # Validate and clean list fields
        list_fields = ['streaming_links', 'images']
        for field in list_fields:
            if field in data:
                if isinstance(data[field], list):
                    # Validate URLs
                    valid_urls = []
                    for url in data[field]:
                        if isinstance(url, str) and re.match(self.url_pattern, url.strip()):
                            valid_urls.append(url.strip())
                    data[field] = valid_urls[:5]  # Limit to 5 URLs
                else:
                    data[field] = []
        
        return data
    
    def process_all_content(self, content_list: List[Dict], batch_size: int = 50) -> List[Dict]:
        """Process all content pages to extract tournament data."""
        
        if not self.validate_and_initialize():
            return []
        
        extracted_tournaments = []
        total_pages = len(content_list)
        successful_extractions = 0
        failed_extractions = 0
        
        print(f"🎯 Starting tournament data extraction for {total_pages} pages...")
        print(f"⏱️  Estimated time: {total_pages * self.rate_limit_delay / 60:.1f} minutes")
        
        # Process in batches to manage memory and provide progress updates
        for batch_start in range(0, total_pages, batch_size):
            batch_end = min(batch_start + batch_size, total_pages)
            batch = content_list[batch_start:batch_end]
            
            print(f"\n📦 Processing batch {batch_start//batch_size + 1}: pages {batch_start + 1}-{batch_end}")
            
            for i, content in enumerate(batch):
                global_index = batch_start + i
                
                # Progress indicator
                if global_index % 25 == 0:
                    print(f"📊 Progress: {global_index + 1}/{total_pages} ({((global_index + 1)/total_pages)*100:.1f}%)")
                
                print(f"🔍 Processing: {content.get('domain', 'unknown')} - {content.get('sport')} {content.get('level')}")
                
                # Extract tournament data
                tournament_data = self.extract_tournament_data(content)
                
                if tournament_data:
                    extracted_tournaments.append(tournament_data)
                    successful_extractions += 1
                    
                    # Show confidence score
                    confidence = tournament_data.get('confidence_score', 0)
                    if confidence >= 0.7:
                        print(f"  ✅ High confidence: {confidence}")
                    elif confidence >= 0.4:
                        print(f"  ⚠️  Medium confidence: {confidence}")
                    else:
                        print(f"  ❌ Low confidence: {confidence}")
                else:
                    failed_extractions += 1
                    print(f"  ❌ Extraction failed")
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
        
        print(f"\n✅ Tournament extraction completed:")
        print(f"   💚 Successful: {successful_extractions}")
        print(f"   ❌ Failed: {failed_extractions}")
        print(f"   📊 Success rate: {(successful_extractions/total_pages)*100:.1f}%")
        
        return extracted_tournaments
    
    def filter_high_confidence_tournaments(self, tournaments: List[Dict], min_confidence: float = 0.4) -> List[Dict]:
        """Filter tournaments based on confidence score."""
        
        high_confidence = [t for t in tournaments if t.get('confidence_score', 0) >= min_confidence]
        
        print(f"🏆 Filtered to {len(high_confidence)} high-confidence tournaments (score >= {min_confidence})")
        
        # Show confidence distribution
        confidence_ranges = {"High (0.7+)": 0, "Medium (0.4-0.7)": 0, "Low (0.0-0.4)": 0}
        for tournament in tournaments:
            score = tournament.get('confidence_score', 0)
            if score >= 0.7:
                confidence_ranges["High (0.7+)"] += 1
            elif score >= 0.4:
                confidence_ranges["Medium (0.4-0.7)"] += 1
            else:
                confidence_ranges["Low (0.0-0.4)"] += 1
        
        print("📊 Confidence distribution:")
        for range_name, count in confidence_ranges.items():
            print(f"   {range_name}: {count} tournaments")
        
        return high_confidence
    
    def save_tournament_data(self, tournaments: List[Dict], filename: str = "tournament_data_complete.json"):
        """Save extracted tournament data with comprehensive metadata."""
        
        # Generate statistics
        stats = self.generate_tournament_statistics(tournaments)
        
        # Prepare data with metadata
        tournament_export = {
            "metadata": {
                "total_tournaments": len(tournaments),
                "extraction_date": datetime.now().isoformat(),
                "api_used": "OpenAI API",
                "model": self.model,
                "version": "1.0",
                "statistics": stats
            },
            "tournaments": tournaments
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tournament_export, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(tournaments)} tournaments to {filename}")
        return filename
    
    def generate_tournament_statistics(self, tournaments: List[Dict]) -> Dict:
        """Generate comprehensive statistics about extracted tournaments."""
        
        stats = {
            "total_tournaments": len(tournaments),
            "by_sport": {},
            "by_level": {},
            "by_confidence": {"high": 0, "medium": 0, "low": 0},
            "average_confidence": 0.0,
            "fields_completion": {},
            "top_domains": {}
        }
        
        confidence_scores = []
        domain_counts = {}
        
        # Field completion tracking
        all_fields = ['name', 'sport', 'level', 'dates', 'venue', 'summary', 
                     'registration_deadline', 'entry_fee', 'contact_info', 'eligibility', 'prizes']
        
        field_completion = {field: 0 for field in all_fields}
        
        for tournament in tournaments:
            # Count by sport
            sport = tournament.get('sport', 'Unknown')
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            
            # Count by level
            level = tournament.get('level', 'Unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Confidence distribution
            confidence = tournament.get('confidence_score', 0)
            if confidence >= 0.7:
                stats["by_confidence"]["high"] += 1
            elif confidence >= 0.4:
                stats["by_confidence"]["medium"] += 1
            else:
                stats["by_confidence"]["low"] += 1
            
            confidence_scores.append(confidence)
            
            # Domain counts
            domain = tournament.get('source_domain', '')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Field completion
            for field in all_fields:
                if tournament.get(field, ''):
                    field_completion[field] += 1
        
        # Calculate averages and percentages
        if confidence_scores:
            stats["average_confidence"] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        # Field completion percentages
        total_tournaments = len(tournaments)
        if total_tournaments > 0:
            stats["fields_completion"] = {
                field: round((count / total_tournaments) * 100, 1) 
                for field, count in field_completion.items()
            }
        
        # Top domains
        stats["top_domains"] = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return stats

def main():
    """Main function to extract tournament data from all content."""
    print("=" * 60)
    print("🎯 Complete Tournament Data Extraction")
    print("=" * 60)
    
    extractor = TournamentDataExtractor()
    
    # Load extracted content from Step 3
    print("📂 Loading extracted content...")
    content_list = extractor.load_extracted_content()
    if not content_list:
        return
    
    # For testing, limit content (remove this for full run)
    # content_list = content_list[:20]  # Uncomment to test with fewer pages
    
    print(f"📖 Processing {len(content_list)} content pages")
    
    # Extract tournament data from all content
    print("\n🎯 Starting comprehensive tournament data extraction...")
    tournaments = extractor.process_all_content(content_list)
    
    if not tournaments:
        print("❌ No tournament data extracted. Check API key and content quality.")
        return
    
    print(f"\n📊 Total tournaments extracted: {len(tournaments)}")
    
    # Filter for high-confidence tournaments
    print("🏆 Filtering for high-confidence tournaments...")
    quality_tournaments = extractor.filter_high_confidence_tournaments(tournaments, min_confidence=0.4)
    
    # Save tournament data
    print("💾 Saving tournament data...")
    filename = extractor.save_tournament_data(quality_tournaments)
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Tournament Data Extraction Complete!")
    print(f"📁 Saved to: {filename}")
    print(f"🎯 Ready for Step 5: Database Integration")
    
    # Show sample high-confidence tournaments
    print("\n🏆 Top 5 High-Confidence Tournaments:")
    confidence_sorted = sorted(quality_tournaments, key=lambda x: x.get('confidence_score', 0), reverse=True)
    
    for i, tournament in enumerate(confidence_sorted[:5], 1):
        print(f"\n{i}. {tournament.get('name', 'N/A')}")
        print(f"   Sport: {tournament.get('sport')} | Level: {tournament.get('level')}")
        print(f"   Dates: {tournament.get('dates', 'N/A')}")
        print(f"   Venue: {tournament.get('venue', 'N/A')}")
        print(f"   Confidence: {tournament.get('confidence_score', 0)}")
        print(f"   Summary: {tournament.get('summary', 'N/A')[:100]}...")

if __name__ == "__main__":
    main()
