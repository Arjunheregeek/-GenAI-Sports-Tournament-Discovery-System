"""
Search Results Collector Module

Collects search results using Serper API with comprehensive filtering and ranking.
Supports batch processing and intelligent result filtering.
"""

import json
import requests
import time
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from .config import SPORTS_LIST, LEVELS_LIST, APIConfig

# Load environment variables
load_dotenv()

class SearchResultsCollector:
    """Collects and processes search results using Serper API."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.api_key = self.api_config.serper_api_key
        self.base_url = self.api_config.serper_base_url
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        self.rate_limit_delay = self.api_config.serper_rate_limit
        self.max_retries = self.api_config.max_retries
        self.timeout = self.api_config.request_timeout
    
    def validate_api_key(self) -> bool:
        """Validate Serper API key before starting."""
        if not self.api_key or self.api_key == 'your_serper_api_key_here':
            print("❌ SERPER_API_KEY not found or not set in .env file")
            return False
        return True
    
    def search_query(self, query: str, num_results: int = 10, retries: int = 0) -> Optional[Dict]:
        """Search a single query using Serper API with retry logic."""
        
        payload = {
            'q': query,
            'num': num_results,
            'hl': 'en',
            'gl': 'in',  # Geo-location set to India
            'type': 'search'
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                if retries < self.max_retries:
                    wait_time = (retries + 1) * 2  # Exponential backoff
                    print(f"Rate limit hit, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    return self.search_query(query, num_results, retries + 1)
                else:
                    print(f"Rate limit exceeded for query: '{query}'")
                    return None
            elif response.status_code == 401:
                print(f"Authentication error - check API key")
                return None
            else:
                print(f"Error searching '{query}': Status {response.status_code}")
                if retries < self.max_retries:
                    time.sleep(2)
                    return self.search_query(query, num_results, retries + 1)
                return None
                
        except requests.exceptions.Timeout:
            if retries < self.max_retries:
                print(f"Timeout for '{query}', retrying...")
                time.sleep(2)
                return self.search_query(query, num_results, retries + 1)
            print(f"Timeout exceeded for query: '{query}'")
            return None
        except Exception as e:
            print(f"Exception searching '{query}': {e}")
            return None
    
    def extract_search_results(self, search_response: Dict, original_query: Dict) -> List[Dict]:
        """Extract and enrich search results from Serper API response."""
        results = []
        
        # Extract organic results
        if 'organic' in search_response:
            for result in search_response['organic']:
                enriched_result = {
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'position': result.get('position', 0),
                    'domain': self.extract_domain(result.get('link', '')),
                    'sport': original_query.get('sport', ''),
                    'level': original_query.get('level', ''),
                    'original_query': original_query.get('query', ''),
                    'query_type': original_query.get('type', 'standard'),
                    'search_date': '2025-08-02'
                }
                
                # Add sitelinks if available
                if 'sitelinks' in result:
                    enriched_result['sitelinks'] = result['sitelinks']
                
                results.append(enriched_result)
        
        # Extract related searches for additional queries
        if 'relatedSearches' in search_response:
            for related in search_response['relatedSearches']:
                results.append({
                    'type': 'related_search',
                    'query': related.get('query', ''),
                    'sport': original_query.get('sport', ''),
                    'level': original_query.get('level', ''),
                    'original_query': original_query.get('query', '')
                })
        
        return results
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ''
    
    def load_queries(self, filename: str = "search_queries_complete.json") -> List[Dict]:
        """Load queries from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both old and new format
            if isinstance(data, dict) and 'queries' in data:
                queries = data['queries']
                print(f"✅ Loaded {len(queries)} queries from {filename}")
                print(f"📊 Metadata: {data.get('metadata', {})}")
            else:
                queries = data
                print(f"✅ Loaded {len(queries)} queries from {filename}")
            
            return queries
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Please generate queries first.")
            return []
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            return []
    
    def filter_relevant_results(self, results: List[Dict]) -> List[Dict]:
        """Filter results to keep only tournament-related links with enhanced filtering."""
        
        # Enhanced keywords for better filtering
        relevant_keywords = [
            # Tournament terms
            'tournament', 'championship', 'competition', 'league', 'cup', 'series',
            'match', 'fixture', 'schedule', 'calendar', 'event',
            
            # Registration and info terms
            'register', 'registration', 'entry', 'participate', 'apply',
            'official', 'website', 'portal', 'form',
            
            # Sports organizations
            'federation', 'association', 'board', 'council', 'committee',
            'academy', 'club', 'society',
            
            # Educational institutions
            'school', 'college', 'university', 'institute', 'academy',
            
            # Government and corporate
            'government', 'ministry', 'department', 'corporate', 'company',
            
            # Location terms
            'india', 'indian', 'national', 'state', 'district', 'city'
        ]
        
        # Exclude irrelevant domains
        excluded_domains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com',
            'linkedin.com', 'pinterest.com', 'reddit.com', 'quora.com',
            'wikipedia.org'  # Remove if we want to keep Wikipedia
        ]
        
        filtered_results = []
        
        for result in results:
            if result.get('type') == 'related_search':
                filtered_results.append(result)
                continue
                
            title_lower = result.get('title', '').lower()
            snippet_lower = result.get('snippet', '').lower()
            link_lower = result.get('link', '').lower()
            domain = result.get('domain', '').lower()
            
            # Skip excluded domains
            if any(excluded in domain for excluded in excluded_domains):
                continue
            
            # Check if any relevant keywords are present
            text_to_search = f"{title_lower} {snippet_lower} {link_lower}"
            has_relevant_keyword = any(keyword in text_to_search for keyword in relevant_keywords)
            
            # Additional sport-specific filtering
            sport = result.get('sport', '').lower()
            has_sport_mention = sport in text_to_search
            
            if has_relevant_keyword or has_sport_mention:
                # Calculate relevance score
                result['relevance_score'] = self.calculate_relevance_score(result, relevant_keywords)
                filtered_results.append(result)
        
        return filtered_results
    
    def calculate_relevance_score(self, result: Dict, keywords: List[str]) -> float:
        """Calculate relevance score for ranking results."""
        score = 0.0
        
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        domain = result.get('domain', '').lower()
        
        # Title relevance (higher weight)
        for keyword in keywords:
            if keyword in title:
                score += 2.0
        
        # Snippet relevance
        for keyword in keywords:
            if keyword in snippet:
                score += 1.0
        
        # Domain credibility
        credible_domains = ['gov.in', 'edu', 'org', 'official', 'bcci', 'aiff', 'hockey', 'badminton']
        for domain_part in credible_domains:
            if domain_part in domain:
                score += 3.0
        
        # Position bonus (higher positions get bonus)
        position = result.get('position', 10)
        score += max(0, (10 - position) * 0.1)
        
        return round(score, 2)
    
    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs while keeping the best result."""
        url_dict = {}
        
        for result in results:
            if result.get('type') == 'related_search':
                continue
                
            url = result.get('link', '')
            if not url:
                continue
            
            # Normalize URL
            url = url.lower().rstrip('/')
            
            if url not in url_dict:
                url_dict[url] = result
            else:
                # Keep result with higher relevance score or better position
                existing = url_dict[url]
                current_score = result.get('relevance_score', 0)
                existing_score = existing.get('relevance_score', 0)
                
                if current_score > existing_score:
                    url_dict[url] = result
                elif current_score == existing_score:
                    # Use position as tiebreaker
                    if result.get('position', 10) < existing.get('position', 10):
                        url_dict[url] = result
        
        # Add back related searches
        deduplicated = list(url_dict.values())
        for result in results:
            if result.get('type') == 'related_search':
                deduplicated.append(result)
        
        return deduplicated
    
    def search_all_queries(self, queries: List[Dict], max_queries: int = None) -> List[Dict]:
        """Search all queries and collect results with progress tracking."""
        
        if not self.validate_api_key():
            return []
        
        if max_queries:
            queries = queries[:max_queries]
            print(f"🔢 Limited to first {max_queries} queries for testing")
        
        all_results = []
        total_queries = len(queries)
        successful_searches = 0
        failed_searches = 0
        
        print(f"🔍 Starting search for {total_queries} queries...")
        print(f"⏱️  Estimated time: {total_queries * self.rate_limit_delay / 60:.1f} minutes")
        
        for i, query_info in enumerate(queries):
            # Progress indicator
            if i % 50 == 0 or i == total_queries - 1:
                print(f"📊 Progress: {i+1}/{total_queries} ({((i+1)/total_queries)*100:.1f}%)")
            
            search_response = self.search_query(query_info['query'])
            
            if search_response:
                search_results = self.extract_search_results(search_response, query_info)
                all_results.extend(search_results)
                successful_searches += 1
            else:
                failed_searches += 1
            
            # Rate limiting
            if i < total_queries - 1:  # Don't wait after last query
                time.sleep(self.rate_limit_delay)
        
        print(f"✅ Search completed: {successful_searches} successful, {failed_searches} failed")
        return all_results
    
    def save_results(self, results: List[Dict], filename: str = "search_results_complete.json") -> str:
        """Save search results with comprehensive metadata."""
        
        # Generate statistics
        stats = self.generate_result_statistics(results)
        
        # Prepare data with metadata
        result_data = {
            "metadata": {
                "total_results": len(results),
                "search_date": "2025-08-02T00:00:00Z",
                "api_used": "Serper API",
                "version": "1.0",
                "statistics": stats
            },
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(results)} search results to {filename}")
        return filename
    
    def generate_result_statistics(self, results: List[Dict]) -> Dict:
        """Generate comprehensive statistics about search results."""
        stats = {
            "total_results": len(results),
            "by_sport": {},
            "by_level": {},
            "by_domain": {},
            "by_type": {},
            "average_relevance_score": 0.0,
            "top_domains": []
        }
        
        relevance_scores = []
        domain_counts = {}
        
        for result in results:
            # Count by sport
            sport = result.get('sport', 'Unknown')
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            
            # Count by level
            level = result.get('level', 'Unknown')
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Count by type
            result_type = result.get('type', 'organic')
            stats["by_type"][result_type] = stats["by_type"].get(result_type, 0) + 1
            
            # Domain statistics
            domain = result.get('domain', '')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Relevance scores
            score = result.get('relevance_score', 0)
            if score > 0:
                relevance_scores.append(score)
        
        # Calculate average relevance score
        if relevance_scores:
            stats["average_relevance_score"] = round(sum(relevance_scores) / len(relevance_scores), 2)
        
        # Top domains
        stats["top_domains"] = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return stats

def main():
    """Main function to search all queries and collect results."""
    print("=" * 60)
    print("🚀 Complete Search Results Collection")
    print("=" * 60)
    
    collector = SearchResultsCollector()
    
    # Load queries from Step 1
    print("📂 Loading queries...")
    queries = collector.load_queries()
    if not queries:
        return
    
    # For testing, limit queries (remove this for full run)
    # queries = queries[:100]  # Uncomment to test with fewer queries
    
    print(f"🔍 Loaded {len(queries)} queries")
    
    # Search all queries
    print("\n🌐 Starting comprehensive search...")
    all_results = collector.search_all_queries(queries)
    
    if not all_results:
        print("❌ No results found. Check API key and network connection.")
        return
    
    print(f"\n📊 Total results found: {len(all_results)}")
    
    # Filter relevant results
    print("🔍 Filtering relevant results...")
    relevant_results = collector.filter_relevant_results(all_results)
    print(f"✅ Relevant results: {len(relevant_results)}")
    
    # Remove duplicates
    print("🧹 Removing duplicates...")
    final_results = collector.deduplicate_results(relevant_results)
    print(f"✅ Final unique results: {len(final_results)}")
    
    # Sort by relevance score
    final_results = sorted(final_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Save results
    print("💾 Saving results...")
    filename = collector.save_results(final_results)
    
    # Display summary
    print("\n" + "=" * 60)
    print("✅ Search Results Collection Complete!")
    print(f"📁 Saved to: {filename}")
    print(f"🎯 Ready for Step 3: Content Extraction")
    
    # Show sample high-quality results
    print("\n🏆 Top 5 Results by Relevance:")
    for i, result in enumerate(final_results[:5], 1):
        if result.get('type') != 'related_search':
            print(f"\n{i}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('link', 'N/A')}")
            print(f"   Sport: {result.get('sport')} | Level: {result.get('level')}")
            print(f"   Score: {result.get('relevance_score', 0)} | Domain: {result.get('domain', 'N/A')}")

if __name__ == "__main__":
    main()
