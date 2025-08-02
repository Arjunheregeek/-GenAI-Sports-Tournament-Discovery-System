"""
Step 3: Extract Page Content using Firecrawl API
Complete production version with comprehensive content extraction and processing.
"""

import json
import os
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

class ContentExtractor:
    def __init__(self):
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        self.app = None
        self.rate_limit_delay = 2.0  # Seconds between requests (Firecrawl may have stricter limits)
        self.max_retries = 3
        self.timeout = 60
        
        # Content quality thresholds
        self.min_content_length = 100
        self.max_content_length = 50000
    
    def validate_and_initialize(self) -> bool:
        """Validate API key and initialize Firecrawl app."""
        if not self.api_key or self.api_key == 'your_firecrawl_api_key_here':
            print("❌ FIRECRAWL_API_KEY not found or not set in .env file")
            return False
        
        try:
            self.app = FirecrawlApp(api_key=self.api_key)
            print("✅ Firecrawl app initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Firecrawl: {e}")
            return False
    
    def load_search_results(self, filename: str = "search_results_complete.json") -> List[Dict]:
        """Load search results from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
                print(f"✅ Loaded {len(results)} search results from {filename}")
                print(f"📊 Metadata: {data.get('metadata', {})}")
            else:
                results = data
                print(f"✅ Loaded {len(results)} search results from {filename}")
            
            # Filter out non-organic results
            organic_results = [r for r in results if r.get('type', 'organic') == 'organic' and r.get('link')]
            print(f"🔗 Found {len(organic_results)} URLs to extract content from")
            
            return organic_results
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run step2_search_results.py first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def extract_single_page(self, url: str, retries: int = 0) -> Optional[Dict]:
        """Extract content from a single page using Firecrawl API."""
        
        if not self.app:
            return None
        
        try:
            # Use Firecrawl to scrape the page
            result = self.app.scrape_url(url, formats=['markdown', 'html'])
            
            if not result:
                return None
            
            # Extract data from Firecrawl response
            if hasattr(result, 'data') and result.data:
                data = result.data
                content_data = {
                    'url': url,
                    'title': data.get('metadata', {}).get('title', ''),
                    'markdown': data.get('markdown', ''),
                    'html': data.get('html', ''),
                    'metadata': data.get('metadata', {}),
                    'extraction_success': True,
                    'extraction_date': '2025-08-02',
                    'content_length': len(data.get('markdown', '')),
                    'quality_score': self.calculate_content_quality(data.get('markdown', ''), data.get('metadata', {}))
                }
            else:
                # Fallback for different response format
                content_data = {
                    'url': url,
                    'title': getattr(result, 'title', ''),
                    'markdown': str(result)[:self.max_content_length] if result else '',
                    'html': '',
                    'metadata': {},
                    'extraction_success': True,
                    'extraction_date': '2025-08-02',
                    'content_length': len(str(result)) if result else 0,
                    'quality_score': 1.0
                }
            
            return content_data
            
        except Exception as e:
            if retries < self.max_retries:
                print(f"⚠️  Retry {retries + 1} for {url}: {str(e)[:100]}")
                time.sleep(2 ** retries)  # Exponential backoff
                return self.extract_single_page(url, retries + 1)
            else:
                print(f"❌ Failed to extract {url} after {self.max_retries} retries: {e}")
                return {
                    'url': url,
                    'title': '',
                    'markdown': '',
                    'html': '',
                    'metadata': {},
                    'extraction_success': False,
                    'extraction_date': '2025-08-02',
                    'content_length': 0,
                    'quality_score': 0.0,
                    'error': str(e)
                }
    
    def calculate_content_quality(self, content: str, metadata: Dict) -> float:
        """Calculate quality score for extracted content."""
        score = 0.0
        
        if not content:
            return 0.0
        
        # Length score (optimal range: 500-10000 characters)
        length = len(content)
        if length < self.min_content_length:
            length_score = 0.0
        elif length > self.max_content_length:
            length_score = 0.5
        else:
            # Optimal length gets higher score
            length_score = min(1.0, length / 2000)  # Max score at 2000+ chars
        
        score += length_score * 0.3
        
        # Tournament-related keywords score
        tournament_keywords = [
            'tournament', 'championship', 'competition', 'league', 'cup',
            'register', 'registration', 'schedule', 'date', 'venue',
            'participate', 'entry', 'form', 'deadline', 'fee'
        ]
        
        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in tournament_keywords if keyword in content_lower)
        keyword_score = min(1.0, keyword_matches / len(tournament_keywords))
        score += keyword_score * 0.4
        
        # Metadata quality score
        title = metadata.get('title', '')
        description = metadata.get('description', '')
        if title and len(title) > 10:
            score += 0.1
        if description and len(description) > 20:
            score += 0.1
        
        # Structured content indicators
        structured_indicators = ['date', 'time', 'venue', 'contact', 'phone', 'email', 'website']
        structured_matches = sum(1 for indicator in structured_indicators if indicator in content_lower)
        structured_score = min(1.0, structured_matches / len(structured_indicators))
        score += structured_score * 0.1
        
        return round(min(1.0, score), 2)
    
    def prioritize_urls(self, search_results: List[Dict]) -> List[Dict]:
        """Prioritize URLs based on relevance and likelihood of containing tournament info."""
        
        # Priority scoring
        for result in search_results:
            priority_score = result.get('relevance_score', 0)
            
            # Domain-based priorities
            domain = result.get('domain', '').lower()
            high_priority_domains = [
                'gov.in', 'edu', 'bcci.tv', 'aiff.in', 'hockeyindia.org',
                'badmintonindia.org', 'tabletennis.org.in', 'aainet.org'
            ]
            
            medium_priority_domains = [
                'sportskeeda.com', 'espncricinfo.com', 'olympics.com',
                'sportstar.thehindu.com', 'indianexpress.com'
            ]
            
            if any(hp_domain in domain for hp_domain in high_priority_domains):
                priority_score += 5.0
            elif any(mp_domain in domain for mp_domain in medium_priority_domains):
                priority_score += 2.0
            
            # Title-based priorities
            title = result.get('title', '').lower()
            high_priority_terms = ['official', 'registration', 'schedule', 'tournament']
            for term in high_priority_terms:
                if term in title:
                    priority_score += 1.0
            
            result['priority_score'] = priority_score
        
        # Sort by priority score
        return sorted(search_results, key=lambda x: x.get('priority_score', 0), reverse=True)
    
    def extract_all_content(self, search_results: List[Dict], max_pages: int = None) -> List[Dict]:
        """Extract content from all URLs with progress tracking."""
        
        if not self.validate_and_initialize():
            return []
        
        # Prioritize URLs
        prioritized_results = self.prioritize_urls(search_results)
        
        if max_pages:
            prioritized_results = prioritized_results[:max_pages]
            print(f"🔢 Limited to top {max_pages} priority URLs")
        
        extracted_content = []
        total_urls = len(prioritized_results)
        successful_extractions = 0
        failed_extractions = 0
        
        print(f"🌐 Starting content extraction for {total_urls} URLs...")
        print(f"⏱️  Estimated time: {total_urls * self.rate_limit_delay / 60:.1f} minutes")
        
        for i, result in enumerate(prioritized_results):
            url = result.get('link', '')
            if not url:
                continue
            
            # Progress indicator
            if i % 10 == 0 or i == total_urls - 1:
                print(f"📊 Progress: {i+1}/{total_urls} ({((i+1)/total_urls)*100:.1f}%)")
            
            print(f"🔍 Extracting: {result.get('domain', 'unknown')} - {result.get('sport')} {result.get('level')}")
            
            content = self.extract_single_page(url)
            
            if content:
                # Add search result metadata to extracted content
                content.update({
                    'sport': result.get('sport', ''),
                    'level': result.get('level', ''),
                    'original_query': result.get('original_query', ''),
                    'search_position': result.get('position', 0),
                    'relevance_score': result.get('relevance_score', 0),
                    'priority_score': result.get('priority_score', 0),
                    'domain': result.get('domain', ''),
                    'search_title': result.get('title', ''),
                    'search_snippet': result.get('snippet', '')
                })
                
                extracted_content.append(content)
                
                if content.get('extraction_success', False):
                    successful_extractions += 1
                else:
                    failed_extractions += 1
            else:
                failed_extractions += 1
            
            # Rate limiting
            if i < total_urls - 1:
                time.sleep(self.rate_limit_delay)
        
        print(f"✅ Content extraction completed: {successful_extractions} successful, {failed_extractions} failed")
        return extracted_content
    
    def filter_quality_content(self, content_list: List[Dict], min_quality: float = 0.3) -> List[Dict]:
        """Filter content based on quality score."""
        
        high_quality_content = []
        for content in content_list:
            if content.get('quality_score', 0) >= min_quality and content.get('extraction_success', False):
                high_quality_content.append(content)
        
        print(f"🏆 Filtered to {len(high_quality_content)} high-quality pages (score >= {min_quality})")
        return high_quality_content
    
    def save_extracted_content(self, content_list: List[Dict], filename: str = "extracted_content_complete.json"):
        """Save extracted content with comprehensive metadata."""
        
        # Generate statistics
        stats = self.generate_content_statistics(content_list)
        
        # Prepare data with metadata
        content_data = {
            "metadata": {
                "total_pages": len(content_list),
                "extraction_date": "2025-08-02T00:00:00Z",
                "api_used": "Firecrawl API",
                "version": "1.0",
                "statistics": stats
            },
            "content": content_list
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(content_list)} extracted content to {filename}")
        return filename
    
    def generate_content_statistics(self, content_list: List[Dict]) -> Dict:
        """Generate comprehensive statistics about extracted content."""
        stats = {
            "total_pages": len(content_list),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "by_sport": {},
            "by_level": {},
            "by_domain": {},
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "average_content_length": 0,
            "average_quality_score": 0.0
        }
        
        content_lengths = []
        quality_scores = []
        domain_counts = {}
        
        for content in content_list:
            # Success/failure count
            if content.get('extraction_success', False):
                stats["successful_extractions"] += 1
            else:
                stats["failed_extractions"] += 1
            
            # Count by sport
            sport = content.get('sport', 'Unknown')
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            
            # Count by level
            level = content.get('level', 'Unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Domain statistics
            domain = content.get('domain', '')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Quality distribution
            quality = content.get('quality_score', 0)
            if quality >= 0.7:
                stats["quality_distribution"]["high"] += 1
            elif quality >= 0.4:
                stats["quality_distribution"]["medium"] += 1
            else:
                stats["quality_distribution"]["low"] += 1
            
            # Collect metrics
            content_lengths.append(content.get('content_length', 0))
            quality_scores.append(quality)
        
        # Calculate averages
        if content_lengths:
            stats["average_content_length"] = round(sum(content_lengths) / len(content_lengths))
        
        if quality_scores:
            stats["average_quality_score"] = round(sum(quality_scores) / len(quality_scores), 2)
        
        # Top domains
        stats["top_domains"] = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return stats

def main():
    """Main function to extract content from all search results."""
    print("=" * 60)
    print("🚀 Complete Content Extraction")
    print("=" * 60)
    
    extractor = ContentExtractor()
    
    # Load search results from Step 2
    print("📂 Loading search results...")
    search_results = extractor.load_search_results()
    if not search_results:
        return
    
    # For testing, limit pages (remove this for full run)
    # search_results = search_results[:50]  # Uncomment to test with fewer pages
    
    print(f"🔗 Found {len(search_results)} URLs to process")
    
    # Extract content from all pages
    print("\n🌐 Starting comprehensive content extraction...")
    extracted_content = extractor.extract_all_content(search_results)
    
    if not extracted_content:
        print("❌ No content extracted. Check API key and network connection.")
        return
    
    print(f"\n📊 Total pages processed: {len(extracted_content)}")
    
    # Filter for quality content
    print("🏆 Filtering for high-quality content...")
    quality_content = extractor.filter_quality_content(extracted_content, min_quality=0.3)
    
    # Save all extracted content
    print("💾 Saving extracted content...")
    filename = extractor.save_extracted_content(quality_content)
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Content Extraction Complete!")
    print(f"📁 Saved to: {filename}")
    print(f"🎯 Ready for Step 4: Tournament Data Extraction")
    
    # Show sample high-quality content
    print("\n🏆 Top 3 Quality Extractions:")
    quality_sorted = sorted(quality_content, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    for i, content in enumerate(quality_sorted[:3], 1):
        print(f"\n{i}. {content.get('title', 'N/A')}")
        print(f"   URL: {content.get('url', 'N/A')}")
        print(f"   Sport: {content.get('sport')} | Level: {content.get('level')}")
        print(f"   Quality: {content.get('quality_score', 0)} | Length: {content.get('content_length', 0)} chars")
        print(f"   Preview: {content.get('markdown', '')[:150]}...")

if __name__ == "__main__":
    main()
