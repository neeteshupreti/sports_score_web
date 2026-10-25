from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import TeamViewSet, MatchViewSet, BlogPostViewSet, api_overview, LiveMatchesView, UpcomingMatchesView

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'blog', BlogPostViewSet)

urlpatterns = [
    path('', api_overview, name='api-overview'),
    path('', include(router.urls)),
    path('matches/live/', LiveMatchesView.as_view(), name='live-matches'),
    path('matches/upcoming/', UpcomingMatchesView.as_view(), name='upcoming-matches'),
]