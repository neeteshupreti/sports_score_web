from django.core.management.base import BaseCommand
from sports.models import Team, Match, BlogPost
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        # Create sample teams
        nepal_cricket = Team.objects.create(name="Nepal National Cricket Team", country="Nepal", sport="cricket")
        india_cricket = Team.objects.create(name="India National Cricket Team", country="India", sport="cricket")
        nepal_football = Team.objects.create(name="Nepal National Football Team", country="Nepal", sport="football")
        india_football = Team.objects.create(name="India National Football Team", country="India", sport="football")
        nepal_volleyball = Team.objects.create(name="Nepal National Volleyball Team", country="Nepal", sport="volleyball")
        india_volleyball = Team.objects.create(name="India National Volleyball Team", country="India", sport="volleyball")
        
        # Create sample matches
        Match.objects.create(
            sport="cricket",
            team1=nepal_cricket,
            team2=india_cricket,
            date=datetime.now() + timedelta(days=2),
            location="Kathmandu, Nepal",
            status="upcoming"
        )
        
        Match.objects.create(
            sport="football",
            team1=nepal_football,
            team2=india_football,
            date=datetime.now() - timedelta(days=1),
            location="New Delhi, India",
            team1_score="2",
            team2_score="1",
            status="completed"
        )
        
        Match.objects.create(
            sport="volleyball",
            team1=nepal_volleyball,
            team2=india_volleyball,
            date=datetime.now(),
            location="Pokhara, Nepal",
            team1_score="25-22",
            team2_score="20-25",
            status="live"
        )
        
        # Create a sample user and blog post
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('password')
            user.save()
        
        BlogPost.objects.create(
            title="Exciting Cricket Match Between Nepal and India",
            content="The upcoming cricket match between Nepal and India promises to be an exciting encounter. Both teams have been preparing rigorously for this event.",
            author=user
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample data'))