from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, FitnessActivity, WeightEntry, Group, Challenge, LeaderboardEntry, Invitation #,DietaryLog
from django.utils import timezone
from datetime import datetime
from django.forms.widgets import DateInput #DateInput to be able to use the little calendar :)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    date_of_birth = forms.DateField(help_text='Required. Format: YYYY-MM-DD', widget=forms.DateInput(attrs={'type': 'date'}),
                                    input_formats=['%Y-%m-%d'])
    
    height = forms.IntegerField(help_text='Height in centimeters')
    weight = forms.IntegerField(help_text='Weight in kilograms')
    fitness_level = forms.IntegerField(help_text='Fitness level from 1 to 10')

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
        fields = ['activity_type', 'duration', 'intensity', 'calories_burned', 'date_time']
        widgets = {
            'date_time': forms.DateInput(format='%d/%m/%Y', attrs={
                'type': 'date',
                'placeholder': 'dd/mm/yyyy'  # Placeholder
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_time'].initial = datetime.now().strftime('%Y-%m-%d')  # Default value as today
        self.fields['intensity'].label = 'Training Stress Score TSS' 




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


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['name', 'group', 'challenge_type', 'target_amount', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChallengeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = user.fitness_groups.all()

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['invite_type', 'group', 'challenge', 'invitee', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invitee'].queryset = User.objects.none()
        self.fields['challenge'].queryset = Challenge.objects.none()
        self.fields['group'].queryset = Group.objects.none()

        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                self.fields['invitee'].queryset = User.objects.filter(groups__id=group_id)
                self.fields['challenge'].queryset = Challenge.objects.filter(group_id=group_id)
            except (ValueError, TypeError):
                pass  # Handle empty data and invalid inputs

        elif self.instance.pk:
            if self.instance.invite_type == InviteType.CHALLENGE_INVITE:
                self.fields['invitee'].queryset = self.instance.group.members.all()
                self.fields['challenge'].queryset = self.instance.group.challenge_set.all()
            elif self.instance.invite_type == InviteType.GROUP_INVITE:
                self.fields['invitee'].queryset = self.instance.group.user_set.all()