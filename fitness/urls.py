from django.urls import path
from django.contrib.auth.views import LoginView
from .views import add_activity, custom_logout, profile, create_group, group_list, create_challenge, challenge_list, weight_tracker, challenge_list, create_challenge, edit_challenge, send_invitation, invitations_list, respond_invitation, group_detail#,,add_diet_log
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('activities/', views.activity_list, name='activity_list'),
    # path('diet/', views.diet_log, name='diet_log'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='fitness/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('activities/add/', add_activity, name='add_activity'),
    # path('diet/add/', add_diet_log, name='add_diet_log'),
    path('weight/', views.weight_tracker, name='weight_tracker'),
    path('profile/', profile, name='profile'),
    path('create_group/', views.create_group, name='create_group'),
    path('fitness_groups/', group_list, name='group_list'),
    path('invitations/<int:invitation_id>/respond/<str:response>/', views.respond_invitation, name='respond_invitation'),
    path('groups/<int:fitness_group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:fitness_group_id>/invite/', views.send_invitation, name='send_group_invitation'),
    path('challenges/<int:challenge_id>/invite/', views.send_invitation, name='send_challenge_invitation'),
    path('invitations/', invitations_list, name='invitations_list'),
    path('create_invitation/', views.create_invitation, name='create_invitation'),
    path('invitation/<int:invitation_id>/approve/', views.approve_join_request, name='approve_join_request'),
    path('invitation/<int:invitation_id>/reject/', views.reject_join_request, name='reject_join_request'),
    path('get_group_users/<int:fitness_group_id>/', views.get_group_users, name='get_group_users'),
    path('group/<int:fitness_group_id>/toggle_visibility/', views.toggle_group_visibility, name='toggle_group_visibility'),
    path('group/<int:fitness_group_id>/request_to_join/', views.request_to_join_group, name='request_to_join_group'),
    path('activity/<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('challenges/', challenge_list, name='challenge_list'),
    path('challenges/create/', create_challenge, name='create_challenge'),
    path('challenges/edit/<int:pk>/', edit_challenge, name='edit_challenge'),
    path('challenge/<int:challenge_id>/request-to-join/', views.request_to_join_challenge, name='request_to_join_challenge'),
    path('challenge/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('invitation/<int:invitation_id>/approve-challenge/', views.approve_challenge_join_request, name='approve_challenge_join_request'),
    path('invitation/<int:invitation_id>/reject-challenge/', views.reject_challenge_join_request, name='reject_challenge_join_request'),
]