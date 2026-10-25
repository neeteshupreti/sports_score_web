# File: sports/admin.py
from django.contrib import admin
from django import forms
from django.db import models  # Import models for Q objects
from .models import Team, Match, BlogPost, UserProfile, Tournament, Player, PlayerMatchRecord, Standings
from .forms import MatchForm  # Import the form we defined

# --- Inline Admin for PlayerMatchRecord ---
class PlayerMatchRecordInline(admin.TabularInline):
    """
    Inline admin for managing PlayerMatchRecord entries within a Match.
    Allows selecting players from the teams involved in the match.
    """
    model = PlayerMatchRecord
    extra = 10
    fields = ('player', 'team') # Add performance stat fields here if desired

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Dynamically filter player and team dropdowns in the inline based on the match being edited.
        """
        if db_field.name == "player":
            match_id = request.resolver_match.kwargs.get('object_id')
            if match_id:
                try:
                    match = Match.objects.get(pk=match_id)
                    kwargs["queryset"] = Player.objects.filter(
                        models.Q(team=match.team1) | models.Q(team=match.team2)
                    )
                except Match.DoesNotExist:
                    pass
        if db_field.name == "team":
            match_id = request.resolver_match.kwargs.get('object_id')
            if match_id:
                try:
                    match = Match.objects.get(pk=match_id)
                    kwargs["queryset"] = Team.objects.filter(
                        models.Q(id=match.team1.id) | models.Q(id=match.team2.id)
                    )
                except Match.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
class StandingsInline(admin.TabularInline): # Or admin.StackedInline
    """
    Inline admin for managing Standings entries within a Tournament.
    """
    model = Standings
    extra = 5  # How many empty rows to show by default
    ordering = ('position',) # Show entries ordered by position
    
    # Optional: Customize fields displayed in the inline
    # fields = ('team', 'position', 'matches_played', 'wins', 'losses', 'draws', 'points', 'net_run_rate')
    
    def get_queryset(self, request):
        """
        Optional: Filter the queryset for the inline if needed.
        E.g., pre-select related team for performance.
        """
        qs = super().get_queryset(request)
        return qs.select_related('team')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Optional: Filter the 'team' dropdown in the inline to only show teams
        that have played matches in this specific tournament.
        This requires getting the tournament ID from the request.
        """
        # This is a bit tricky in an inline, but possible.
        # One way is to get the object ID from the URL.
        if db_field.name == "team":
            # Get the tournament ID from the URL path (e.g., /admin/sports/tournament/123/change/)
            import re
            resolver_match = request.resolver_match
            if resolver_match and resolver_match.kwargs.get('object_id'):
                tournament_id = resolver_match.kwargs['object_id']
                try:
                    tournament = Tournament.objects.get(pk=tournament_id)
                    # Get teams that played in this tournament
                    teams_in_tournament = Team.objects.filter(
                        models.Q(home_matches__tournament=tournament) |
                        models.Q(away_matches__tournament=tournament)
                    ).distinct()
                    kwargs["queryset"] = teams_in_tournament
                except Tournament.DoesNotExist:
                    pass # Fallback to all teams if tournament not found (shouldn't happen)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# --- Admin Classes ---

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'country', 'sport', 'logo_preview')
    list_filter = ('country', 'sport')
    search_fields = ('name', 'nickname', 'country')
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />'
        return "No logo"
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Logo Preview'

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'logo_preview')
    list_filter = ('sport',)
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)
    
    # Add the Standings inline
    inlines = [StandingsInline] # Add this line

    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />'
        return "No logo"
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Logo Preview'

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'role', 'jersey_number')
    list_filter = ('team', 'role')
    search_fields = ('name',)

# --- Corrected MatchAdmin ---
class MatchAdmin(admin.ModelAdmin):
    form = MatchForm
    inlines = [PlayerMatchRecordInline]
    
    # --- Use the EXACT field names from your Match model ---
    list_display = ('tournament', 'sport', 'team1', 'team2', 'date', 'status', 'team1_score', 'team2_score')
    list_filter = ('tournament', 'sport', 'status', 'date')
    search_fields = ('team1__name', 'team2__name', 'location', 'tournament__name')
    list_editable = ('team1_score', 'team2_score', 'status')
    # --- End of list/display/filter corrections ---
    
    fieldsets = (
        (None, {
            # --- Use the EXACT field names from your Match model ---
            'fields': ('tournament', 'sport', 'team1', 'team2', 'date', 'location')
        }),
        ('Scores and Status', {
             # --- Use the EXACT field names from your Match model ---
            'fields': ('team1_score', 'team2_score', 'status', 'live_status_message')
        }),
        ('Cricket Details', {
            # --- Use the EXACT field names from your Match model ---
            # Ensure these field names match what you have in your updated Match model
            'fields': (
                'cricket_overs_played',
                'cricket_batting_team',
                'cricket_batter_on_strike', 'cricket_batter_on_non_strike',
                'cricket_current_bowler',
                # Remove any fields here that don't exist in your Match model
            ),
            'classes': ('collapse',)
        }),
        ('Football Details', {
            # --- Use the EXACT field name from your Match model ---
            'fields': ('football_current_time',),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        js = ('admin/js/team_filter.js',) # Removed match_admin.js as it wasn't provided

# --- Rest of Admin Classes ---
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_sports', 'get_favorite_teams_count')
    filter_horizontal = ('favorite_teams',)
    
    def get_favorite_sports(self, obj):
        return obj.favorite_sports or "None"
    get_favorite_sports.short_description = 'Favorite Sports'
    
    def get_favorite_teams_count(self, obj):
        return obj.favorite_teams.count()
    get_favorite_teams_count.short_description = 'Favorite Teams Count'

# --- Register Models ---
admin.site.register(Team, TeamAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
# PlayerMatchRecord is handled via the inline
