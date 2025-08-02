"""
Content Extractor Module

Extracts webpage content using Firecrawl API with comprehensive processing.
Supports batch extraction and content quality filtering.
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from .config import APIConfig

# Load environment variables
load_dotenv()

class ContentExtractor:
    """Extracts content from web pages using Firecrawl API."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.api_key = self.api_config.firecrawl_api_key
        self.app = None
        self.rate_limit_delay = self.api_config.firecrawl_rate_limit
        self.max_retries = self.api_config.max_retries
        self.timeout = self.api_config.request_timeout
        
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
            print("✅ Firecrawl API initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing Firecrawl API: {e}")
            return False
    
    def extract_single_url(self, url: str, retries: int = 0) -> Optional[Dict]:
        """Extract content from a single URL with retry logic."""
        
        if not self.app:
            print("❌ Firecrawl not initialized")
            return None
        
        try:
            print(f"🔄 Extracting content from: {url}")
            
            # Use scrape method for single URL extraction - Fixed API format
            result = self.app.scrape_url(url, formats=['markdown', 'html'])
            
            # Parse the result based on Firecrawl API response format
            if result:
                # Get the scraped data - Firecrawl returns response with 'data' attribute
                if hasattr(result, 'data') and result.data:
                    data = result.data
                    content_dict = {
                        'title': data.get('metadata', {}).get('title', ''),
                        'content': data.get('markdown', ''),
                        'markdown': data.get('markdown', ''),
                        'html': data.get('html', ''),
                        'metadata': data.get('metadata', {})
                    }
                else:
                    # Fallback for different response format
                    content_dict = {
                        'title': '',
                        'content': str(result)[:1000] if result else '',
                        'markdown': str(result)[:1000] if result else '',
                        'html': '',
                        'metadata': {}
                    }
                
                # Process and validate content
                processed_content = self.process_extracted_content(content_dict, url)
                return processed_content
            else:
                print(f"⚠️ No content returned for {url}")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting from {url}: {e}")
            
            if retries < self.max_retries:
                print(f"🔄 Retrying... ({retries + 1}/{self.max_retries})")
                time.sleep(2 ** retries)  # Exponential backoff
                return self.extract_single_url(url, retries + 1)
            
            return None
    
    def process_extracted_content(self, raw_result: Dict, url: str) -> Dict:
        """Process and enrich extracted content."""
        
        content = raw_result.get('content', '')
        markdown = raw_result.get('markdown', '')
        html = raw_result.get('html', '')
        
        # Create processed content structure
        processed = {
            'url': url,
            'title': raw_result.get('title', ''),
            'content': content,
            'markdown': markdown,
            'html': html,
            'extraction_date': datetime.now().isoformat(),
            'word_count': len(content.split()) if content else 0,
            'char_count': len(content) if content else 0,
            'quality_score': 0.0,
            'structured_data': {}
        }
        
        # Calculate quality score
        processed['quality_score'] = self.calculate_content_quality(processed)
        
        # Extract structured data if available
        if 'llm_extraction' in raw_result:
            processed['structured_data'] = raw_result['llm_extraction']
        
        # Extract additional metadata
        processed.update(self.extract_metadata(raw_result))
        
        return processed
    
    def calculate_content_quality(self, content_data: Dict) -> float:
        """Calculate quality score for extracted content."""
        score = 0.0
        
        content = content_data.get('content', '')
        title = content_data.get('title', '')
        word_count = content_data.get('word_count', 0)
        
        # Length score (0-3 points)
        if word_count >= 500:
            score += 3.0
        elif word_count >= 200:
            score += 2.0
        elif word_count >= 100:
            score += 1.0
        
        # Title quality (0-2 points)
        if title and len(title) > 10:
            score += 1.0
            if any(keyword in title.lower() for keyword in ['tournament', 'championship', 'competition', 'league']):
                score += 1.0
        
        # Content relevance (0-3 points)
        tournament_keywords = ['tournament', 'registration', 'date', 'venue', 'prize', 'entry', 'competition']
        keyword_count = sum(1 for keyword in tournament_keywords if keyword in content.lower())
        score += min(3.0, keyword_count * 0.5)
        
        # Structure indicators (0-2 points)
        if any(indicator in content.lower() for indicator in ['registration', 'contact', 'venue', 'prize']):
            score += 1.0
        if any(indicator in content.lower() for indicator in ['date', 'time', 'deadline']):
            score += 1.0
        
        return round(min(10.0, score), 2)
    
    def extract_metadata(self, raw_result: Dict) -> Dict:
        """Extract additional metadata from raw result."""
        metadata = {}
        
        # Extract meta tags if available
        if 'metadata' in raw_result:
            meta = raw_result['metadata']
            metadata.update({
                'description': meta.get('description', ''),
                'keywords': meta.get('keywords', ''),
                'author': meta.get('author', ''),
                'language': meta.get('language', 'en')
            })
        
        # Extract links
        if 'links' in raw_result:
            metadata['internal_links'] = raw_result['links']
        
        # Extract images
        if 'screenshot' in raw_result:
            metadata['screenshot_url'] = raw_result['screenshot']
        
        return metadata
    
    def load_search_results(self, filename: str = "search_results_complete.json") -> List[Dict]:
        """Load search results from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both old and new format
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
                print(f"✅ Loaded {len(results)} search results from {filename}")
            else:
                results = data
                print(f"✅ Loaded {len(results)} search results from {filename}")
            
            return results
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please run search collection first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def filter_extractable_urls(self, search_results: List[Dict]) -> List[Dict]:
        """Filter URLs that are suitable for content extraction."""
        
        extractable_results = []
        
        # Skip certain types of URLs
        skip_patterns = [
            'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com',
            'linkedin.com', 'pinterest.com', 'reddit.com'
        ]
        
        for result in search_results:
            if result.get('type') == 'related_search':
                continue
            
            url = result.get('link', '')
            domain = result.get('domain', '')
            
            # Skip problematic domains
            if any(pattern in domain.lower() for pattern in skip_patterns):
                continue
            
            # Skip non-HTTP URLs
            if not url.startswith(('http://', 'https://')):
                continue
            
            # Only process URLs with decent relevance scores
            relevance_score = result.get('relevance_score', 0)
            if relevance_score < 1.0:
                continue
            
            extractable_results.append(result)
        
        return extractable_results
    
    def extract_all_content(self, search_results: List[Dict], max_urls: int = None) -> List[Dict]:
        """Extract content from all search result URLs."""
        
        if not self.validate_and_initialize():
            return []
        
        # Filter extractable URLs
        extractable_urls = self.filter_extractable_urls(search_results)
        
        if max_urls:
            extractable_urls = extractable_urls[:max_urls]
            print(f"🔢 Limited to first {max_urls} URLs for extraction")
        
        extracted_content = []
        total_urls = len(extractable_urls)
        successful_extractions = 0
        failed_extractions = 0
        
        print(f"🌐 Starting content extraction for {total_urls} URLs...")
        print(f"⏱️  Estimated time: {total_urls * self.rate_limit_delay / 60:.1f} minutes")
        
        for i, result in enumerate(extractable_urls):
            url = result.get('link', '')
            
            # Progress indicator
            if i % 10 == 0 or i == total_urls - 1:
                print(f"📊 Progress: {i+1}/{total_urls} ({((i+1)/total_urls)*100:.1f}%)")
            
            # Extract content
            content = self.extract_single_url(url)
            
            if content:
                # Enrich with search result metadata
                content.update({
                    'search_title': result.get('title', ''),
                    'search_snippet': result.get('snippet', ''),
                    'sport': result.get('sport', ''),
                    'level': result.get('level', ''),
                    'original_query': result.get('original_query', ''),
                    'relevance_score': result.get('relevance_score', 0)
                })
                
                extracted_content.append(content)
                successful_extractions += 1
            else:
                failed_extractions += 1
            
            # Rate limiting
            if i < total_urls - 1:
                time.sleep(self.rate_limit_delay)
        
        print(f"✅ Content extraction completed: {successful_extractions} successful, {failed_extractions} failed")
        return extracted_content
    
    def save_extracted_content(self, content_list: List[Dict], filename: str = "extracted_content_complete.json") -> str:
        """Save extracted content with metadata."""
        
        # Generate statistics
        stats = self.generate_extraction_statistics(content_list)
        
        # Prepare data with metadata
        content_data = {
            "metadata": {
                "total_extractions": len(content_list),
                "extraction_date": datetime.now().isoformat(),
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
    
    def generate_extraction_statistics(self, content_list: List[Dict]) -> Dict:
        """Generate statistics about extracted content."""
        if not content_list:
            return {}
        
        stats = {
            "total_content": len(content_list),
            "by_sport": {},
            "by_level": {},
            "quality_distribution": {},
            "average_quality_score": 0.0,
            "average_word_count": 0.0,
            "total_words": 0
        }
        
        quality_scores = []
        word_counts = []
        
        for content in content_list:
            # Count by sport
            sport = content.get('sport', 'Unknown')
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            
            # Count by level
            level = content.get('level', 'Unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Quality score distribution
            quality = content.get('quality_score', 0)
            quality_range = f"{int(quality)}-{int(quality)+1}"
            stats["quality_distribution"][quality_range] = stats["quality_distribution"].get(quality_range, 0) + 1
            
            if quality > 0:
                quality_scores.append(quality)
            
            # Word count statistics
            word_count = content.get('word_count', 0)
            if word_count > 0:
                word_counts.append(word_count)
                stats["total_words"] += word_count
        
        # Calculate averages
        if quality_scores:
            stats["average_quality_score"] = round(sum(quality_scores) / len(quality_scores), 2)
        
        if word_counts:
            stats["average_word_count"] = round(sum(word_counts) / len(word_counts), 1)
        
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
    
    print(f"🔍 Loaded {len(search_results)} search results")
    
    # For testing, limit URLs (remove this for full run)
    # max_urls = 50  # Uncomment to test with fewer URLs
    max_urls = None
    
    # Extract content from all URLs
    print("\n🌐 Starting comprehensive content extraction...")
    extracted_content = extractor.extract_all_content(search_results, max_urls)
    
    if not extracted_content:
        print("❌ No content extracted. Check API key and network connection.")
        return
    
    print(f"\n📊 Total content extracted: {len(extracted_content)}")
    
    # Filter high-quality content
    high_quality_content = [c for c in extracted_content if c.get('quality_score', 0) >= 3.0]
    print(f"🏆 High-quality content (score ≥ 3.0): {len(high_quality_content)}")
    
    # Save all extracted content
    print("💾 Saving extracted content...")
    filename = extractor.save_extracted_content(extracted_content)
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Content Extraction Complete!")
    print(f"📁 Saved to: {filename}")
    print(f"🎯 Ready for Step 4: Tournament Data Processing")
    
    # Show sample high-quality content
    print("\n🏆 Top 5 Content by Quality Score:")
    sorted_content = sorted(extracted_content, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    for i, content in enumerate(sorted_content[:5], 1):
        print(f"\n{i}. {content.get('title', 'N/A')}")
        print(f"   URL: {content.get('url', 'N/A')}")
        print(f"   Sport: {content.get('sport')} | Level: {content.get('level')}")
        print(f"   Quality: {content.get('quality_score', 0)} | Words: {content.get('word_count', 0)}")

if __name__ == "__main__":
    main()
