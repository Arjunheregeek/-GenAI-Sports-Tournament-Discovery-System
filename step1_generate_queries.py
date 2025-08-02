"""
Step 1: Generate Search Queries for Tournament Calendar
Complete production version with all sports and levels from assignment.
"""

import json
from typing import List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from config import SPORTS_LIST, LEVELS_LIST

# Load environment variables
load_dotenv()

class QueryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sports = SPORTS_LIST
        self.levels = LEVELS_LIST
        
        # Query templates for different types of searches
        self.query_templates = [
            "Upcoming {sport} tournaments 2025 India {level} level",
            "{sport} championship {level} 2025 India registration dates",
            "{level} {sport} competition India 2025 schedule",
            "India {sport} tournament {level} 2025 official website",
            "{sport} inter {level} tournament 2025 India dates",
            "{level} level {sport} tournaments India 2025 calendar",
            "2025 {sport} {level} championship India venues dates",
            "India {sport} {level} league 2025 fixtures schedule",
            "{sport} {level} cup tournament India 2025 registration",
            "Best {sport} tournaments {level} India 2025 official"
        ]
    
    def generate_base_queries(self) -> List[Dict]:
        """Generate comprehensive search queries for all sport-level combinations."""
        queries = []
        
        print(f"Generating queries for {len(self.sports)} sports and {len(self.levels)} levels...")
        
        for sport in self.sports:
            for level in self.levels:
                # Generate multiple query variations for each combination
                for template in self.query_templates:
                    query = template.format(sport=sport, level=level)
                    queries.append({
                        "sport": sport,
                        "level": level,
                        "query": query,
                        "template": template
                    })
        
        return queries
    
    def enhance_queries_with_llm(self, base_queries: List[Dict], batch_size: int = 20) -> List[Dict]:
        """Use LLM to generate more sophisticated and diverse queries in batches."""
        
        enhanced_queries = base_queries.copy()
        
        # Process sports in batches to avoid token limits
        for i in range(0, len(self.sports), batch_size):
            sport_batch = self.sports[i:i + batch_size]
            
            prompt = f"""
            Generate 3 additional search queries for finding tournament information for each sport-level combination.
            Focus on finding official tournament websites, registration pages, and schedule information.
            
            Make queries specific to India and include year 2025.
            Vary the language and terms used (tournament, championship, competition, league, cup, series, etc.).
            Include local tournament searches for bonus points.
            
            Sports: {', '.join(sport_batch)}
            Levels: {', '.join(self.levels)}
            
            Return only the additional queries in this exact JSON format:
            [
                {{"sport": "Cricket", "level": "School", "query": "example query", "source": "llm_generated"}},
                ...
            ]
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # Parse the LLM response
                llm_response = response.choices[0].message.content.strip()
                if llm_response.startswith('```json'):
                    llm_response = llm_response.replace('```json', '').replace('```', '').strip()
                
                llm_queries = json.loads(llm_response)
                enhanced_queries.extend(llm_queries)
                
                print(f"Enhanced with {len(llm_queries)} LLM-generated queries for batch {i//batch_size + 1}")
                
            except Exception as e:
                print(f"Error generating enhanced queries for batch {i//batch_size + 1}: {e}")
                continue
        
        return enhanced_queries
    
    def add_local_tournament_queries(self, queries: List[Dict]) -> List[Dict]:
        """Add queries specifically for local tournaments (bonus points)."""
        
        local_templates = [
            "{sport} local tournament {level} India 2025",
            "{level} {sport} district tournament India 2025",
            "Community {sport} tournament {level} 2025",
            "Local {sport} championship {level} India cities",
            "{sport} club tournament {level} India 2025",
            "Residential {sport} tournament {level} 2025",
            "City level {sport} tournament {level} India",
            "Municipal {sport} championship {level} 2025"
        ]
        
        local_queries = []
        for sport in self.sports:
            for level in ["Club", "Academy", "District", "Corporate"]:  # Focus on local levels
                for template in local_templates:
                    query = template.format(sport=sport, level=level)
                    local_queries.append({
                        "sport": sport,
                        "level": level,
                        "query": query,
                        "template": template,
                        "type": "local_tournament"
                    })
        
        return queries + local_queries
    
    def remove_duplicates(self, queries: List[Dict]) -> List[Dict]:
        """Remove duplicate queries based on query text."""
        seen_queries = set()
        unique_queries = []
        
        for query in queries:
            query_text = query['query'].lower()
            if query_text not in seen_queries:
                seen_queries.add(query_text)
                unique_queries.append(query)
        
        removed_count = len(queries) - len(unique_queries)
        if removed_count > 0:
            print(f"Removed {removed_count} duplicate queries")
        
        return unique_queries
    
    def save_queries(self, queries: List[Dict], filename: str = "search_queries_complete.json"):
        """Save generated queries to a JSON file with metadata."""
        
        # Add metadata
        query_data = {
            "metadata": {
                "total_queries": len(queries),
                "sports_covered": len(self.sports),
                "levels_covered": len(self.levels),
                "sports_list": self.sports,
                "levels_list": self.levels,
                "generated_at": "2025-08-02T00:00:00Z",
                "generator_version": "1.0"
            },
            "queries": queries
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(query_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(queries)} queries to {filename}")
        return filename
    
    def generate_query_statistics(self, queries: List[Dict]) -> Dict:
        """Generate statistics about the queries."""
        stats = {
            "total_queries": len(queries),
            "by_sport": {},
            "by_level": {},
            "by_type": {}
        }
        
        for query in queries:
            sport = query.get('sport', 'Unknown')
            level = query.get('level', 'Unknown')
            query_type = query.get('type', 'standard')
            
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            stats["by_type"][query_type] = stats["by_type"].get(query_type, 0) + 1
        
        return stats
    
    def generate_all_queries(self, use_llm_enhancement: bool = True) -> List[Dict]:
        """Generate complete set of search queries."""
        print("=" * 60)
        print("🚀 Generating Complete Query Set for Tournament Calendar")
        print("=" * 60)
        
        # Step 1: Generate base queries
        print("📋 Step 1: Generating base queries...")
        base_queries = self.generate_base_queries()
        print(f"✅ Generated {len(base_queries)} base queries")
        
        # Step 2: Enhance with LLM (optional)
        if use_llm_enhancement and os.getenv('OPENAI_API_KEY'):
            print("\n🤖 Step 2: Enhancing queries with LLM...")
            all_queries = self.enhance_queries_with_llm(base_queries)
            print(f"✅ Total queries after LLM enhancement: {len(all_queries)}")
        else:
            all_queries = base_queries
            print("\n⏭️  Skipping LLM enhancement")
        
        # Step 3: Add local tournament queries
        print("\n🏘️  Step 3: Adding local tournament queries...")
        all_queries = self.add_local_tournament_queries(all_queries)
        print(f"✅ Total queries after local tournaments: {len(all_queries)}")
        
        # Step 4: Remove duplicates
        print("\n🧹 Step 4: Removing duplicates...")
        all_queries = self.remove_duplicates(all_queries)
        print(f"✅ Final unique queries: {len(all_queries)}")
        
        # Step 5: Generate statistics
        print("\n📊 Step 5: Generating statistics...")
        stats = self.generate_query_statistics(all_queries)
        
        print(f"\n📈 Query Statistics:")
        print(f"   Total Queries: {stats['total_queries']}")
        print(f"   Sports Covered: {len(stats['by_sport'])}")
        print(f"   Levels Covered: {len(stats['by_level'])}")
        
        # Step 6: Save queries
        print("\n💾 Step 6: Saving queries...")
        filename = self.save_queries(all_queries)
        
        print("\n" + "=" * 60)
        print("✅ Query Generation Complete!")
        print(f"📁 Saved to: {filename}")
        print(f"🎯 Ready for Step 2: Search Results Collection")
        
        return all_queries

def main():
    """Main function to generate all search queries."""
    generator = QueryGenerator()
    
    # Generate complete query set
    queries = generator.generate_all_queries(use_llm_enhancement=True)
    
    # Display sample queries from different categories
    print("\n📋 Sample Queries by Category:")
    
    sports_shown = set()
    for query in queries[:20]:  # Show first 20 as examples
        sport = query['sport']
        if sport not in sports_shown and len(sports_shown) < 5:
            print(f"\n🏆 {sport} - {query['level']}:")
            print(f"   Query: {query['query']}")
            sports_shown.add(sport)

if __name__ == "__main__":
    main()
