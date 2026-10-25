# File: sports/serializers.py
from rest_framework import serializers
from .models import Match, Team, Player, Tournament # Import relevant models

class MatchScoreSerializer(serializers.ModelSerializer):
    """
    Serializer for exposing match scores and basic live info via API.
    Read-only for public consumption, or writable for trusted internal APIs.
    """
    team1_name = serializers.CharField(source='team1.name', read_only=True)
    team2_name = serializers.CharField(source='team2.name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'team1', 'team1_name', 'team1_score',
            'team2', 'team2_name', 'team2_score',
            'tournament', 'tournament_name',
            'sport', 'status', 'live_status_message',
            'date', 'location',
            # Cricket specific
            'cricket_overs_played', 'cricket_team1_wickets', 'cricket_team2_wickets',
            # Football specific (add if you have specific live fields)
            # 'football_current_time',
        ]
        read_only_fields = ['id', 'team1_name', 'team2_name', 'tournament_name', 'sport', 'date', 'location'] # Prevent changing core match details via score API

class MatchDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed match information, potentially including player stats.
    """
    team1_name = serializers.CharField(source='team1.name', read_only=True)
    team2_name = serializers.CharField(source='team2.name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    # You could add nested serializers for player stats if needed via PlayerMatchRecord

    class Meta:
        model = Match
        fields = '__all__' # Or specify fields explicitly
        # Consider making certain fields read-only if they shouldn't be changed via API
        # read_only_fields = [...] 

# ... Add serializers for Team, Player, Tournament if needed for other API endpoints ...