from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Team, Match, BlogPost, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View    
from django.shortcuts import render, get_object_or_404
from .models import Team, Match, BlogPost, UserProfile, Tournament, Player, MatchEvent, PlayerMatchRecord, Standings
from django.db.models import Q
from django.utils import timezone


def home(request):
    # Get live matches (limit to 4 for a single row)
    live_matches = Match.objects.filter(status='live')[:4]
    
    # Get latest blog posts
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:6]
    
    context = {
        'live_matches': live_matches,
        'blog_posts': blog_posts,
    }
    return render(request, 'sports/home.html', context)

def scores(request):
    """
    View function for displaying live and completed matches, with optional sport filtering.
    """
    # --- Get filter parameter ---
    selected_sport = request.GET.get('sport', '')

    # Get all matches, ordered by status and date
    matches_query = Match.objects.all().order_by('-date') # Start with all matches

    # --- Apply Sport Filter ---
    if selected_sport:
        matches_query = matches_query.filter(sport=selected_sport)

    # Separate into live and completed based on the filtered queryset
    live_matches = matches_query.filter(status='live')
    completed_matches = matches_query.filter(status='completed').order_by('-date')
    # Optionally filter upcoming matches if needed on this page
    # upcoming_matches = matches_query.filter(status='upcoming').order_by('date')

    # Get distinct sports for the filter dropdown (using choices from Team model)
    all_sports = Team.SPORT_CHOICES

    context = {
        'live_matches': live_matches,
        'completed_matches': completed_matches,
        # 'upcoming_matches': upcoming_matches, # Uncomment if added
        'all_sports': all_sports,
        'selected_sport': selected_sport, # Pass selected sport to template
    }
    return render(request, 'sports/scores.html', context)


