from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class FitnessActivity(models.Model):
    ACTIVITY_CHOICES = [
        ('RUN', 'Running'),
        ('YOG', 'Yoga'),
        ('CYC', 'Cycling'),
        ('WEI', 'Wheight Lift'),
        # Add more activities as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=3, choices=ACTIVITY_CHOICES)
    duration = models.DurationField()  # e.g., 30 minutes
    intensity = models.CharField(max_length=50)  # e.g., moderate, high
    calories_burned = models.IntegerField()
    date_time = models.DateTimeField()
    # Add TSS field
    tss = models.FloatField(null=True, blank=True)  # TSS can be a float value

    def __str__(self):
        return f"{self.activity_type} on {self.date_time.strftime('%Y-%m-%d')}"


class UserProfile(models.Model):
    """
    User Profile
        Extend the default User model using a One-to-One link.
        Fields: date of birth, height, weight, fitness level, etc.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    height = models.IntegerField()
    weight = models.IntegerField()
    fitness_level = models.IntegerField()
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class FitnessGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='fitness_groups')  # Change related_name to something unique
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)  # New field to indicate if the group is public or private

    def __str__(self):
        return self.name

# class DietaryLog(models.Model):
#     """
#     Dietary Log
#         Fields: user (ForeignKey to User), food item, calories, nutrients (carbs, proteins, fats), quantity, date/time of meal.
#     """
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     food_item = models.CharField(max_length=50)
#     calories = models.IntegerField()
#     carbs = models.IntegerField()
#     proteins = models.IntegerField()
#     fats = models.IntegerField()
#     quantity = models.IntegerField()
#     date_time = models.DateTimeField()

class FitnessGoal(models.Model):
    """
    Fitness Goal
        Fields: user (ForeignKey to User), goal type (e.g., weight loss, hydration), target value, start date, end date, current progress.
    """
    GOAL_CHOICES = [
        ('WGT', 'Weight Loss'),
        ('HYD', 'Hydration'),
        ('MUS', 'Muscle Gain'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.CharField(max_length=3, choices=GOAL_CHOICES)
    target_value = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    current_progress = models.IntegerField()

    def __str__(self):
        return f"{self.goal_type} goal for {self.user.username}"

class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} - {self.weight} kg on {self.date}'

# models.py
class Challenge(models.Model):
    CHALLENGE_TYPE_CHOICES = [
        ('CAL', 'Calories'),
        ('KM', 'Kilometers'),
        ('TSS', 'TSS'),
        ('Fastest Run', 'Time'),
    ]
    name = models.CharField(max_length=100)
    fitness_group = models.ForeignKey(FitnessGroup, on_delete=models.CASCADE)
    challenge_type = models.CharField(max_length=12, choices=CHALLENGE_TYPE_CHOICES)
    target_amount = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    users = models.ManyToManyField(User, related_name='challenges', blank=True)
    is_public = models.BooleanField(default=True)  # New field to indicate if the challenge is public or private

    def __str__(self):
        return f"Challenge: {self.challenge_type} - Target: {self.target_amount}"

class LeaderboardEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.challenge} - Progress: {self.progress}"

#Creating invitation system
class InviteType(models.TextChoices):
    GROUP_INVITE = 'FitnessGroup', 'Group Invite'
    CHALLENGE_INVITE = 'CHALLENGE', 'Challenge Invite'

class Invitation(models.Model):
    INVITE_TYPE_CHOICES = [
        ('fitnessGroup', 'FitnessGroup'),
        ('challenge', 'Challenge'),
    ]
    invite_type = models.CharField(max_length=20, choices=INVITE_TYPE_CHOICES, default=InviteType.GROUP_INVITE)
    fitness_group = models.ForeignKey(FitnessGroup, on_delete=models.CASCADE, null=True, blank=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Add status field

    def clean(self):
        if self.invite_type == 'challenge' and not self.challenge:
            raise ValidationError('Challenge must be selected for challenge invitations.')
        if self.invite_type == 'fitness_group' and not self.fitness_group:
            raise ValidationError('Fitness Group must be selected for fitness group invitations.')
        if self.invite_type == 'challenge' and self.challenge.group != self.group:
            raise ValidationError('Challenge must belong to the selected group.')

