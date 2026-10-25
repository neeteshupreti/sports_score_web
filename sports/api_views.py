# File: sports/api_views.py (or add to sports/views.py)
from rest_framework import generics, viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Match, Team, Player, Tournament
from .serializers import MatchScoreSerializer, MatchDetailSerializer

# --- Example 1: Simple Function-Based View for Live Scores ---
@api_view(['GET'])
@permission_classes([permissions.AllowAny]) # Publicly accessible endpoint
def live_scores_api(request):
    """
    API endpoint that returns a list of live matches with scores.
    """
    live_matches = Match.objects.filter(status='live')
    serializer = MatchScoreSerializer(live_matches, many=True)
    return Response(serializer.data)

# --- Example 2: Generic Class-Based View for Filtering Scores ---
class ScoresListView(generics.ListAPIView):
    """
    API endpoint that allows getting a list of matches, filterable by sport, status, etc.
    """
    serializer_class = MatchScoreSerializer
    permission_classes = [permissions.AllowAny] # Adjust permissions as needed
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sport', 'status', 'tournament'] # Fields you can filter by ?sport=cricket&status=completed
    search_fields = ['team1__name', 'team2__name', 'location'] # Fields for ?search=
    ordering_fields = ['date', 'team1_score', 'team2_score'] # Fields for ?ordering=
    ordering = ['-date'] # Default ordering

    def get_queryset(self):
        """
        Optionally, filter the queryset based on query parameters.
        E.g., default to 'live' status if no status filter is given.
        """
        queryset = Match.objects.all()
        # Example: Default to live if no status filter
        # if not self.request.query_params.get('status'):
        #     queryset = queryset.filter(status='live')
        return queryset

# --- Example 3: ViewSet for Detailed Match Operations (Read/Write) ---
# This requires more careful permission handling for write operations.
class MatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Matches.
    Provides list, create, retrieve, update, destroy actions.
    WARNING: This is powerful, ensure strict permissions for write actions.
    """
    queryset = Match.objects.all()
    serializer_class = MatchDetailSerializer # Use detailed serializer

    # Define default permissions (start restrictive)
    # permission_classes = [permissions.IsAuthenticated] # Require login for any access
    permission_classes = [permissions.IsAdminUser] # Require admin/superuser for any access (safer start)

    # Add filtering if desired
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sport', 'status', 'tournament']
    search_fields = ['team1__name', 'team2__name']

    # Override get_permissions for granular control (optional but recommended)
    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     Example: Allow anyone to list/retrieve, but only admins to create/update/delete.
    #     """
    #     if self.action == 'list' or self.action == 'retrieve':
    #         permission_classes = [permissions.AllowAny] # Or IsAuthenticated
    #     else:
    #         permission_classes = [permissions.IsAdminUser] # Only admins for CUD
    #     return [permission() for permission in permission_classes]

    # Example: Custom action to update only score-related fields (safer than full update)
    # from rest_framework.decorators import action
    # @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated]) # Requires auth
    # def update_score(self, request, pk=None):
    #     """
    #     Custom action to partially update score-related fields for a specific match.
    #     """
    #     match = self.get_object()
    #     # Use the score-specific serializer for partial updates
    #     serializer = MatchScoreSerializer(match, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=400)

# --- Example 4: Endpoint for a Specific Match Detail ---
class MatchDetailView(generics.RetrieveAPIView):
    """
    API endpoint that returns detailed information for a single match.
    """
    queryset = Match.objects.all()
    serializer_class = MatchDetailSerializer # Or MatchScoreSerializer if less detail needed
    permission_classes = [permissions.AllowAny] # Adjust as needed

# ... Add views for Teams, Players, Tournaments if needed ...