from django.shortcuts import render, redirect, get_object_or_404
from .models import FitnessActivity, WeightEntry, UserProfile, FitnessGroup, Challenge, LeaderboardEntry, Invitation
from .forms import UserRegisterForm, ActivityForm, WeightEntryForm, FitnessGroupForm, ChallengeForm, InvitationForm #,DietaryLogForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q  #added to build home 
from django.utils.timezone import now, timedelta, make_aware #added to build home 
from django.contrib.auth.models import User  # Import the User model
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def activity_list(request):
    activities = FitnessActivity.objects.filter(user=request.user)
    return render(request, 'fitness/activity_list.html', {'activities': activities})

def custom_logout(request):
    logout(request)
    return redirect('login')

# def diet_log(request):
#     diet_logs = DietaryLog.objects.filter(user=request.user)
#     return render(request, 'fitness/diet_log.html', {'diet_logs': diet_logs})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the login page after successful registration
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'fitness/register.html', {'form': form})

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch user's groups and active challenges
    user_groups = request.user.fitness_groups.all()
    active_challenges = Challenge.objects.filter(fitness_group__in=user_groups, end_date__gte=now())

    selected_challenge_id = request.GET.get('challenge')
    tss_data = []

    if selected_challenge_id:
        try:
            selected_challenge = Challenge.objects.get(id=selected_challenge_id)
        except Challenge.DoesNotExist:
            logger.error(f'Challenge with id {selected_challenge_id} does not exist.')
            selected_challenge = None
            leaderboard_data = []
        else:
            start_date = make_aware(datetime.combine(selected_challenge.start_date, datetime.min.time()))
            end_date = now()
            
            participants = selected_challenge.users.all()
            activities = FitnessActivity.objects.filter(user__in=participants, date_time__range=[start_date, end_date])

            if participants.exists():
                one_week_ago = now() - timedelta(days=7)
                leaderboard_data = (
                    activities
                    .values('user__username')
                    .annotate(
                        total_tss=Sum('tss'),
                        week_tss=Sum('tss', filter=Q(date_time__gte=one_week_ago))
                    )
                    .order_by('-total_tss')
                )
                
                for entry in leaderboard_data:
                    entry['challenge_name'] = selected_challenge.name
                    entry['challenge_start_date'] = selected_challenge.start_date
                    entry['challenge_end_date'] = selected_challenge.end_date

                # Fetch TSS data for the graph
                for participant in participants:
                    tss_logs = FitnessActivity.objects.filter(user=participant, date_time__range=[start_date, end_date]).values('date_time').annotate(tss_sum=Sum('tss'))
                    tss_dates = [log['date_time'].strftime('%Y-%m-%d') for log in tss_logs]
                    tss_sums = [log['tss_sum'] for log in tss_logs]
                    tss_data.append({
                        'username': participant.username,
                        'dates': tss_dates,
                        'sums': tss_sums
                    })
            else:
                leaderboard_data = []

    else:
        selected_challenge = None
        leaderboard_data = []
        one_week_ago = now() - timedelta(days=7)
        
        all_challenges = Challenge.objects.filter(fitness_group__in=user_groups)
        for challenge in all_challenges:
            start_date = make_aware(datetime.combine(challenge.start_date, datetime.min.time()))
            end_date = make_aware(datetime.combine(challenge.end_date, datetime.min.time()))
            activities = FitnessActivity.objects.filter(user=request.user, date_time__range=[start_date, end_date])
            
            if activities.exists():  # Only process if there are activities
                challenge_leaderboard = (
                    activities
                    .values('user__username')
                    .annotate(
                        total_tss=Sum('tss'),
                        week_tss=Sum('tss', filter=Q(date_time__gte=one_week_ago))
                    )
                    .order_by('-total_tss')
                )
                
                for entry in challenge_leaderboard:
                    entry['challenge_name'] = challenge.name
                    entry['challenge_start_date'] = challenge.start_date
                    entry['challenge_end_date'] = challenge.end_date
                    leaderboard_data.append(entry)

    user_position = None
    if selected_challenge:
        for idx, entry in enumerate(leaderboard_data):
            if entry['user__username'] == request.user.username:
                user_position = idx + 1
                break

    return render(request, 'fitness/home.html', {
        'active_challenges': active_challenges,
        'selected_challenge': selected_challenge,
        'leaderboard_data': leaderboard_data,
        'user_position': user_position,
        'tss_data': tss_data,
    })



def add_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            return redirect('activity_list')
    else:
        form = ActivityForm()  # Make sure this line is correct

    return render(request, 'fitness/add_activity.html', {'form': form})

# def add_diet_log(request):
#     if request.method == 'POST':
#         form = DietaryLogForm(request.POST)
#         if form.is_valid():
#             dietary_log = form.save(commit=False)
#             dietary_log.user = request.user  # Set the user to the current user
#             dietary_log.save()
#             return redirect('diet_log')
#     else:
#         form = DietaryLogForm()
#     return render(request, 'fitness/add_diet_log.html', {'form': form})



def weight_tracker(request):
    if request.method == 'POST':
        form = WeightEntryForm(request.POST)
        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()
            return redirect('weight_tracker')
    else:
        form = WeightEntryForm()

    # Fetch weight entries for the graph
    weight_entries = WeightEntry.objects.filter(user=request.user).order_by('date')
    dates = [entry.date.strftime("%Y-%m-%d") for entry in weight_entries]
    weights = [entry.weight for entry in weight_entries]

    return render(request, 'fitness/weight_tracker.html', {
        'form': form, 
        'dates': dates, 
        'weights': weights
    })


