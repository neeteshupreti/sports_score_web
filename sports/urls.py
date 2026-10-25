from django.urls import path
from . import views
from . import api_views
from .views import TeamOptionsView

urlpatterns = [
    path('', views.home, name='home'),
    path('scores/', views.scores, name='scores'),
    path('schedule/', views.schedule, name='schedule'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('admin/team-options/', TeamOptionsView.as_view(), name='team_options'),
    path('series/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    # --- Add this line for the series list page ---
    path('series/', views.series_list, name='series_list'), # Note: No trailing slash before <int:tournament_id>/
    path('series/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    # --- API URL Patterns ---
    # 1. Simple Function-Based View
    path('api/live-scores/', api_views.live_scores_api, name='api_live_scores'),

    # 2. Class-Based View for filtered list
    path('api/scores/', api_views.ScoresListView.as_view(), name='api_scores_list'),

    # 3. Detail view for a single match
    path('api/match/<int:pk>/', api_views.MatchDetailView.as_view(), name='api_match_detail'),

    # 4. ViewSet URLs (if using MatchViewSet)
    # path('api/', include(router.urls)), # Includes standard CRUD: /api/matches/, /api/matches/{id}/, etc.

    # 5. Custom action on ViewSet (if defined)
    # path('api/matches/<int:pk>/update-score/', api_views.MatchViewSet.as_view({'patch': 'update_score'}), name='api_match_update_score'),
    # --- End of API URL Patterns ---
]