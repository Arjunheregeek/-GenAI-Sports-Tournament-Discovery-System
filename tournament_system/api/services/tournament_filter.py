#!/usr/bin/env python3
"""
Tournament Filter Service

Handles filtering and validation of tournament data.
"""

from typing import List, Dict, Any
from datetime import datetime, date, timedelta


class TournamentFilterService:
    """Service for filtering and validating tournament data."""
    
    @staticmethod
    def filter_recent_and_future_tournaments(tournaments: List[Dict]) -> List[Dict]:
        """
        Filter tournaments to include those held in the past six months and future tournaments.
        
        Args:
            tournaments: List of tournament dictionaries
            
        Returns:
            Filtered list of relevant tournaments
        """
        current_date = date.today()
        six_months_ago = current_date - timedelta(days=6 * 30)
        relevant_tournaments = []

        for tournament in tournaments:
            start_date_str = tournament.get('start_date', '')

            # Include tournaments with unknown/TBD dates
            if not start_date_str or start_date_str in ['N/A', 'TBD', 'To be announced']:
                relevant_tournaments.append(tournament)
                continue

            try:
                tournament_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                if six_months_ago <= tournament_start_date:
                    relevant_tournaments.append(tournament)
            except ValueError:
                # Include tournaments with invalid date formats
                relevant_tournaments.append(tournament)

        return relevant_tournaments
    
    @staticmethod
    def filter_by_level(tournaments: List[Dict], level: str) -> List[Dict]:
        """
        Filter tournaments by competition level.
        
        Args:
            tournaments: List of tournament dictionaries
            level: Competition level to filter by
            
        Returns:
            Filtered list of tournaments matching the level
        """
        if level.lower() == 'international':
            # For now, return all tournaments as we don't have level classification
            return tournaments
        
        # Future implementation can add more sophisticated level filtering
        return tournaments
    
    @staticmethod
    def validate_tournament_data(tournament: Dict) -> bool:
        """
        Validate if tournament data is complete and valid.
        
        Args:
            tournament: Tournament dictionary to validate
            
        Returns:
            True if tournament data is valid, False otherwise
        """
        required_fields = ['tournament_name']
        
        # Check if required fields are present and not empty
        for field in required_fields:
            if not tournament.get(field) or tournament[field].strip() == '':
                return False
        
        return True
    
    @staticmethod
    def sort_tournaments_by_date(tournaments: List[Dict], ascending: bool = True) -> List[Dict]:
        """
        Sort tournaments by start date.
        
        Args:
            tournaments: List of tournament dictionaries
            ascending: Sort in ascending order (earliest first) if True
            
        Returns:
            Sorted list of tournaments
        """
        def get_sort_key(tournament):
            start_date_str = tournament.get('start_date', '')
            
            # Handle special cases
            if not start_date_str or start_date_str in ['N/A', 'TBD', 'To be announced']:
                # Put unknown dates at the end
                return datetime.max.date() if ascending else datetime.min.date()
            
            try:
                return datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                # Put invalid dates at the end
                return datetime.max.date() if ascending else datetime.min.date()
        
        return sorted(tournaments, key=get_sort_key, reverse=not ascending)
