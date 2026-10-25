# File: sports/models.py
from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    SPORT_CHOICES = [
        ('cricket', 'Cricket'),
        ('football', 'Football'),
        ('volleyball', 'Volleyball'),
    ]
    
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, blank=True) # Add nickname field
    country = models.CharField(max_length=50)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    jersey_image = models.ImageField(upload_to='team_jerseys/', null=True, blank=True) # Add jersey image field
    
    def __str__(self):
        return f"{self.name} ({self.sport})"

class Tournament(models.Model):
    SPORT_CHOICES = [
        ('cricket', 'Cricket'),
        ('football', 'Football'),
        ('volleyball', 'Volleyball'),
    ]
    
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES)
    logo = models.ImageField(upload_to='tournament_logos/', null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.sport})"

    # Add this method to get matches for this tournament
    def get_matches(self):
        """Returns matches related to this tournament, ordered by date."""
        # You might want to filter by status or order differently
        return self.match_set.all().order_by('date') # Assuming 'date' field exists in Match

    # Optional: Add a method to get upcoming matches
    def get_upcoming_matches(self):
        from django.utils import timezone
        return self.match_set.filter(date__gt=timezone.now()).order_by('date')

    # Optional: Add a method to get past matches
    def get_past_matches(self):
        from django.utils import timezone
        return self.match_set.filter(date__lte=timezone.now()).order_by('-date')


class Match(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('halftime', 'Halftime'),
    ]

    # --- Core Match Fields ---
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True)
    sport = models.CharField(max_length=20, choices=Team.SPORT_CHOICES) # Use choices from Team model
    team1 = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField() # Or models.DateField() if you only need the date
    location = models.CharField(max_length=100, blank=True)
    team1_score = models.CharField(max_length=20, blank=True, null=True)
    team2_score = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    # --- End of Core Match Fields ---

    # --- Generic fields for additional info ---
    live_status_message = models.CharField(max_length=200, blank=True, null=True)

    # --- Cricket Specific Fields ---
    cricket_overs_played = models.CharField(max_length=10, blank=True, null=True) # e.g., "15.3"

    # --- Dynamic Cricket State Tracking ---
    # Field to indicate which team is currently batting
    cricket_batting_team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='batting_matches')

    # Current Batters (from the batting team)
    cricket_batter_on_strike = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='on_strike_batter_matches')
    cricket_batter_on_non_strike = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='non_strike_batter_matches')

    # Current Bowler (from the bowling team - the team that is NOT batting)
    cricket_current_bowler = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bowler_matches')
    # Optional: Fielder on the crease or other positional info if needed later
    # cricket_keeper = models.ForeignKey('Player', ...)

    # --- Football Specific Fields ---
    football_current_time = models.CharField(max_length=20, blank=True, null=True) # e.g., "45+2'"

    def get_bowling_team(self):
        """Determine the bowling team based on the batting team."""
        if self.cricket_batting_team:
            if self.cricket_batting_team == self.team1:
                return self.team2
            elif self.cricket_batting_team == self.team2:
                return self.team1
        return None

    def __str__(self):
        tournament_name = f" - {self.tournament.name}" if self.tournament else ""
        return f"{self.team1} vs {self.team2}{tournament_name} - {self.sport}"


# Ensure Player and other models are defined correctly
class Player(models.Model):
    name = models.CharField(max_length=100)
    # Consider making team nullable if a player can exist without a current team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', null=True, blank=True)
    role = models.CharField(max_length=50, blank=True) # E.g., Batsman, Bowler, Wicket-Keeper, All-rounder
    jersey_number = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to='player_photos/', null=True, blank=True)
    
    # --- Career Stats Fields (Overall and by Format) ---
    # You can choose to store overall stats or calculate them from PlayerMatchRecord
    # Storing them directly can be faster for display but requires updates after each match.
    
    # Overall Career Stats
    total_matches = models.IntegerField(default=0)
    total_runs = models.IntegerField(default=0)
    total_wickets = models.IntegerField(default=0)
    # Add more overall stats as needed
    
    # --- Cricket Specific Career Stats by Format ---
    # Example for Batting (similar structures for Bowling and per-format)
    # ODI Batting
    odi_matches = models.IntegerField(default=0)
    odi_runs = models.IntegerField(default=0)
    odi_balls_faced = models.IntegerField(default=0, null=True, blank=True)
    odi_fours = models.IntegerField(default=0)
    odi_sixes = models.IntegerField(default=0)
    odi_not_outs = models.IntegerField(default=0)
    odi_highest_score = models.IntegerField(default=0)
    # Add ODI Bowling stats...
    
    # T20I Batting
    t20i_matches = models.IntegerField(default=0)
    t20i_runs = models.IntegerField(default=0)
    t20i_balls_faced = models.IntegerField(default=0, null=True, blank=True)
    t20i_fours = models.IntegerField(default=0)
    t20i_sixes = models.IntegerField(default=0)
    t20i_not_outs = models.IntegerField(default=0)
    t20i_highest_score = models.IntegerField(default=0)
    # Add T20I Bowling stats...
    
    # Test Batting
    test_matches = models.IntegerField(default=0)
    test_runs = models.IntegerField(default=0)
    test_balls_faced = models.IntegerField(default=0, null=True, blank=True)
    test_fours = models.IntegerField(default=0)
    test_sixes = models.IntegerField(default=0)
    test_not_outs = models.IntegerField(default=0)
    test_highest_score = models.IntegerField(default=0)
    # Add Test Bowling stats...
    
    # Add fields for other formats (T20, List-A) as needed
    # T20 Batting
    t20_matches = models.IntegerField(default=0)
    t20_runs = models.IntegerField(default=0)
    # ... etc.
    
    # List-A Batting
    list_a_matches = models.IntegerField(default=0)
    list_a_runs = models.IntegerField(default=0)
    # ... etc.
    
    # --- Football Specific Career Stats (Example) ---
    # Overall
    total_goals = models.IntegerField(default=0)
    total_assists = models.IntegerField(default=0)
    total_yellow_cards = models.IntegerField(default=0)
    total_red_cards = models.IntegerField(default=0)
    # Add per-format or per-league stats if needed
    
    def __str__(self):
        return self.name

    # --- Optional: Methods to calculate stats ---
    # These can be used if you prefer to calculate stats dynamically from PlayerMatchRecord
    # instead of storing them directly. This is often more accurate but slower.
    # Requires PlayerMatchRecord to have a 'format' field or derive format from Match/Tournament.
    #
    # def calculate_total_runs(self):
    #     return self.events.filter(event_type='runs').aggregate(total=models.Sum('runs_value'))['total'] or 0
    #
    # def calculate_career_stats_by_format(self, format_name):
    #     # This would involve filtering PlayerMatchRecords by format and aggregating stats
    #     # Example (conceptual):
    #     # records = self.playermatchrecord_set.filter(match__tournament__format=format_name) # Needs 'format' on Tournament/Match
    #     # runs = records.aggregate(total=models.Sum('runs_scored'))['total'] or 0
    #     # wickets = records.aggregate(total=models.Sum('wickets_taken'))['total'] or 0
    #     # ... calculate other stats ...
    #     # return {'runs': runs, 'wickets': wickets, ...}
    #     pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_teams = models.ManyToManyField(Team, blank=True)
    favorite_sports = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.user.username

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    
    def __str__(self):
        return self.title

