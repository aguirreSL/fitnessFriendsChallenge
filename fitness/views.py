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
    user_groups = request.user.fitness_groups.all()  # Correct related_name
    active_challenges = Challenge.objects.filter(group__in=user_groups, end_date__gte=now())

    # Check if a challenge is selected
    selected_challenge_id = request.GET.get('challenge')
    selected_challenge = None
    if selected_challenge_id:
        selected_challenge = Challenge.objects.get(id=selected_challenge_id)

    # Fetch leaderboard data based on selected challenge or all challenges
    if selected_challenge:
        leaderboard_data = (
            LeaderboardEntry.objects.filter(challenge=selected_challenge)
            .values('user__username')
            .annotate(total_tss=Sum('progress'))
            .order_by('-total_tss')[:10]  # Top 10 leaderboard entries
        )
    else:
        leaderboard_data = (
            LeaderboardEntry.objects.filter(challenge__in=active_challenges)
            .values('user__username')
            .annotate(total_tss=Sum('progress'))
            .order_by('-total_tss')[:10]
        )

    # Fetch TSS logs for the last week
    one_week_ago = now() - timedelta(days=7)
    tss_logs = FitnessActivity.objects.filter(user=request.user, date_time__gte=one_week_ago).values('date_time').annotate(tss_sum=Sum('tss'))

    tss_dates = [log['date_time'].strftime('%Y-%m-%d') for log in tss_logs]
    tss_sums = [log['tss_sum'] for log in tss_logs]

    return render(request, 'fitness/home.html', {
        'active_challenges': active_challenges,
        'leaderboard_data': leaderboard_data,
        'selected_challenge': selected_challenge,
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
    context = {
        'user': request.user,
        'user_profile': user_profile
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
    groups = Group.objects.filter(members=request.user)
    print(groups)  # Debugging: Check if groups are retrieved
    return render(request, 'fitness/group_list.html', {'groups': groups})


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

def send_invitation(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.sender = request.user
            invitation.group = group
            invitation.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = InvitationForm()
    return render(request, 'fitness/send_invitation.html', {'form': form, 'group': group})

def respond_invitation(request, invitation_id, response):
    invitation = Invitation.objects.get(id=invitation_id)
    if response == 'accept':
        invitation.status = 'Accepted'
        invitation.group.members.add(invitation.receiver)
    else:
        invitation.status = 'Declined'
    invitation.save()
    return redirect('group_list')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    challenges = Challenge.objects.filter(group=group)
    members = group.members.all()  # Get all members of the group
    return render(request, 'fitness/group_detail.html', {
        'group': group,
        'challenges': challenges,
        'members': members
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
    else:
        form = ChallengeForm(instance=challenge, user=request.user)

    return render(request, 'fitness/challenge_form.html', {'form': form})
  