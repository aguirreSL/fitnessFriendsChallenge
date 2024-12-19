from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, FitnessActivity, WeightEntry, FitnessGroup, Challenge, Invitation #,DietaryLog
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from datetime import datetime
from django.forms.widgets import DateInput #DateInput to be able to use the little calendar :)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    date_of_birth = forms.DateField(help_text='Required. Format: DD-MM-YYYY', widget=forms.DateInput(attrs={'type': 'date'}),
                                    input_formats=['%d-%m-%Y'])
    height = forms.IntegerField(help_text='Height in centimeters')
    weight = forms.IntegerField(help_text='Weight in kilograms')
    fitness_level = forms.IntegerField(
        help_text='Fitness level from 1 to 10',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    bio = forms.CharField(widget=forms.Textarea, required=False, help_text='Tell us a bit about yourself.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth', 'height', 'weight', 'fitness_level', 'first_name', 'last_name', 'bio']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                height=self.cleaned_data['height'],
                weight=self.cleaned_data['weight'],
                fitness_level=self.cleaned_data['fitness_level'],
                bio=self.cleaned_data['bio']
            )
        return user


class ActivityForm(forms.ModelForm):
    class Meta:
        model = FitnessActivity
        fields = ['activity_type', 'duration', 'calories_burned', 'date_time', 'tss', 'distance', 'perceived_effort']
        widgets = {
            'date_time': forms.DateInput(format='%d/%m/%Y', attrs={
                'type': 'date',
                'placeholder': 'dd/mm/yyyy'  # Placeholder
            }),
            'perceived_effort': forms.NumberInput(attrs={'min': 1, 'max': 10})  # Ensure it's between 1 and 10
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_time'].initial = datetime.now().strftime('%d-%m-%Y')  # Default value as today
        self.fields['tss'].label = 'Training Stress Score (TSS)'

    def clean_date_time(self):
        date_time = self.cleaned_data['date_time']
        if is_naive(date_time):
            return make_aware(date_time)
        return date_time


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
        fields = ['name', 'description', 'fitness_group', 'challenge_type', 'target_amount', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        challenge = self.instance
        placeholder_text = (
            f"The participants aim for {challenge.target_amount} amount of "
            f"{challenge.get_challenge_type_display()} combined. "
            f"The timeframe is from {challenge.start_date} to {challenge.end_date}."
        )
        self.placeholder_text = placeholder_text  # Store the placeholder text for later use

        if not self.instance.pk and not self.fields['description'].initial:
            self.fields['description'].initial = placeholder_text
        self.fields['description'].widget.attrs['placeholder'] = placeholder_text

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description == self.placeholder_text:
            return ''  # Return an empty string if the description is the same as the placeholder
        return description

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

        if challenge:
            self.fields['challenge'].initial = challenge
            self.fields['invitee'].queryset = User.objects.exclude(id__in=challenge.users.all())

        if self.instance.pk:  # Edit case
            if self.instance.invite_type == 'challenge':
                self.fields['invitee'].queryset = User.objects.exclude(id__in=self.instance.challenge.users.all())
                self.fields['challenge'].queryset = Challenge.objects.filter(fitness_group=self.instance.fitness_group)
            elif self.instance.invite_type == 'fitnessGroup':
                self.fields['invitee'].queryset = User.objects.exclude(id__in=self.instance.fitness_group.members.all())

    def clean(self):
        cleaned_data = super().clean()
        invite_type = cleaned_data.get('invite_type')
        fitness_group = cleaned_data.get('fitness_group')
        challenge = cleaned_data.get('challenge')
        invitee = cleaned_data.get('invitee')

        if invite_type == 'challenge' and challenge:
            if not fitness_group.members.filter(id=invitee.id).exists():
                raise forms.ValidationError('The selected user is not a member of the group. A combined invite will be sent.')

        return cleaned_data

class FitnessGroupAdminForm(forms.ModelForm):
    class Meta:
        model = FitnessGroup
        fields = ['admins']
        widgets = {
            'admins': forms.CheckboxSelectMultiple,
        }
