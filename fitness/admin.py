from django.contrib import admin
from .models import FitnessActivity, UserProfile, FitnessGroup, Challenge

# Register your models here.
class FitnessActivityAdmin(admin.ModelAdmin):
    # list_display = ('user', 'activity_type','duration')   
    #This get_list_display func is a way to not have to type all fields in the list display :)
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields] 

class UserProfileAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]         

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('user')

class FitnessGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members', 'created_at')
    
    def get_members(self, obj):
        return ", ".join([member.username for member in obj.members.all()])
    get_members.short_description = 'Members'

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fitness_group', 'challenge_type', 'target_amount', 'start_date', 'end_date', 'display_users')

    def display_users(self, obj):
        return ", ".join([user.username for user in obj.users.all()])

    display_users.short_description = 'Users'


# Register your models here.
admin.site.register(FitnessActivity, FitnessActivityAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
# admin.site.register(User, UserAdmin)
admin.site.register(FitnessGroup,FitnessGroupAdmin)
admin.site.register(Challenge,ChallengeAdmin)
