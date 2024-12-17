from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, FitnessActivity, WeightEntry, FitnessGroup, Challenge, LeaderboardEntry, Invitation, InviteType #,DietaryLog
from django.utils import timezone
from datetime import datetime
from django.forms.widgets import DateInput #DateInput to be able to use the little calendar :)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    date_of_birth = forms.DateField(help_text='Required. Format: YYYY-MM-DD', widget=forms.DateInput(attrs={'type': 'date'}),
                                    input_formats=['%Y-%m-%d'])

    height = forms.IntegerField(help_text='Height in centimeters')
    weight = forms.IntegerField(help_text='Weight in kilograms')
    fitness_level = forms.IntegerField(
        help_text='Fitness level from 1 to 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth', 'height', 'weight', 'fitness_level']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                height=self.cleaned_data['height'],
                weight=self.cleaned_data['weight'],
                fitness_level=self.cleaned_data['fitness_level']
            )
        return user


class ActivityForm(forms.ModelForm):
    class Meta:
        model = FitnessActivity
        fields = ['activity_type', 'duration', 'calories_burned', 'date_time', 'tss']
        widgets = {
            'date_time': forms.DateInput(format='%d/%m/%Y', attrs={
                'type': 'date',
                'placeholder': 'dd/mm/yyyy'  # Placeholder
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_time'].initial = datetime.now().strftime('%d-%m-%Y')  # Default value as today
        self.fields['tss'].label = 'Training Stress Score TSS'




# class DietaryLogForm(forms.ModelForm):
#     class Meta:
#         model = DietaryLog
#         fields = ['food_item', 'calories', 'carbs', 'proteins', 'fats', 'quantity', 'date_time']
#         widgets = {
#         'date_time': forms.DateInput(format='%d/%m/%y', attrs={'type': 'date'}),
#         }

class WeightEntryForm(forms.ModelForm):
    class Meta:
        model = WeightEntry
        fields = ['weight', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'max': timezone.now().date().isoformat()}),
        }


class FitnessGroupForm(forms.ModelForm):
    class Meta:
        model = FitnessGroup
        fields = ['name']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['name', 'fitness_group', 'challenge_type', 'target_amount', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChallengeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['fitness_group'].queryset = user.fitness_groups.all()

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['invite_type', 'fitness_group', 'challenge', 'invitee', 'message']

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        challenge = kwargs.pop('challenge', None)
        super().__init__(*args, **kwargs)

        self.fields['invitee'].queryset = User.objects.none()
        self.fields['challenge'].queryset = Challenge.objects.none()
        self.fields['invitee'].label = 'Select a user '

        if group:
            # Exclude users who are already members of the group
            self.fields['invitee'].queryset = User.objects.exclude(id__in=group.members.all())
            self.fields['challenge'].queryset = Challenge.objects.filter(fitness_group=group)

        if self.instance.pk:  # Edit case
            if self.instance.invite_type == InviteType.CHALLENGE_INVITE:
                self.fields['invitee'].queryset = User.objects.exclude(id__in=self.instance.challenge.users.all())
                self.fields['challenge'].queryset = Challenge.objects.filter(fitness_group=self.instance.fitness_group)
            elif self.instance.invite_type == InviteType.GROUP_INVITE:
                self.fields['invitee'].queryset = User.objects.exclude(id__in=self.instance.fitness_group.members.all())

    def clean(self):
        cleaned_data = super().clean()
        invite_type = cleaned_data.get('invite_type')
        fitness_group = cleaned_data.get('fitness_group')
        challenge = cleaned_data.get('challenge')
        invitee = cleaned_data.get('invitee')

        if invite_type == InviteType.CHALLENGE_INVITE and challenge:
            if not fitness_group.members.filter(id=invitee.id).exists():
                raise forms.ValidationError('The selected user is not a member of the group. A combined invite will be sent.')

        return cleaned_data