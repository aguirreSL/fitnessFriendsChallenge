from django.shortcuts import render, redirect, get_object_or_404
from .models import FitnessActivity, WeightEntry, UserProfile, Group, Challenge, LeaderboardEntry, Invitation
from .forms import UserRegisterForm, ActivityForm, WeightEntryForm, GroupForm, ChallengeForm, InvitationForm #,DietaryLogForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum #added to build home 
from django.utils.timezone import now, timedelta #added to build home 

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
       # Redirect to login page if user is not authenticated
        return redirect('login')  # Make sure to replace 'login' with your actual login view name

    # Fetch all active challenges related to the user's fitness groups
    user_groups = request.user.fitness_groups.all()  # Correct related_name
    active_challenges = Challenge.objects.filter(group__in=user_groups, end_date__gte=now())

    # Handle selected challenge
    selected_challenge_id = request.GET.get('challenge')
    if selected_challenge_id:
        selected_challenge = get_object_or_404(Challenge, id=selected_challenge_id)
        # Get all leaderboard entries for the selected challenge
        leaderboard_entries = LeaderboardEntry.objects.filter(challenge=selected_challenge)
    else:
        selected_challenge = None
        # Get all leaderboard entries for challenges related to user's groups
        leaderboard_entries = LeaderboardEntry.objects.filter(challenge__group__in=user_groups)
    
    # Prepare leaderboard data
    leaderboard_data = (
        leaderboard_entries
        .values('user__username')
        .annotate(total_tss=Sum('progress'))
        .order_by('-total_tss')
    )

    # Compute user's rank
    leaderboard_list = list(leaderboard_data)  # Convert to list to handle indexing
    user_rank = next((item for item in leaderboard_list if item['user__username'] == request.user.username), None)
    user_position = None
    if user_rank:
        user_position = leaderboard_list.index(user_rank) + 1  # Rank starts from 1

    # Fetch TSS logs for the last week
    one_week_ago = now() - timedelta(days=7)
    tss_logs = FitnessActivity.objects.filter(user=request.user, date_time__gte=one_week_ago).values('date_time').annotate(tss_sum=Sum('tss'))

    # Convert tss_logs to separate lists of dates and TSS sums
    tss_dates = [log['date_time'].strftime('%Y-%m-%d') for log in tss_logs]
    tss_sums = [log['tss_sum'] for log in tss_logs]

    return render(request, 'fitness/home.html', {
        'active_challenges': active_challenges,
        'selected_challenge': selected_challenge,
        'leaderboard_data': leaderboard_list,  # Pass the list to the template
        'user_position': user_position,
        'tss_dates': tss_dates,
        'tss_sums': tss_sums,
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
    groups = Group.objects.filter(members=request.user)
    challenges = Challenge.objects.filter(group__members=request.user)
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'groups': groups,
        'challenges': challenges
    }
    return render(request, 'fitness/profile.html', context)

def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            group.members.add(request.user)  # Add the creator to the group
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'fitness/create_group.html', {'form': form})

def group_list(request):
    user_groups = request.user.groups.all()  # Groups the user is part of
    all_groups = Group.objects.all()  # All groups

    return render(request, 'fitness/group_list.html', {
        'user_groups': user_groups,
        'all_groups': all_groups
    })


def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('challenge_list')
    else:
        form = ChallengeForm()
    return render(request, 'create_challenge.html', {'form': form})

def challenge_list(request):
    challenges = Challenge.objects.filter(group__members=request.user)
    return render(request, 'challenge_list.html', {'challenges': challenges})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    challenges = Challenge.objects.filter(group=group)
    members = group.members.all()  # Get all members of the group

    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.group = group  # Set the group for the invitation
            invitation.save()
            return redirect('group_detail', group_id=group_id)  # Redirect to avoid resubmission
    else:
        form = InvitationForm()

    return render(request, 'fitness/group_detail.html', {
        'group': group,
        'challenges': challenges,
        'members': members,
        'form': form
    })

@login_required
def challenge_list(request):
    challenges = Challenge.objects.filter(group__in=request.user.fitness_groups.all())
    return render(request, 'fitness/challenge_list.html', {'challenges': challenges})

@login_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('challenge_list')
    else:
        form = ChallengeForm(user=request.user)
    return render(request, 'fitness/challenge_form.html', {'form': form})

@login_required
def edit_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, group__in=request.user.fitness_groups.all())

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
                group=challenge.group,
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
def send_invitation(request, group_id=None, challenge_id=None):
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
                invitation.group = challenge.group  # Set the group based on the challenge
            
            elif group_id:
                # Handle group invitation
                group = get_object_or_404(Group, id=group_id)
                invitation.group = group
                invitation.invite_type = 'group'
            
            invitation.save()
            return redirect('invitations_list')  # Redirect to the list of invitations after sending
    else:
        initial_data = {}
        if challenge_id:
            initial_data['challenge'] = challenge_id
        if group_id:
            initial_data['group'] = group_id
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
            invitation.group.members.add(invitation.receiver)
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

def get_group_users(request, group_id):
    group = Group.objects.get(id=group_id)
    users = group.members.all()
    challenges = Challenge.objects.filter(group=group)
    users_data = [{'id': user.id, 'username': user.username} for user in users]
    challenges_data = [{'id': challenge.id, 'name': challenge.name} for challenge in challenges]
    return JsonResponse({'users': users_data, 'challenges': challenges_data})

def all_groups(request):
    groups = Group.objects.all()  # Retrieve all groups
    return render(request, 'fitness/all_groups.html', {'groups': groups})

    