"""
Test OpenAI API functionality for tournament data extraction
This script tests OpenAI's ability to extract structured tournament information from scraped content.
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class TournamentExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def test_api_connection(self):
        """Test basic OpenAI API connection."""
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OPENAI_API_KEY not found or not set in .env file")
            return False
        
        print(f"✅ API Key found: {api_key[:20]}...")
        
        try:
            # Simple test call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello! Just testing the connection."}],
                max_tokens=50
            )
            
            print("✅ OpenAI API connection successful!")
            print(f"📊 Model: {response.model}")
            print(f"💬 Response: {response.choices[0].message.content}")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI API connection failed: {e}")
            return False
    
    def extract_tournament_data(self, content_text, source_url=""):
        """Extract structured tournament data from scraped content using OpenAI."""
        
        prompt = f"""
        You are a tournament data extraction expert. Extract tournament information from the following web content and return it as a JSON array.

        For each tournament found, extract:
        - tournament_name: Full name of the tournament
        - sport: The sport (Cricket, Football, Badminton, etc.)
        - level: Tournament level (School, College, Corporate, State, National, etc.)
        - start_date: Start date (YYYY-MM-DD format if available, otherwise "TBD")
        - end_date: End date (YYYY-MM-DD format if available, otherwise "TBD")
        - official_url: Official tournament website URL if mentioned
        - streaming_links: Array of streaming/broadcast links if available
        - image_url: Tournament poster/logo image URL if available
        - summary: Brief summary of the tournament (max 50 words)

        Only extract tournaments that are clearly mentioned in the content. If no specific tournaments are found, return an empty array.

        Source URL: {source_url}
        Content:
        {content_text}

        Return ONLY a valid JSON array, no other text:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse the JSON response
            json_text = response.choices[0].message.content.strip()
            
            # Clean up common JSON formatting issues
            if json_text.startswith('```json'):
                json_text = json_text.replace('```json', '').replace('```', '').strip()
            
            tournaments = json.loads(json_text)
            return tournaments
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw response: {response.choices[0].message.content}")
            return []
        except Exception as e:
            print(f"❌ OpenAI extraction error: {e}")
            return []

def test_with_sample_content():
    """Test tournament extraction with sample cricket content."""
    
    extractor = TournamentExtractor()
    
    # Sample content from our previous Firecrawl results
    sample_content = """
    Indian cricket schedule 2025: Women's ODI Cricket World Cup, ICC Men's Champions Trophy headline calendar - full list

    The Indian men's team will start their World Test Championship 2025-27 cycle with a five-match series in England in June. Know the upcoming tours and series.

    India Men's Cricket Team's Series and Tournaments - BCCI
    
    Series and Tournaments:
    
    INDIA TOUR OF ENGLAND 2025
    5 Test(s) · 20 Jun - 4 Aug
    
    INDIA MENS U19 TOUR OF ENGLAND 2025  
    2 Test(s) 5 ODI(s) · 27 Jun - 23 Jul
    
    ICC Men's Champions Trophy 2025
    Pakistan · Feb-Mar 2025
    
    Women's ODI Cricket World Cup 2025
    India · Oct-Nov 2025
    
    Indian Premier League 2025
    Mar-Jun 2025 (in India)
    
    World Test Championship 2025-27 cycle
    Starting June 2025
    """
    
    print("🔍 Testing tournament extraction with sample cricket content...")
    
    tournaments = extractor.extract_tournament_data(
        sample_content, 
        "https://www.bcci.tv/international/men/series-and-tournaments"
    )
    
    if tournaments:
        print(f"✅ Successfully extracted {len(tournaments)} tournaments!")
        
        for i, tournament in enumerate(tournaments, 1):
            print(f"\n🏆 Tournament {i}:")
            print(f"   Name: {tournament.get('tournament_name', 'N/A')}")
            print(f"   Sport: {tournament.get('sport', 'N/A')}")
            print(f"   Level: {tournament.get('level', 'N/A')}")
            print(f"   Dates: {tournament.get('start_date', 'N/A')} to {tournament.get('end_date', 'N/A')}")
            print(f"   Summary: {tournament.get('summary', 'N/A')}")
        
        # Save results
        with open('test_openai_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(tournaments, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to 'test_openai_extraction.json'")
        
        return True
    else:
        print("❌ No tournaments extracted")
        return False

def test_with_firecrawl_content():
    """Test with actual Firecrawl scraped content if available."""
    
    extractor = TournamentExtractor()
    
    # Try to load content from our previous Firecrawl test
    content_files = ['test_firecrawl_content_1.json', 'test_firecrawl_content_2.json']
    
    for filename in content_files:
        if os.path.exists(filename):
            print(f"\n🔍 Testing with content from {filename}")
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                content = data.get('markdown', '')
                url = data.get('url', '')
                
                if content:
                    # Clean up the content (remove the wrapper text)
                    if content.startswith("url=None markdown='"):
                        content = content[19:]  # Remove the prefix
                    if content.endswith("'"):
                        content = content[:-1]  # Remove the suffix
                    
                    tournaments = extractor.extract_tournament_data(content, url)
                    
                    if tournaments:
                        print(f"✅ Extracted {len(tournaments)} tournaments from {filename}")
                        
                        for tournament in tournaments:
                            print(f"   🏆 {tournament.get('tournament_name', 'N/A')}")
                    else:
                        print(f"⚠️  No tournaments found in {filename}")
                        
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

def main():
    """Main test function."""
    print("🚀 Testing OpenAI API Integration for Tournament Extraction")
    print("=" * 65)
    
    extractor = TournamentExtractor()
    
    # Test 1: Basic API connection
    print("🔌 Step 1: Testing API Connection")
    if not extractor.test_api_connection():
        return
    
    print("\n" + "="*65)
    
    # Test 2: Tournament extraction with sample content
    print("📋 Step 2: Testing Tournament Extraction")
    success = test_with_sample_content()
    
    # Test 3: Test with actual scraped content if available
    print("\n" + "="*65)
    print("📄 Step 3: Testing with Previously Scraped Content")
    test_with_firecrawl_content()
    
    print("\n" + "="*65)
    if success:
        print("✅ OpenAI integration test completed successfully!")
        print("🚀 Ready to proceed with full pipeline integration")
    else:
        print("❌ OpenAI integration test failed")
        print("🔧 Please check your API key and try again")

if __name__ == "__main__":
    main()
