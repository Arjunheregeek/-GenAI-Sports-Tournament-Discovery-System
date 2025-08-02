"""
Query Generator Module

Generates comprehensive search queries for tournament data collection.
Supports template-based and LLM-enhanced query generation.
"""

import json
from typing import List, Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
from .config import SPORTS_LIST, LEVELS_LIST, APIConfig

# Load environment variables
load_dotenv()

class QueryGenerator:
    """Generates search queries for tournament data collection."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.client = OpenAI(api_key=self.api_config.openai_api_key)
        self.sports = SPORTS_LIST
        self.levels = LEVELS_LIST
        
        # Official Sports Governing Bodies for targeted queries
        self.governing_bodies = {
            "Cricket": {"international": "ICC", "national": "BCCI", "website": "bcci.tv"},
            "Football": {"international": "FIFA", "national": "AIFF", "website": "the-aiff.com"},
            "Badminton": {"international": "BWF", "national": "BAI", "website": "badmintonindia.org"},
            "Running": {"international": "World Athletics", "national": "AFI", "website": "athleticsfederationofindia.in"},
            "Cycling": {"international": "UCI", "national": "CFI", "website": "cyclingfederationofindia.com"},
            "Swimming": {"international": "World Aquatics", "national": "SFI", "website": "swimmingfederationofindia.com"},
            "Basketball": {"international": "FIBA", "national": "BFI", "website": "basketballfederationofindia.org"},
            "Chess": {"international": "FIDE", "national": "AICF", "website": "aicf.in"},
            "Table Tennis": {"international": "ITTF", "national": "TTFI", "website": "tabletennis.org.in"},
            "Kabaddi": {"international": "IKF", "national": "KFI", "website": "prokabaddi.com"},
            "Yoga": {"international": "International Yoga Federation", "national": "Ministry of AYUSH", "website": "ayush.gov.in"},
            "Gym": {"international": "IWF", "national": "Indian Weightlifting Federation", "website": "indianweightlifting.com"}
        }
        
        # Sport-specific major events (for LLM context)
        self.major_events_by_sport = {
            "Cricket": ["World Cup", "Women's World Cup", "T20 World Cup", "Asia Cup", "Champions Trophy"],
            "Football": ["World Cup", "Women's World Cup", "Asian Cup", "Copa America", "Euros"],
            "Badminton": ["World Championships", "Thomas Cup", "Uber Cup", "Asian Championships"],
            "Basketball": ["World Cup", "Women's World Cup", "Asia Cup", "Olympic Qualifiers"],
            # Add more sports as needed
        }
        
        # Highly efficient query templates - exactly 4 queries (2 men + 2 women)
        # These target comprehensive tournament calendars and schedules
        self.official_query_templates = [
            # Men's international events - comprehensive calendar searches
            '"{international_body}" men {sport} international tournament calendar 2025 schedule fixtures upcoming',
            '"{international_body}" men {sport} events 2025 world championship asia cup series schedule',
            
            # Women's international events - comprehensive calendar searches  
            '"{international_body}" women {sport} international tournament calendar 2025 schedule fixtures upcoming',
            '"{international_body}" women {sport} events 2025 world championship asia cup series schedule'
        ]
    
    def generate_official_body_queries(self) -> List[Dict]:
        """Generate targeted queries using official governing bodies for maximum authority."""
        queries = []
        
        print(f"Generating official body queries for {len(self.sports)} sports using governing body data...")
        
        for sport in self.sports:
            if sport not in self.governing_bodies:
                print(f"⚠️  No governing body data for {sport}, skipping...")
                continue
                
            body_info = self.governing_bodies[sport]
            
            # Generate queries using official body templates
            for template in self.official_query_templates:
                try:
                    query = template.format(
                        sport=sport,
                        international_body=body_info["international"],
                        national_body=body_info["national"],
                        website=body_info["website"]
                    )
                    
                    queries.append({
                        "sport": sport,
                        "query": query,
                        "template": template,
                        "type": "official_body",
                        "governing_body": body_info["national"],
                        "international_body": body_info["international"],
                        "official_website": body_info["website"]
                    })
                except KeyError as e:
                    print(f"⚠️  Template formatting error for {sport}: {e}")
                    continue
        
        print(f"✅ Generated {len(queries)} official body queries ({len(self.official_query_templates)} per sport)")
        return queries
    
    def generate_supplementary_llm_queries(self, base_queries: List[Dict]) -> List[Dict]:
        """Generate additional sophisticated queries using LLM with governing body context."""
        
        enhanced_queries = base_queries.copy()
        
        for sport in self.sports:
            if sport not in self.governing_bodies:
                continue
                
            body_info = self.governing_bodies[sport]
            
            prompt = f"""
            Generate 5 highly targeted search queries for finding official {sport} tournament information in India for 2025.
            
            Context:
            - Sport: {sport}
            - National Governing Body: {body_info["national"]}
            - International Body: {body_info["international"]}
            - Official Website: {body_info["website"]}
            
            PRIORITY EVENTS TO TARGET (especially for Cricket):
            - Cricket World Cup 2025 (Men's)
            - Women's Cricket World Cup 2025
            - Asia Cup Cricket 2025
            - Champions Trophy 2025
            - T20 World Cup 2025
            
            Requirements:
            - Focus on OFFICIAL tournament announcements, schedules, and registration
            - PRIORITIZE {body_info["international"]} (international body) over national bodies
            - Include BOTH men's and women's tournaments/competitions
            - Target the specific upcoming major events listed above
            - Use governing body names/acronyms for authority targeting
            - Include site-specific searches when beneficial
            - Target registration deadlines, venue information, and live streaming
            - Make queries actionable for finding tournament participation info
            - Include World Cup, championship, and league-specific searches
            
            Return ONLY a JSON array of query strings:
            ["query1", "query2", "query3", "query4", "query5"]
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.6,
                    max_tokens=800
                )
                
                # Parse the LLM response
                llm_response = response.choices[0].message.content.strip()
                if llm_response.startswith('```json'):
                    llm_response = llm_response.replace('```json', '').replace('```', '').strip()
                
                llm_queries = json.loads(llm_response)
                
                # Add the LLM queries for this sport
                for query_text in llm_queries:
                    enhanced_queries.append({
                        "sport": sport,
                        "query": query_text,
                        "template": "llm_generated_with_governing_body",
                        "type": "llm_official",
                        "source": "openai_gpt35",
                        "governing_body": body_info["national"]
                    })
                
                print(f"✅ Generated {len(llm_queries)} official LLM queries for {sport}")
                
            except Exception as e:
                print(f"❌ Error generating official LLM queries for {sport}: {e}")
                continue
        
        return enhanced_queries
    
    def add_local_tournament_queries(self, queries: List[Dict]) -> List[Dict]:
        """Add queries for local tournaments using governing body context with gender-specific searches."""
        
        local_templates = [
            '"{national_body}" district {sport} tournaments India 2025',
            '"{national_body}" state championship {sport} 2025 registration',
            'local {sport} clubs India "{national_body}" affiliation 2025',
            'corporate {sport} tournaments India "{national_body}" sanctioned 2025',
            'academy {sport} competitions India "{national_body}" recognized 2025',
            'municipal {sport} leagues India "{national_body}" approved 2025',
            '"{national_body}" men {sport} district championships India 2025',
            '"{national_body}" women {sport} district championships India 2025',
            'local men {sport} tournaments India "{national_body}" 2025',
            'local women {sport} tournaments India "{national_body}" 2025',
            'corporate men {sport} leagues India "{national_body}" 2025',
            'corporate women {sport} leagues India "{national_body}" 2025'
        ]
        
        local_queries = []
        for sport in self.sports:
            if sport not in self.governing_bodies:
                continue
                
            body_info = self.governing_bodies[sport]
            
            for template in local_templates:
                try:
                    query = template.format(
                        sport=sport,
                        national_body=body_info["national"]
                    )
                    local_queries.append({
                        "sport": sport,
                        "query": query,
                        "template": template,
                        "type": "local_official",
                        "governing_body": body_info["national"]
                    })
                except KeyError:
                    continue
        
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
    
    def save_queries(self, queries: List[Dict], filename: str = "search_queries_complete.json") -> str:
        """Save generated queries to a JSON file with metadata."""
        
        # Add metadata
        query_data = {
            "metadata": {
                "total_queries": len(queries),
                "sports_covered": len(self.sports),
                "sports_list": self.sports,
                "generated_at": "2025-08-02T00:00:00Z",
                "generator_version": "2.0",
                "query_approach": "official_governing_body_targeted"
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
            "by_type": {}
        }
        
        for query in queries:
            sport = query.get('sport', 'Unknown')
            query_type = query.get('type', 'standard')
            
            stats["by_sport"][sport] = stats["by_sport"].get(sport, 0) + 1
            stats["by_type"][query_type] = stats["by_type"].get(query_type, 0) + 1
        
        return stats
    
    def generate_all_queries(self, use_llm_enhancement: bool = True) -> List[Dict]:
        """Generate complete set of official body targeted queries."""
        print("=" * 60)
        print("🚀 Generating Official Body Query Set for Tournament Calendar")
        print("=" * 60)
        
        # Step 1: Generate official body queries using governing bodies
        print("📋 Step 1: Generating official body queries...")
        base_queries = self.generate_official_body_queries()
        print(f"✅ Generated {len(base_queries)} official body queries")
        
        # Step 2: Skip LLM enhancement - using only hand-crafted efficient queries
        all_queries = base_queries
        print("\n⏭️  Using only hand-crafted efficient queries (no LLM enhancement needed)")
        
        # Step 3: Skip local tournament queries - focus on international tournaments only
        print(f"\n🎯 Using focused international queries only: {len(all_queries)} queries")
        
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
        print(f"   Query Types: {', '.join(stats['by_type'].keys())}")
        
        # Step 6: Save queries
        print("\n💾 Step 6: Saving queries...")
        filename = self.save_queries(all_queries)
        
        print("\n" + "=" * 60)
        print("✅ Official Body Query Generation Complete!")
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
            print(f"\n🏆 {sport} - {query.get('type', 'N/A')}:")
            print(f"   Query: {query['query']}")
            sports_shown.add(sport)

if __name__ == "__main__":
    main()
