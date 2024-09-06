from django.urls import path
from django.contrib.auth.views import LoginView
from .views import add_activity, custom_logout, profile, create_group, group_list, create_challenge, challenge_list, weight_tracker#,add_diet_log
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
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:group_id>/invite/', views.send_invitation, name='send_invitation'),
    path('invitations/<int:invitation_id>/respond/<str:response>/', views.respond_invitation, name='respond_invitation'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    ]
