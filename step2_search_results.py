"""
Step 2: Get Search Results using Serper API
This script takes the generated queries and fetches search results.
"""

import json
import requests
import time
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SerperSearcher:
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def search_query(self, query: str, num_results: int = 10) -> Optional[Dict]:
        """Search a single query using Serper API."""
        
        payload = {
            'q': query,
            'num': num_results,
            'hl': 'en',
            'gl': 'in'  # Geo-location set to India
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error searching '{query}': Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception searching '{query}': {e}")
            return None
    
    def extract_search_results(self, search_response: Dict) -> List[Dict]:
        """Extract relevant information from Serper API response."""
        results = []
        
        # Extract organic results
        if 'organic' in search_response:
            for result in search_response['organic']:
                results.append({
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'position': result.get('position', 0)
                })
        
        return results
    
    def search_all_queries(self, queries: List[Dict], delay: float = 1.0) -> List[Dict]:
        """Search all queries and collect results."""
        all_results = []
        total_queries = len(queries)
        
        for i, query_info in enumerate(queries):
            print(f"Processing query {i+1}/{total_queries}: {query_info['sport']} - {query_info['level']}")
            
            search_response = self.search_query(query_info['query'])
            
            if search_response:
                search_results = self.extract_search_results(search_response)
                
                # Add metadata to each result
                for result in search_results:
                    result.update({
                        'sport': query_info['sport'],
                        'level': query_info['level'],
                        'original_query': query_info['query']
                    })
                
                all_results.extend(search_results)
                print(f"  Found {len(search_results)} results")
            else:
                print(f"  No results found")
            
            # Rate limiting
            time.sleep(delay)
        
        return all_results
    
    def filter_relevant_results(self, results: List[Dict]) -> List[Dict]:
        """Filter results to keep only tournament-related links."""
        
        # Keywords that indicate tournament/competition content
        relevant_keywords = [
            'tournament', 'championship', 'competition', 'league', 'cup',
            'register', 'registration', 'schedule', 'fixture', 'match',
            'sport', 'official', 'association', 'federation', 'board'
        ]
        
        filtered_results = []
        
        for result in results:
            title_lower = result['title'].lower()
            snippet_lower = result['snippet'].lower()
            link_lower = result['link'].lower()
            
            # Check if any relevant keywords are present
            has_relevant_keyword = any(
                keyword in title_lower or 
                keyword in snippet_lower or 
                keyword in link_lower
                for keyword in relevant_keywords
            )
            
            if has_relevant_keyword:
                filtered_results.append(result)
        
        return filtered_results
    
    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs while keeping the best result."""
        seen_urls = {}
        deduplicated = []
        
        for result in results:
            url = result['link']
            
            if url not in seen_urls:
                seen_urls[url] = result
                deduplicated.append(result)
            else:
                # Keep the result with better position (lower number = better)
                if result['position'] < seen_urls[url]['position']:
                    # Remove old result and add new one
                    deduplicated = [r for r in deduplicated if r['link'] != url]
                    deduplicated.append(result)
                    seen_urls[url] = result
        
        return deduplicated
    
    def save_results(self, results: List[Dict], filename: str = "search_results.json"):
        """Save search results to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(results)} search results to {filename}")
    
    def load_queries(self, filename: str = "search_queries.json") -> List[Dict]:
        """Load queries from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {filename} not found. Please run step1_generate_queries.py first.")
            return []

def main():
    """Main function to search all queries."""
    searcher = SerperSearcher()
    
    # Load queries from Step 1
    queries = searcher.load_queries()
    if not queries:
        return
    
    print(f"Loaded {len(queries)} queries")
    
    # Limit queries for testing (remove this limit for full run)
    # queries = queries[:20]  # Uncomment to test with fewer queries
    
    print("Starting search process...")
    all_results = searcher.search_all_queries(queries)
    
    print(f"\nTotal results found: {len(all_results)}")
    
    # Filter relevant results
    print("Filtering relevant results...")
    relevant_results = searcher.filter_relevant_results(all_results)
    print(f"Relevant results: {len(relevant_results)}")
    
    # Remove duplicates
    print("Removing duplicates...")
    final_results = searcher.deduplicate_results(relevant_results)
    print(f"Final unique results: {len(final_results)}")
    
    # Save results
    searcher.save_results(final_results)
    
    # Display sample results
    print("\nSample search results:")
    for i, result in enumerate(final_results[:5]):
        print(f"\n{i+1}. {result['title']}")
        print(f"   URL: {result['link']}")
        print(f"   Sport: {result['sport']}, Level: {result['level']}")
        print(f"   Snippet: {result['snippet'][:100]}...")

if __name__ == "__main__":
    main()
