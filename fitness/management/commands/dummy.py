from django.core.management.base import BaseCommand
from fitness.models import Challenge, User, FitnessActivity
from django.utils.timezone import make_aware, now
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generate dummy data for users'

    def handle(self, *args, **kwargs):
        # Get or create the users
        users = []
        for username in ['seag', 'seagPro', 'seag2']:
            user, created = User.objects.get_or_create(username=username)
            users.append(user)

        # Get or create the 'All Year' challenge
        challenge, created = Challenge.objects.get_or_create(name='All Year')

        # Define the date range (convert start_date to datetime and make it timezone-aware)
        start_date = make_aware(datetime.combine(challenge.start_date, datetime.min.time()))
        end_date = now()  # This is already timezone-aware

        # Generate random TSS data for each user
        for user in users:
            for _ in range(10):  # 10 activities per user
                random_days = random.randint(1, (end_date - start_date).days)
                activity_date = start_date + timedelta(days=random_days)
                tss = random.uniform(10, 150)  # Random TSS value
                duration = timedelta(minutes=random.randint(30, 120))  # Random duration
                intensity = random.choice(['low', 'moderate', 'high'])  # Random intensity
                calories_burned = random.randint(200, 800)  # Random calories burned
                activity_type = random.choice(['RUN', 'YOG', 'CYC'])  # Random activity type

                # Create a fitness activity for each user
                FitnessActivity.objects.create(
                    user=user,
                    activity_type=activity_type,
                    duration=duration,
                    intensity=intensity,
                    calories_burned=calories_burned,
                    date_time=activity_date,
                    tss=tss,
                )

        self.stdout.write(self.style.SUCCESS('Dummy data created!'))
