from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Team, Match, BlogPost
from .serializers import TeamSerializer, MatchSerializer, BlogPostSerializer

@api_view(['GET'])
def api_overview(request):
    api_urls = {
        'Teams': '/api/teams/',
        'Matches': '/api/matches/',
        'Live Matches': '/api/matches/live/',
        'Upcoming Matches': '/api/matches/upcoming/',
        'Blog Posts': '/api/blog/',
    }
    return Response(api_urls)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class LiveMatchesView(generics.ListAPIView):
    queryset = Match.objects.filter(status='live')
    serializer_class = MatchSerializer

class UpcomingMatchesView(generics.ListAPIView):
    queryset = Match.objects.filter(status='upcoming')
    serializer_class = MatchSerializer

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer