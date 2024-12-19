from django.shortcuts import render, redirect, get_object_or_404
from .models import FitnessActivity, WeightEntry, UserProfile, FitnessGroup, Challenge, Invitation, InviteType
from .forms import UserRegisterForm, UserProfileForm, ActivityForm, WeightEntryForm, FitnessGroupForm, ChallengeForm, InvitationForm, FitnessGroupAdminForm  #,DietaryLogForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils.timezone import now, timedelta, make_aware, is_naive #added to build home
from django.contrib.auth.models import User  # Import the User model
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def activity_list(request):
    activities = FitnessActivity.objects.filter(user=request.user)
    return render(request, 'fitness/activity_list.html', {'activities': activities})

@login_required
def delete_activity(request, activity_id):
    activity = get_object_or_404(FitnessActivity, id=activity_id, user=request.user)
    if request.method == 'POST':
        activity.delete()
        return redirect('activity_list')
    return render(request, 'fitness/confirm_delete_activity.html', {'activity': activity})

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
        # Select the most recent challenge by start date if no challenge is selected
        if active_challenges.exists():
            selected_challenge = active_challenges.order_by('-start_date').first()
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
            if is_naive(activity.date_time):
                activity.date_time = make_aware(activity.date_time)  # Make datetime aware only if it's naive
            activity.save()
            return redirect('activity_list')
    else:
        form = ActivityForm()

    return render(request, 'fitness/add_activity.html', {'form': form})

def edit_activity(request, activity_id):
    activity = get_object_or_404(FitnessActivity, id=activity_id)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)

    return render(request, 'fitness/edit_activity.html', {'form': form, 'activity': activity})

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


@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    groups = FitnessGroup.objects.filter(members=request.user)
    challenges = Challenge.objects.filter(fitness_group__members=request.user)

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'fitness_groups': groups,
        'challenges': challenges,
    }
    return render(request, 'fitness/profile.html', context)

@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form
    }
    return render(request, 'fitness/edit_profile.html', context)

def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    groups = FitnessGroup.objects.filter(members=user)
    challenges = Challenge.objects.filter(fitness_group__members=user)

    context = {
        'user': user,
        'user_profile': user_profile,
        'fitness_groups': groups,
        'challenges': challenges,
    }
    return render(request, 'fitness/user_profile.html', context)

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
    public_groups = FitnessGroup.objects.filter(is_public=True)  # Public groups
    private_groups = FitnessGroup.objects.filter(is_public=False, members=request.user)  # Private groups the user is part of

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
        'public_groups': public_groups,
        'private_groups': private_groups,
        'form': form,
    })

@login_required
def create_challenge(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST)
        if form.is_valid():
            challenge = form.save(commit=False)
            challenge.save()
            challenge.users.add(request.user)  # Add the current user to the challenge's users
            return redirect('challenge_list')
    else:
        form = ChallengeForm()
    return render(request, 'fitness/challenge_form.html', {'form': form})

def challenge_list(request):
    public_challenges = Challenge.objects.filter(is_public=True)
    private_challenges = Challenge.objects.filter(is_public=False, fitness_group__members=request.user)
    pending_invitations = Invitation.objects.filter(invite_type='challenge', status='Pending')

    return render(request, 'fitness/challenge_list.html', {
        'public_challenges': public_challenges,
        'private_challenges': private_challenges,
        'pending_invitations': pending_invitations,
    })

@login_required
def group_detail(request, fitness_group_id):
    group = get_object_or_404(FitnessGroup, id=fitness_group_id)
    challenges = Challenge.objects.filter(fitness_group=group)
    members = group.members.all()
    non_members = User.objects.exclude(id__in=members.values_list('id', flat=True))  # Non-members

    pending_invitations = Invitation.objects.filter(fitness_group=group, status='Pending')

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
        'form': form,
        'pending_invitations': pending_invitations,  # Pass pending invitations to the template
    })

@login_required
def edit_challenge(request, pk):
    challenge = get_object_or_404(Challenge, pk=pk, fitness_group__in=request.user.fitness_groups.all())

    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
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
        form = ChallengeForm(instance=challenge)

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
    group = get_object_or_404(FitnessGroup, id=fitness_group_id) if fitness_group_id else None
    challenge = get_object_or_404(Challenge, id=challenge_id) if challenge_id else None

    if request.method == 'POST':
        form = InvitationForm(request.POST, group=group, challenge=challenge)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.sender = request.user

            if invitation.invite_type == InviteType.CHALLENGE_INVITE and challenge:
                if not group.members.filter(id=invitation.invitee.id).exists():
                    # Send combined invite
                    Invitation.objects.create(
                        invite_type=InviteType.GROUP_INVITE,
                        fitness_group=group,
                        sender=request.user,
                        invitee=invitation.invitee,
                        message=f"Combined invite: {invitation.message}"
                    )

            invitation.save()
            return redirect('group_detail', fitness_group_id=group.id if group else challenge.fitness_group.id)
    else:
        form = InvitationForm(group=group, challenge=challenge)

    return render(request, 'fitness/send_invitation.html', {'form': form, 'group': group, 'challenge': challenge})

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

@login_required
def toggle_group_visibility(request, fitness_group_id):
    group = get_object_or_404(FitnessGroup, id=fitness_group_id)
    if request.method == 'POST':
        is_public = request.POST.get('is_public') == 'on'
        group.is_public = is_public
        group.save()
        return redirect('group_detail', fitness_group_id=fitness_group_id)

@login_required
def request_to_join_group(request, fitness_group_id):
    group = get_object_or_404(FitnessGroup, id=fitness_group_id)
    if request.method == 'POST':
        Invitation.objects.create(
            invite_type='fitnessGroup',
            fitness_group=group,
            sender=request.user,
            invitee=group.members.first(),  # Placeholder, not used for approval
            message=f"{request.user.username} has requested to join the group."
        )
        return redirect('group_detail', fitness_group_id=fitness_group_id)

