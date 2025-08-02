"""
Step 1: Generate Search Queries for Tournament Calendar
This script generates search queries for different sports and levels.
"""

import json
from typing import List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QueryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Define sports and levels
        self.sports = [
            "Cricket", "Football", "Badminton", "Basketball", "Tennis", 
            "Volleyball", "Kabaddi", "Hockey", "Table Tennis", "Chess"
        ]
        
        self.levels = [
            "School", "College", "University", "Corporate", "Inter-college",
            "State", "National", "District", "Regional", "Amateur"
        ]
    
    def generate_base_queries(self) -> List[Dict]:
        """Generate basic search queries for each sport-level combination."""
        queries = []
        
        for sport in self.sports:
            for level in self.levels:
                # Generate multiple query variations
                base_queries = [
                    f"Upcoming {sport} tournaments 2025 India {level} level",
                    f"{sport} championship {level} 2025 India registration dates",
                    f"{level} {sport} competition India 2025 schedule",
                    f"India {sport} tournament {level} 2025 official website",
                    f"{sport} inter {level} tournament 2025 India dates"
                ]
                
                for query in base_queries:
                    queries.append({
                        "sport": sport,
                        "level": level,
                        "query": query
                    })
        
        return queries
    
    def enhance_queries_with_llm(self, base_queries: List[Dict]) -> List[Dict]:
        """Use LLM to generate more sophisticated and diverse queries."""
        
        prompt = f"""
        Generate 5 additional search queries for finding tournament information for each sport-level combination.
        Focus on finding official tournament websites, registration pages, and schedule information.
        
        Make queries specific to India and include year 2025.
        Vary the language and terms used (tournament, championship, competition, league, cup, etc.).
        
        Sports: {', '.join(self.sports)}
        Levels: {', '.join(self.levels)}
        
        Return only the additional queries in this exact JSON format:
        [
            {{"sport": "Cricket", "level": "School", "query": "example query"}},
            ...
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            # Parse the LLM response
            llm_queries = json.loads(response.choices[0].message.content)
            return base_queries + llm_queries
            
        except Exception as e:
            print(f"Error generating enhanced queries: {e}")
            return base_queries
    
    def save_queries(self, queries: List[Dict], filename: str = "search_queries.json"):
        """Save generated queries to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(queries, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(queries)} queries to {filename}")
    
    def generate_all_queries(self) -> List[Dict]:
        """Generate all search queries and return them."""
        print("Generating base queries...")
        base_queries = self.generate_base_queries()
        print(f"Generated {len(base_queries)} base queries")
        
        print("Enhancing queries with LLM...")
        all_queries = self.enhance_queries_with_llm(base_queries)
        print(f"Total queries generated: {len(all_queries)}")
        
        # Save queries
        self.save_queries(all_queries)
        
        return all_queries

def main():
    """Main function to generate search queries."""
    generator = QueryGenerator()
    queries = generator.generate_all_queries()
    
    # Display sample queries
    print("\nSample generated queries:")
    for i, query in enumerate(queries[:10]):
        print(f"{i+1}. Sport: {query['sport']}, Level: {query['level']}")
        print(f"   Query: {query['query']}\n")

if __name__ == "__main__":
    main()