# --- Optional: Match Event Model for detailed events (goals, wickets, etc.) ---
# This is a more scalable way to track events within a match.
class MatchEvent(models.Model):
    EVENT_TYPES = [
        ('goal', 'Goal'),
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('wicket', 'Wicket'),
        ('six', 'Six'),
        ('four', 'Four'),
        # Add more event types as needed
    ]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='events', null=True, blank=True) # Null for events not tied to a specific player
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='events') # Team associated with the event
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    minute = models.IntegerField(null=True, blank=True) # Time of event
    description = models.CharField(max_length=200, blank=True) # Optional extra details
    # For cricket wickets: could store how_out, fielder, bowler
    # For goals: could store assist_player

    def __str__(self):
        return f"{self.event_type} in {self.match} by {self.player or 'N/A'} ({self.team}) at {self.minute}'"

# --- Optional: Match Squad/Player Match Record Model ---
# This links players to specific matches and can store performance data.
class PlayerMatchRecord(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE) # Redundant but useful for direct access
    # Performance stats (generic fields, might be sport-specific)
    runs_scored = models.IntegerField(default=0, null=True, blank=True) # Cricket
    wickets_taken = models.IntegerField(default=0, null=True, blank=True) # Cricket
    balls_faced = models.IntegerField(default=0, null=True, blank=True) # Cricket
    overs_bowled = models.CharField(max_length=10, blank=True, null=True) # Cricket e.g., "10.0"
    goals = models.IntegerField(default=0, null=True, blank=True) # Football
    assists = models.IntegerField(default=0, null=True, blank=True) # Football
    yellow_cards = models.IntegerField(default=0, null=True, blank=True)
    red_cards = models.IntegerField(default=0, null=True, blank=True)
    # ... add more fields as needed for different sports/stats

    def __str__(self):
        return f"{self.player.name} in {self.match}"

class Standings(models.Model):
    """
    Model to store custom or calculated standings for a tournament.
    Can be used for manual override or displaying specific formats (e.g., Group Stages).
    """
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='standings_entries')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    # Position in the standings (1st, 2nd, etc.)
    position = models.PositiveIntegerField()
    
    # --- Generic Stats (can be used for various sports) ---
    matches_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0) # Or ties/no result
    points = models.PositiveIntegerField(default=0)
    
    # --- Cricket Specific Stats ---
    # We'll add NRR here. It's only meaningful for cricket, but the field exists for all.
    # Storing it allows for easy display and sorting.
    net_run_rate = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000, help_text="Net Run Rate (for Cricket)")
    # Optional: Add other cricket stats if needed directly in standings
    # runs_scored = models.PositiveIntegerField(default=0)
    # runs_conceded = models.PositiveIntegerField(default=0)
    # balls_faced = models.PositiveIntegerField(default=0) # Or overs
    # balls_bowled = models.PositiveIntegerField(default=0) # Or overs
    
    # --- Optional: Group Stage Support ---
    # group = models.CharField(max_length=50, blank=True, help_text="Group name (e.g., 'Group A') if applicable")
    
    # --- Metadata ---
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # is_manual = models.BooleanField(default=False, help_text="Checked if this entry was manually entered/overridden")
    
    class Meta:
        ordering = ['tournament', 'position'] # Default order by position within a tournament
        unique_together = ('tournament', 'team') # A team can only have one entry per tournament
        # unique_together = ('tournament', 'position') # Or enforce unique positions if strictly manual
        verbose_name_plural = "Standings"

    def __str__(self):
        return f"{self.tournament.name} - {self.team.name} (Pos: {self.position})"