def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    groups = FitnessGroup.objects.filter(members=request.user)
    
    # Update this query to reference the correct field name
    challenges = Challenge.objects.filter(fitness_group__members=request.user)
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'fitness_groups': groups,
        'challenges': challenges
    }
    return render(request, 'fitness/profile.html', context)


def create_group(request):
    if request.method == 'POST':
        form = FitnessGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            group.members.add(request.user)  # Add the creator to the group
            print("Group created:", group)  # Debugging output
            return redirect('group_list')
        else:
            print("Form errors:", form.errors)  # Show errors if invalid
    else:
        form = FitnessGroupForm()
    return render(request, 'fitness/create_group.html', {'form': form})

def group_list(request):
    user_groups = request.user.fitness_groups.all()  # Groups the user is part of
    all_groups = FitnessGroup.objects.all()  # All groups
    # Handle form submission for creating a group
    if request.method == 'POST':
        form = FitnessGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            group.members.add(request.user)
            return redirect('group_list')
    else:
        form = FitnessGroupForm()
    return render(request, 'fitness/group_list.html', {
        'user_groups': user_groups,
        'all_groups': all_groups,
        'form': form,
    })

@login_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            challenge.users.add(request.user)  # Add the current user to the challenge's users
            return redirect('challenge_list')
    else:
        form = ChallengeForm(user=request.user)
    return render(request, 'fitness/challenge_form.html', {'form': form})

def challenge_list(request):
    challenges = Challenge.objects.filter(fitness_group__members=request.user)
    return render(request, 'fitness/challenge_list.html', {'challenges': challenges})

@login_required
def group_detail(request, fitness_group_id):
    group = get_object_or_404(FitnessGroup, id=fitness_group_id)
    challenges = Challenge.objects.filter(fitness_group=group)
    members = group.members.all()
    non_members = User.objects.exclude(id__in=members.values_list('id', flat=True))  # Non-members
    
    if request.method == 'POST':
        form = InvitationForm(request.POST, group=group)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.fitness_group = group
            invitation.save()
            return redirect('group_detail', fitness_group_id=fitness_group_id)
    else:
        form = InvitationForm(group=group)

    return render(request, 'fitness/group_detail.html', {
        'group': group,
        'challenges': challenges,
        'members': members,
        'non_members': non_members,  # Pass non-members to the template
        'form': form
    })

@login_required
def edit_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, fitness_group__in=request.user.fitness_groups.all())

    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('challenge_list')
        # Handle invitation form submission
        if 'invitee' in request.POST:
            invitee_id = request.POST.get('invitee')
            invitee = get_object_or_404(UserProfile, pk=invitee_id)
            Invitation.objects.create(
                invitee=invitee,
                group=challenge.fitness_group,
                challenge=challenge,
                sender=request.user
            )
            return redirect('challenge_list')  # After sending invitation

    else:
        form = ChallengeForm(instance=challenge, user=request.user)

    return render(request, 'fitness/challenge_form.html', {'form': form})

@login_required
def create_invitation(request):
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invitations:list')
    else:
        form = InvitationForm()
    return render(request, 'invitations/create_invitation.html', {'form': form})

@login_required
def send_invitation(request, fitness_group_id=None, challenge_id=None):
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.sender = request.user
            
            if challenge_id:
                # Handle challenge invitation
                challenge = get_object_or_404(Challenge, id=challenge_id)
                invitation.challenge = challenge
                invitation.invite_type = 'challenge'
                invitation.fitness_group = challenge.fitness_group  # Set the group based on the challenge
            
            elif fitness_group_id:
                # Handle group invitation
                fitness_group = get_object_or_404(FitnessGroup, id=fitness_group_id)
                invitation.fitness_group = fitness_group
                invitation.invite_type = 'group'
            
            invitation.save()
            return redirect('invitations_list')  # Redirect to the list of invitations after sending
    else:
        initial_data = {}
        if challenge_id:
            initial_data['challenge'] = challenge_id
        if fitness_group_id:
            initial_data['group'] = fitness_group_id
        form = InvitationForm(initial=initial_data)
    
    return render(request, 'fitness/send_invitation.html', {'form': form})

@login_required
def respond_invitation(request, invitation_id, response):
    invitation = Invitation.objects.get(id=invitation_id)
    
    if invitation.receiver != request.user:
        return redirect('home')  # Prevent unauthorized access
    
    if response == 'accept':
        invitation.status = 'Accepted'
        # Add user to group or challenge based on the invitation type
        if invitation.invitation_type == 'GROUP':
            invitation.fitness_group.members.add(invitation.receiver)
        elif invitation.invitation_type == 'CHALLENGE':
            invitation.challenge.participants.add(invitation.receiver)
    elif response == 'decline':
        invitation.status = 'Declined'
    
    invitation.save()
    return redirect('invitations_list')  # Redirect to a page listing all invitations

@login_required
def invitations_list(request):
    invitations = Invitation.objects.filter(receiver=request.user)
    return render(request, 'fitness/invitations_list.html', {'invitations': invitations})  

def get_group_users(request, fitness_group_id):
    fitness_group = FitnessGroup.objects.get(id=fitness_group_id)
    users = fitness_group.members.all()
    challenges = Challenge.objects.filter(fitness_group=fitness_group)
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    challenges_data = [{'id': challenge.id, 'name': challenge.name} for challenge in challenges]
    return JsonResponse({'users': users_data, 'challenges': challenges_data})

def all_groups(request):
    groups = FitnessGroup.objects.all()  # Retrieve all fitness groups
    return render(request, 'fitness/all_groups.html', {'groups': groups})

    