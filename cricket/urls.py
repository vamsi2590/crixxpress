from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    #home
    path('', views.home, name='home'),

    #matches
    path('live-matches/', views.live_matches, name='live_matches'),
    path('recent-matches/', views.recent_matches, name='recent_matches'),
    path('upcoming-matches/', views.upcoming_matches, name='upcoming_matches'),
    path('schedule/', views.schedule , name='schedule'),
    path('commentary/<int:match_id>/', views.commentary, name='commentary'),
    path('scorecard/<int:match_id>/' , views.scorecard, name='scorecard'),
    path('match_info/<int:match_id>/', views.match_info, name='match_info'),
    path('match/<int:match_id>/', views.match_details, name='match_details'),

    #news
    path('news/', views.news, name='news'),
    path('news/<int:story_id>/', views.news_detail, name='news_detail'),

    #players
    path('players/', views.players, name='players'),
    path('player/<int:player_id>/', views.player_info, name='player_info'),
    path('search-player/', views.search_player, name='search_player'),

    #rankings
    path('rankings/', views.default_ranking, name='default_ranking'),
    path('rankings/<str:format>/<str:category>/', views.player_ranking, name='player_ranking'),

    #teams
    path('teams/<str:team_type>/', views.teams, name='teams'),
    path('teams/', views.teams, name='teams'),
    path('team/<int:team_id>/', views.team_details, name='team_details'),

    #series
    path('series/', views.render_series_list, name='series_list'),
    path('series/<str:series_type>/', views.render_series_list, name='series_list_type'),
    path('series/<int:series_id>/matches/', views.render_series_detail, name='series_matches'),
    path('series/<int:series_id>/squads/', views.render_series_squads, name='series_squads'),
    path('series/<int:series_id>/squads/<int:squad_id>/players/', views.render_squad_players, name='squad_players'),

     # Authentication URLs
     path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url='/profile/'), name='password_change'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
