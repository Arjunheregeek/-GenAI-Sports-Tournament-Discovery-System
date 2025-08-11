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
            "Tennis": {"international": "ITF", "national": "AITA", "website": "aitatennis.com"},
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
        
        # Sport-specific major events (for LLM context and targeted queries)
        self.major_events_by_sport = {
            "Cricket": [
                "World Cup", "Women's World Cup", "T20 World Cup", "Women's T20 World Cup",
                "Asia Cup", "Champions Trophy", "World Test Championship", "IPL", 
                "Women's Premier League", "Under-19 World Cup", "Commonwealth Games"
            ],
            "Football": [
                "World Cup", "Women's World Cup", "Asian Cup", "AFC Women's Asian Cup",
                "Copa America", "UEFA European Championship", "Nations League", 
                "Club World Cup", "Champions League", "Olympic Games", "Youth World Cup"
            ],
            "Badminton": [
                "World Championships", "Thomas Cup", "Uber Cup", "Asian Championships",
                "All England Open", "World Tour Finals", "Sudirman Cup", 
                "Asian Games", "Commonwealth Games", "Olympic Games", "Youth Olympics"
            ],
            "Basketball": [
                "World Cup", "Women's World Cup", "Asia Cup", "Women's Asia Cup",
                "Olympic Games", "World University Games", "Youth World Cup",
                "3x3 World Cup", "Champions League", "Asian Games", "Commonwealth Games"
            ],
            "Running": [
                "World Championships", "Olympic Games", "World Indoor Championships",
                "World Cross Country Championships", "Diamond League", "Asian Games",
                "Commonwealth Games", "World Half Marathon Championships", "Marathon Majors"
            ],
            "Cycling": [
                "World Championships", "Olympic Games", "Tour de France", "Giro d'Italia",
                "Vuelta a España", "World Cup", "Asian Championships", "Commonwealth Games",
                "Track World Championships", "BMX World Championships", "Mountain Bike World Cup"
            ],
            "Swimming": [
                "World Championships", "Olympic Games", "World Short Course Championships",
                "Asian Games", "Commonwealth Games", "World Junior Championships",
                "Swimming World Cup", "Diamond League", "Pan Pacific Championships"
            ],
            "Chess": [
                "World Championship", "Women's World Championship", "World Cup",
                "Candidates Tournament", "Chess Olympiad", "World Team Championship",
                "Grand Prix", "Asian Continental Championship", "Youth World Championships"
            ],
            "Table Tennis": [
                "World Championships", "World Cup", "Asian Championships", "Asian Games",
                "Commonwealth Games", "Olympic Games", "World Team Championships",
                "ITTF World Tour", "Youth World Championships", "Para World Championships"
            ],
            "Kabaddi": [
                "World Cup", "Asian Games", "Asian Championships", "Pro Kabaddi League",
                "World Championship", "South Asian Games", "Commonwealth Games",
                "World Beach Kabaddi Championship", "Youth World Championship"
            ],
            "Yoga": [
                "World Yoga Championship", "Asian Yoga Championship", "International Yoga Day",
                "World Yoga Olympics", "National Yoga Championship", "Yoga World Cup",
                "International Yoga Competition", "Asian Yoga Games"
            ],
            "Gym": [
                "World Championships", "Olympic Games", "Asian Games", "Commonwealth Games",
                "World Cup", "Asian Championships", "Youth World Championships",
                "World University Games", "Grand Prix Series", "Continental Championships"
            ],
            "Tennis": [
                "Grand Slam", "Wimbledon", "US Open", "French Open", "Australian Open",
                "Davis Cup", "Fed Cup", "ATP Finals", "WTA Finals", "Olympic Games",
                "Asian Games", "Commonwealth Games", "Youth Olympics"
            ]
        }
        
        # Highly efficient query templates - exactly 6 queries (3 men + 3 women)
        # These target comprehensive tournament calendars and major events
        self.official_query_templates = [
            # Men's international events - comprehensive calendar searches
            '"{international_body}" men {sport} international tournament calendar 2025 schedule fixtures upcoming',
            '"{international_body}" men {sport} world cup championship 2025 asia cup series schedule',
            '"{international_body}" men {sport} major events 2025 world championship tournaments schedule',
            
            # Women's international events - comprehensive calendar searches  
            '"{international_body}" women {sport} international tournament calendar 2025 schedule fixtures upcoming',
            '"{international_body}" women {sport} world cup championship 2025 asia cup series schedule',
            '"{international_body}" women {sport} major events 2025 world championship tournaments schedule'
        ]
    
    def generate_official_body_queries(self, sport: str = None) -> List[Dict]:
        """Generate targeted queries using official governing bodies for maximum authority."""
        queries = []
        
        # If no sport specified, use all sports from config, otherwise use the provided sport
        sports_to_process = [sport] if sport else self.sports
        
        print(f"Generating official body queries for {len(sports_to_process)} sport(s) using governing body data...")
        
        for target_sport in sports_to_process:
            if target_sport not in self.governing_bodies:
                print(f"⚠️  No governing body data for {target_sport}, skipping...")
                continue
                
            body_info = self.governing_bodies[target_sport]
            
            # Generate queries using official body templates
            for template in self.official_query_templates:
                try:
                    query = template.format(
                        sport=target_sport,
                        international_body=body_info["international"],
                        national_body=body_info["national"],
                        website=body_info["website"]
                    )
                    
                    queries.append({
                        "sport": target_sport,
                        "query": query,
                        "template": template,
                        "type": "official_body",
                        "governing_body": body_info["national"],
                        "international_body": body_info["international"],
                        "official_website": body_info["website"]
                    })
                except KeyError as e:
                    print(f"⚠️  Template formatting error for {target_sport}: {e}")
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
    
    def is_sport_supported(self, sport: str) -> bool:
        """Check if a sport is supported by checking if it has governing body data."""
        return sport in self.governing_bodies
    
    def get_supported_sports(self) -> List[str]:
        """Get list of all supported sports."""
        return list(self.governing_bodies.keys())
    
    def get_sport_info(self, sport: str) -> Dict:
        """Get governing body information for a specific sport."""
        if sport not in self.governing_bodies:
            return {}
        return self.governing_bodies[sport].copy()
    
    def get_major_events(self, sport: str) -> List[str]:
        """Get major events for a specific sport."""
        return self.major_events_by_sport.get(sport, [])
    
    def generate_enhanced_sport_queries(self, sport: str, include_major_events: bool = True) -> List[Dict]:
        """Generate enhanced queries for a sport including major event-specific queries."""
        if not self.is_sport_supported(sport):
            raise ValueError(f"Sport '{sport}' is not supported. Supported sports: {', '.join(self.get_supported_sports())}")
        
        # Get base queries
        base_queries = self.generate_official_body_queries(sport)
        
        if not include_major_events:
            return base_queries
        
        # Add major event-specific queries
        major_events = self.get_major_events(sport)
        body_info = self.governing_bodies[sport]
        enhanced_queries = base_queries.copy()
        
        # Add 2-3 major event specific queries
        major_event_templates = [
            '"{international_body}" {sport} {major_event} 2025 schedule registration dates venues',
            '"{international_body}" {major_event} {sport} 2025 tournament format teams participants'
        ]
        
        # Use top 3 major events to avoid too many queries
        for major_event in major_events[:3]:
            for template in major_event_templates[:1]:  # Use only 1 template per event to limit queries
                try:
                    query = template.format(
                        sport=sport,
                        major_event=major_event,
                        international_body=body_info["international"]
                    )
                    enhanced_queries.append({
                        "sport": sport,
                        "query": query,
                        "template": template,
                        "type": "major_event_specific",
                        "major_event": major_event,
                        "international_body": body_info["international"]
                    })
                except KeyError:
                    continue
        
        return enhanced_queries
    
    def generate_sport_specific_queries(self, sport: str) -> List[Dict]:
        """Generate standard queries for one sport (main API method)."""
        if not self.is_sport_supported(sport):
            raise ValueError(f"Sport '{sport}' is not supported. Supported sports: {', '.join(self.get_supported_sports())}")
        
        return self.generate_all_queries(sport=sport, use_llm_enhancement=False)
    
    def generate_all_queries(self, sport: str = None, use_llm_enhancement: bool = False) -> List[Dict]:
        """Generate complete set of official body targeted queries for a specific sport or all sports."""
        print("=" * 60)
        print("🚀 Generating Official Body Query Set for Tournament Calendar")
        print("=" * 60)
        
        sport_info = f" for {sport}" if sport else ""
        print(f"🎯 Target: International tournaments{sport_info}")
        
        # Step 1: Generate official body queries using governing bodies
        print("📋 Step 1: Generating official body queries...")
        base_queries = self.generate_official_body_queries(sport)
        print(f"✅ Generated {len(base_queries)} official body queries")
        
        # Step 2: Skip LLM enhancement by default for efficiency
        all_queries = base_queries
        if not use_llm_enhancement:
            print("\n⏭️  Using only hand-crafted efficient queries (no LLM enhancement)")
        
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
