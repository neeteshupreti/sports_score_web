from django import forms
from .models import Match, Team, Tournament, Player
from django.db import models

class MatchForm(forms.ModelForm):
    """
    Custom ModelForm for the Match model in the Django Admin.
    Provides dynamic filtering for teams, tournaments, and players.
    """
    class Meta:
        model = Match
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # --- Filter Teams and Tournaments based on Sport (existing logic) ---
        self.fields['team1'].queryset = Team.objects.all()
        self.fields['team2'].queryset = Team.objects.all()
        self.fields['team1'].label_from_instance = lambda obj: f"{obj.name} ({obj.sport})"
        self.fields['team2'].label_from_instance = lambda obj: f"{obj.name} ({obj.sport})"
        self.fields['tournament'].queryset = Tournament.objects.all()
        self.fields['tournament'].label_from_instance = lambda obj: f"{obj.name} ({obj.sport})"

        # --- Filter Cricket Batting Team ---
        # Initially, only team1 and team2 are valid options for batting team
        if self.instance and self.instance.pk:
            # If editing, filter batting team to match teams
            self.fields['cricket_batting_team'].queryset = Team.objects.filter(
                models.Q(id=self.instance.team1.id) | models.Q(id=self.instance.team2.id)
            )
        else:
            # If creating, start with no options or all teams (JS will update)
            self.fields['cricket_batting_team'].queryset = Team.objects.none() # Or .all()

        # --- Filter Player fields based on Batting Team (initial server-side filter) ---
        # Get the initial value of cricket_batting_team if it exists
        initial_batting_team = self.instance.cricket_batting_team if self.instance and self.instance.pk else None
        # Fallback to team1 or team2 if batting_team not set but instance exists
        if not initial_batting_team and self.instance and self.instance.pk:
             # Default to team1, or could be based on score logic if needed
             initial_batting_team = self.instance.team1

        if initial_batting_team:
            # Filter batters to players of the batting team
            self.fields['cricket_batter_on_strike'].queryset = Player.objects.filter(team=initial_batting_team)
            self.fields['cricket_batter_on_non_strike'].queryset = Player.objects.filter(team=initial_batting_team)

            # Determine bowling team and filter bowler
            # This logic relies on the model method or needs to be handled carefully
            # if self.instance.pk: # Ensure instance is saved to access related teams correctly in method
            bowling_team = self.instance.get_bowling_team() if self.instance.pk else None
            if bowling_team:
                self.fields['cricket_current_bowler'].queryset = Player.objects.filter(team=bowling_team)
            else:
                # Fallback if bowling team cannot be determined
                self.fields['cricket_current_bowler'].queryset = Player.objects.filter(
                    models.Q(team=self.instance.team1) | models.Q(team=self.instance.team2)
                )
        else:
            # If no batting team is selected initially, show no players or players from both teams
            # The JavaScript should update these when cricket_batting_team changes
            self.fields['cricket_batter_on_strike'].queryset = Player.objects.none()
            self.fields['cricket_batter_on_non_strike'].queryset = Player.objects.none()
            self.fields['cricket_current_bowler'].queryset = Player.objects.none()

        # --- Optional: Add help text for clarity ---
        # self.fields['cricket_batting_team'].help_text = "Select the team currently batting."
        # self.fields['cricket_batter_on_strike'].help_text = "Select the batter currently on strike."
        # self.fields['cricket_batter_on_non_strike'].help_text = "Select the batter currently on non-strike (at the other end)."
        # self.fields['cricket_current_bowler'].help_text = "Select the player currently bowling (must be from the bowling team)."

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'team'] # Or specify fields explicitly

    def __init__(self, *args, **kwargs):
        # Extract request from kwargs if provided
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Always show all teams initially
        self.fields['team'].queryset = Team.objects.all()

        # If we have a sport value, filter teams
        sport = None
        if self.instance and self.instance.pk and self.instance.team:
            sport = self.instance.team.sport
        elif self.request and 'sport' in self.request.GET:
            sport = self.request.GET['sport']
        # Note: Player doesn't have a direct sport field, it's on the Team.
        # Filtering by team sport would happen in the view or JS if needed via team selection. 

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'country', 'sport']