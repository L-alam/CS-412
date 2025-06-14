from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView  # Add this import

urlpatterns = [
    path('', views.ShowAllProfilesView.as_view(), name='show_all_profiles'),
    path('profile/<int:pk>', views.ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile', views.CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', views.CreateStatusMessageView.as_view(), name='create_status'),
    path('profile/<int:pk>/update', views.UpdateProfileView.as_view(), name='update_profile'),
    path('status/<int:pk>/update', views.UpdateStatusMessageView.as_view(), name='update_status'),
    path('status/<int:pk>/delete', views.DeleteStatusMessageView.as_view(), name='delete_status'),
    path('profile/<int:pk>/add_friend/<int:other_pk>', views.AddFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/friend_suggestions', views.ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/<int:pk>/news_feed', views.ShowNewsFeedView.as_view(), name='news_feed'),
    
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('logout_confirmation/', TemplateView.as_view(template_name='mini_fb/logged_out.html'), name='logout_confirmation'),
]