@login_required
def approve_join_request(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if request.method == 'POST' and invitation.fitness_group.members.filter(id=request.user.id).exists():
        invitation.status = 'Approved'
        invitation.fitness_group.members.add(invitation.sender)
        invitation.save()
        return redirect('group_detail', fitness_group_id=invitation.fitness_group.id)

@login_required
def reject_join_request(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if request.method == 'POST' and invitation.fitness_group.members.filter(id=request.user.id).exists():
        invitation.status = 'Rejected'
        invitation.save()
        return redirect('group_detail', fitness_group_id=invitation.fitness_group.id)

@login_required
def request_to_join_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    if request.method == 'POST':
        Invitation.objects.create(
            invite_type='challenge',
            challenge=challenge,
            sender=request.user,
            invitee=challenge.users.first(),  # Placeholder, not used for approval
            message=f"{request.user.username} has requested to join the challenge."
        )
        return redirect('challenge_detail', challenge_id=challenge_id)

@login_required
def approve_challenge_join_request(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if request.method == 'POST' and invitation.challenge.fitness_group.members.filter(id=request.user.id).exists():
        invitation.status = 'Approved'
        invitation.challenge.users.add(invitation.sender)
        invitation.save()
        return redirect('challenge_detail', challenge_id=invitation.challenge.id)


@login_required
def reject_challenge_join_request(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id)
    if request.method == 'POST' and invitation.challenge.fitness_group.members.filter(id=request.user.id).exists():
        invitation.status = 'Rejected'
        invitation.save()
        return redirect('challenge_detail', challenge_id=invitation.challenge.id)

@login_required
def challenge_detail(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    participants_data = []

    for user in challenge.users.all():
        week_challenge_type_display = calculate_week_challenge_type_display(user, challenge)
        current_total_challenge_type_display = calculate_current_total_challenge_type_display(user, challenge)
        consecutive_activities_log_days = calculate_consecutive_activities_log_days(user, challenge)
        current_week_start = calculate_current_week_start(user, challenge)
        total_stars = calculate_total_stars(user, challenge)
        current_month_stars = calculate_month_stars(user, challenge, now().month)

        monthly_stars = {f'{month}_stars': calculate_month_stars(user, challenge, month) for month in range(1, 13)}

        participants_data.append({
            'username': user.username,
            'week_challenge_type_display': week_challenge_type_display,
            'current_total_challenge_type_display': current_total_challenge_type_display,
            'consecutive_activities_log_days': consecutive_activities_log_days,
            'current_week_start': current_week_start,
            'total_stars': total_stars,
            'current_month_stars': current_month_stars,
            **monthly_stars
        })

    return render(request, 'fitness/challenge_detail.html', {
        'challenge': challenge,
        'participants_data': participants_data,
    })

def calculate_month_stars(user, challenge, month):
    start_date = datetime(challenge.start_date.year, month, 1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    if is_naive(start_date):
        start_date = make_aware(start_date)
    if is_naive(end_date):
        end_date = make_aware(end_date)

    activities = FitnessActivity.objects.filter(user=user, date_time__range=[start_date, end_date])

    total_distance = activities.aggregate(Sum('distance'))['distance__sum'] or 0
    total_duration = activities.aggregate(Sum('duration'))['duration__sum'] or 0

    stars_from_distance = total_distance // 169
    stars_from_duration = (total_duration // 60) // 21

    total_stars = stars_from_distance + stars_from_duration

    return total_stars

def calculate_total_stars(user, challenge):
    start_date = datetime.combine(challenge.start_date, datetime.min.time())
    end_date = datetime.combine(challenge.end_date, datetime.min.time())

    if is_naive(start_date):
        start_date = make_aware(start_date)
    if is_naive(end_date):
        end_date = make_aware(end_date)

    activities = FitnessActivity.objects.filter(user=user, date_time__range=[start_date, end_date])

    total_distance = activities.aggregate(Sum('distance'))['distance__sum'] or 0
    total_duration = activities.aggregate(Sum('duration'))['duration__sum'] or 0

    stars_from_distance = total_distance // 169
    stars_from_duration = (total_duration // 60) // 21

    total_stars = stars_from_distance + stars_from_duration

    top_distance_user = FitnessActivity.objects.filter(date_time__range=[start_date, end_date]).values('user').annotate(total_distance=Sum('distance')).order_by('-total_distance').first()
    if top_distance_user and top_distance_user['user'] == user.id:
        total_stars += 1

    top_duration_user = FitnessActivity.objects.filter(date_time__range=[start_date, end_date]).values('user').annotate(total_duration=Sum('duration')).order_by('-total_duration').first()
    if top_duration_user and top_duration_user['user'] == user.id:
        total_stars += 1

    return total_stars

def calculate_week_challenge_type_display(user, challenge):
    one_week_ago = now() - timedelta(days=7)
    activities = FitnessActivity.objects.filter(user=user, date_time__gte=one_week_ago, date_time__lte=now())
    if challenge.challenge_type == 'CAL':
        total = activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    elif challenge.challenge_type == 'KM':
        total = activities.aggregate(Sum('distance'))['distance__sum'] or 0
    elif challenge.challenge_type == 'TSS':
        total = activities.aggregate(Sum('tss'))['tss__sum'] or 0
    else:
        total = 0
    return total

def calculate_current_total_challenge_type_display(user, challenge):
    activities = FitnessActivity.objects.filter(user=user, date_time__gte=challenge.start_date, date_time__lte=now())
    if challenge.challenge_type == 'CAL':
        total = activities.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
    elif challenge.challenge_type == 'KM':
        total = activities.aggregate(Sum('distance'))['distance__sum'] or 0
    elif challenge.challenge_type == 'TSS':
        total = activities.aggregate(Sum('tss'))['tss__sum'] or 0
    else:
        total = 0
    return total

def calculate_consecutive_activities_log_days(user, challenge):
    activities = FitnessActivity.objects.filter(user=user, date_time__gte=challenge.start_date, date_time__lte=now()).order_by('date_time')
    consecutive_days = 0
    current_streak = 0
    previous_date = None

    for activity in activities:
        if previous_date:
            if (activity.date_time.date() - previous_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
        else:
            current_streak = 1
        previous_date = activity.date_time.date()
        consecutive_days = max(consecutive_days, current_streak)

    return consecutive_days

def calculate_current_week_start(user, challenge):
    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())
    return start_of_week


def is_group_admin(user, group_id):
    group = FitnessGroup.objects.get(id=group_id)
    return user in group.admins.all()

@login_required
def delete_challenge(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    group_id = challenge.fitness_group.id

    if not is_group_admin(request.user, group_id):
        return redirect('group_detail', fitness_group_id=group_id)

    if request.method == 'POST':
        challenge.delete()
        return redirect('group_detail', fitness_group_id=group_id)
    return render(request, 'fitness/confirm_delete.html', {'challenge': challenge})

@login_required
def manage_admins(request, fitness_group_id):
    if not is_group_admin(request.user, fitness_group_id):
        return redirect('group_detail', fitness_group_id=fitness_group_id)

    group = get_object_or_404(FitnessGroup, id=fitness_group_id)
    if request.method == 'POST':
        form = FitnessGroupAdminForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_detail', fitness_group_id=group.id)
    else:
        form = FitnessGroupAdminForm(instance=group)
    return render(request, 'fitness/manage_admins.html', {'form': form, 'group': group})