def schedule(request):
    """
    View function for displaying upcoming matches, with optional sport filtering.
    """
    # --- Get filter parameter ---
    selected_sport = request.GET.get('sport', '')

    # Get upcoming matches query set
    matches_query = Match.objects.filter(status='upcoming').order_by('date')

    # --- Apply Sport Filter ---
    if selected_sport:
        matches_query = matches_query.filter(sport=selected_sport)

    upcoming_matches = matches_query

    # Get distinct sports for the filter dropdown (using choices from Team model)
    all_sports = Team.SPORT_CHOICES

    context = {
        'upcoming_matches': upcoming_matches,
        'all_sports': all_sports,
        'selected_sport': selected_sport, # Pass selected sport to template
    }
    return render(request, 'sports/schedule.html', context)

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle favorite teams selection
        favorite_teams = request.POST.getlist('favorite_teams')
        user_profile.favorite_teams.clear()
        for team_id in favorite_teams:
            team = Team.objects.get(id=team_id)
            user_profile.favorite_teams.add(team)
        
        # Handle favorite sports selection
        favorite_sports = request.POST.getlist('favorite_sports')
        user_profile.favorite_sports = ','.join(favorite_sports)
        user_profile.save()
        
        messages.success(request, 'Your preferences have been updated!')
        return redirect('profile')
    
    # Get all teams, prioritizing Nepal and India teams
    nepal_teams = Team.objects.filter(country='Nepal')
    india_teams = Team.objects.filter(country='India')
    other_teams = Team.objects.exclude(country__in=['Nepal', 'India'])
    
    # Get teams by sport for the dropdown
    cricket_teams = Team.objects.filter(sport='cricket')
    football_teams = Team.objects.filter(sport='football')
    volleyball_teams = Team.objects.filter(sport='volleyball')
    
    context = {
        'nepal_teams': nepal_teams,
        'india_teams': india_teams,
        'other_teams': other_teams,
        'cricket_teams': cricket_teams,
        'football_teams': football_teams,
        'volleyball_teams': volleyball_teams,
        'user_profile': user_profile,
    }
    return render(request, 'sports/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def search(request):
    """
    View function for handling search requests across teams, matches, blog posts, and players.
    """
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', 'all')
    match_status = request.GET.get('status', 'all')
    
    results = {
        'teams': [],
        'matches': [],
        'blog_posts': [],
        'players': [] # Add players list
    }
    
    if query:
        # Apply filters based on type
        if filter_type in ['all', 'teams']:
            results['teams'] = Team.objects.filter(name__icontains=query)
        
        if filter_type in ['all', 'matches']:
            matches_query = Match.objects.filter(
                models.Q(team1__name__icontains=query) | 
                models.Q(team2__name__icontains=query) |
                models.Q(location__icontains=query)
            )
            
            # Apply match status filter
            if match_status != 'all':
                matches_query = matches_query.filter(status=match_status)
                
            results['matches'] = matches_query
        
        if filter_type in ['all', 'blog']:
            results['blog_posts'] = BlogPost.objects.filter(
                models.Q(title__icontains=query) | 
                models.Q(content__icontains=query)
            )

        # --- Add Player Search ---
        if filter_type in ['all', 'players']:
            results['players'] = Player.objects.filter(name__icontains=query)
        # --- End of Player Search Addition ---
            
    # Get counts for each type
    counts = {
        'all': sum(len(results[key]) for key in results),
        'teams': len(results['teams']),
        'matches': len(results['matches']),
        'blog': len(results['blog_posts']),
        'players': len(results['players']) # Add player count
    }
    
    return render(request, 'sports/search.html', {
        'query': query,
        'results': results,
        'filter_type': filter_type,
        'match_status': match_status,
        'counts': counts
    })

def match_detail(request, match_id):
    """
    View function for displaying detailed match information, including squads.
    """
    match = get_object_or_404(Match, id=match_id)

    # Get related data
    events = match.events.all().order_by('minute') # Get match events

    # --- Fetch player records for both teams for this specific match ---
    # Use select_related to optimize database queries
    team1_players_records = PlayerMatchRecord.objects.filter(
        match=match, team=match.team1
    ).select_related('player', 'team')

    team2_players_records = PlayerMatchRecord.objects.filter(
        match=match, team=match.team2
    ).select_related('player', 'team')
    # --- End of squad data fetching ---

    context = {
        'match': match,
        'events': events,
        'team1_players_records': team1_players_records,
        'team2_players_records': team2_players_records,
    }
    return render(request, 'sports/match_detail.html', context)

# for manual scoring

from django.contrib.auth.decorators import user_passes_test
from .forms import MatchForm, TeamForm

@user_passes_test(lambda u: u.is_staff)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match added successfully!')
            return redirect('home')
    else:
        form = MatchForm()
    
    return render(request, 'sports/add_match.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def add_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team added successfully!')
            return redirect('add_team')
    else:
        form = TeamForm()
    
    return render(request, 'sports/add_team.html', {'form': form})

@method_decorator(csrf_exempt, name='dispatch')
class TeamOptionsView(View):
    def get(self, request):
        sport = request.GET.get('sport')
        if sport:
            teams = Team.objects.filter(sport=sport).values('id', 'name')
            return JsonResponse({'teams': list(teams)})
        return JsonResponse({'teams': []})


def tournament_detail(request, tournament_id):
    """
    View function for displaying tournament details, matches, standings, and records.
    Prioritizes custom standings from the Standings model.
    """
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    # Determine which section to display
    active_section = request.GET.get('section', 'matches') # Default to 'matches'
    
    # Get all matches for this tournament, ordered by date
    matches = Match.objects.filter(tournament=tournament).order_by('date')
    
    # --- Fetch Standings ---
    # Try to get custom standings first
    custom_standings = Standings.objects.filter(tournament=tournament).order_by('position')
    # Flag to indicate if we are using custom standings
    using_custom_standings = custom_standings.exists()
    
    # If no custom standings, fallback logic could be implemented here
    # For now, we'll pass an empty queryset if custom standings don't exist
    # and let the template handle the display logic.
    standings_data = custom_standings # Pass the queryset directly
    
    # Placeholder for records data (as before or new logic)
    records_data = []
    # if active_section == 'records':
    #     # Implement records logic
    #     pass

    context = {
        'tournament': tournament,
        'matches': matches,
        'active_section': active_section,
        'standings_data': standings_data, # Pass the standings queryset
        'using_custom_standings': using_custom_standings, # Pass flag to template
        'records_data': records_data,
    }
    return render(request, 'sports/tournament_detail.html', context)

def team_detail(request, team_id):
    """
    View function for displaying team details, matches, and squad.
    """
    team = get_object_or_404(Team, id=team_id)
    
    # Determine which section to display
    active_section = request.GET.get('section', 'squad') # Default to 'squad'
    
    # Get players associated with this team
    players = Player.objects.filter(team=team).order_by('name') 
    
    # Get matches for this team (both home and away)
    matches = Match.objects.filter(
        Q(team1=team) | Q(team2=team)
    ).select_related('team1', 'team2', 'tournament').order_by('-date')
    
    context = {
        'team': team,
        'players': players,
        'matches': matches,
        'active_section': active_section,
    }
    return render(request, 'sports/team_detail.html', context)

def blog_detail(request, blog_id):
    """
    View function for displaying a single blog post.
    """
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    
    # Optional: Get related or recent blog posts
    # related_posts = BlogPost.objects.exclude(id=blog_post.id).order_by('-created_at')[:3]
    
    context = {
        'post': blog_post,
        # 'related_posts': related_posts, # Uncomment if using related posts
    }
    return render(request, 'sports/blog_detail.html', context)

def series_list(request):
    """
    View function for displaying a list of all tournaments/series, with filtering and categorization.
    """
    # --- Get filter parameters from the request ---
    selected_sport = request.GET.get('sport', '')
    selected_status = request.GET.get('status', 'all') # Default to 'all'

    # Start with all tournaments
    tournaments = Tournament.objects.all()

    # --- Apply Filters ---
    if selected_sport:
        tournaments = tournaments.filter(sport=selected_sport)
    
    # --- Categorize Tournaments ---
    # Get distinct sports for the filter dropdown
    all_sports = Team.SPORT_CHOICES # Use choices from Team model
    
    # --- Prepare categorized lists ---
    # Get current date/time
    now = timezone.now()
    
    # Query for ongoing tournaments (you might need to adjust this logic based on your definition of 'ongoing')
    # Example: tournaments that have started but not ended, or have recent matches
    # Placeholder: tournaments with matches happening today or in the last day or two
    # A more robust way is to check Match status.
    # Let's use matches for a better definition:
    # Ongoing: Has at least one 'live' match
    # Upcoming: No 'live' or 'completed' matches, but has 'upcoming' matches
    # Completed: All matches are 'completed' or past date with no future/upcoming matches
    
    # Get IDs for each category based on matches
    live_tournament_ids = Match.objects.filter(status='live').values_list('tournament_id', flat=True).distinct()
    upcoming_tournament_ids = Match.objects.filter(status='upcoming').exclude(tournament_id__in=live_tournament_ids).values_list('tournament_id', flat=True).distinct()
    # Completed: Tournaments that are not live or upcoming, and either have completed matches or are past their end date
    # This is a bit complex. Let's simplify for now:
    # Completed: Tournaments that are not in live or upcoming lists.
    # This might need refinement.
    

    # Filter the main queryset based on status filter
    categorized_tournaments = {
        'ongoing': [],
        'upcoming': [],
        'completed': []
    }
    
    if selected_status == 'all':
        # Get all tournaments again after sport filter
        filtered_tournaments = tournaments
    elif selected_status == 'ongoing':
        filtered_tournaments = tournaments.filter(id__in=live_tournament_ids)
    elif selected_status == 'upcoming':
        filtered_tournaments = tournaments.filter(id__in=upcoming_tournament_ids)
    elif selected_status == 'completed':
         # Placeholder logic: Not live and not upcoming
         # Refine this logic as needed based on your data model and business rules
         filtered_tournaments = tournaments.exclude(id__in=live_tournament_ids).exclude(id__in=upcoming_tournament_ids)
    else:
        filtered_tournaments = tournaments # Fallback

    # --- Re-categorize the filtered list ---
    # Even if filtered, we might want to show them in the right sections
    # unless the filter specifically asks for a status.
    if selected_status == 'all':
         # Categorize all filtered tournaments
        for t in filtered_tournaments:
            if t.id in live_tournament_ids:
                categorized_tournaments['ongoing'].append(t)
            elif t.id in upcoming_tournament_ids:
                categorized_tournaments['upcoming'].append(t)
            else:
                categorized_tournaments['completed'].append(t)
    else:
        # If filtered by status, put all results in that category
        categorized_tournaments[selected_status] = list(filtered_tournaments)
        

    # --- Order tournaments within categories ---
    # You can define ordering logic here (e.g., by start date, name)
    categorized_tournaments['ongoing'].sort(key=lambda x: x.name) # Example sort
    categorized_tournaments['upcoming'].sort(key=lambda x: (x.start_date or timezone.datetime.max.date(), x.name)) # Sort by start date, then name
    categorized_tournaments['completed'].sort(key=lambda x: (x.end_date or x.start_date or timezone.datetime.min.date(), x.name), reverse=True) # Sort by end/start date desc, then name
    

    context = {
        'all_sports': all_sports,
        'selected_sport': selected_sport,
        'selected_status': selected_status,
        'categorized_tournaments': categorized_tournaments,
        # 'tournaments': filtered_tournaments, # Pass the filtered list if needed elsewhere
    }
    return render(request, 'sports/series_list.html', context)

def player_detail(request, player_id):
    """
    View function for displaying player details and stats.
    """
    player = get_object_or_404(Player, id=player_id)

    # Example: Prepare affiliated teams (if needed)
    affiliated_teams = [player.team] if player.team else []

    # Example: Prepare cricket batting stats context
    cricket_batting_stats = {}
    # You would fill this dictionary with actual stats logic as needed

    # Example: Prepare football stats context
    football_stats = {}
    if player.team and player.team.sport == 'football':
        # Overall stats are directly on the player model in this example
        football_stats['Overall'] = {
            'matches': getattr(player, 'total_matches', 0),
            'goals': getattr(player, 'total_goals', 0),
            'assists': getattr(player, 'total_assists', 0),
            'yellow_cards': getattr(player, 'total_yellow_cards', 0),
            'red_cards': getattr(player, 'total_red_cards', 0),
            # Add more stats as fields are added to the model
        }
    # Add logic for other formats if applicable

    # --- Get recent matches (optional) ---
    # recent_matches = Match.objects.filter(
    #     models.Q(team1__players=player) | models.Q(team2__players=player) # This needs Player in Team model or MatchSquad
    #     # Or using PlayerMatchRecord:
    #     # id__in=PlayerMatchRecord.objects.filter(player=player).values('match')
    # ).order_by('-date')[:5]

    context = {
        'player': player,
        'affiliated_teams': affiliated_teams,
        'cricket_batting_stats': cricket_batting_stats,
        'football_stats': football_stats,
        # 'recent_matches': recent_matches, # Uncomment if using
    }
    return render(request, 'sports/player_detail.html', context)