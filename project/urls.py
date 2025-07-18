# File: urls.py
# Author: Labeeb Alam (lalam@bu.edu), 6/26/2025

from django.urls import path
from .views import * 
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    # Main app
    path('', ShowAllTripsView.as_view(), name='show_all'),
    path('create_trip/', CreateTripView.as_view(), name='create_trip'),
    path('trip/<int:pk>/', ShowTripDetailView.as_view(), name='show_trip'),
    path('trip/<int:trip_pk>/create_plan/', CreatePlanView.as_view(), name='create_plan'),
    
    # Profile
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/add_wishlist/', AddWishlistItemView.as_view(), name='add_wishlist_item'),
    path('profile/<int:pk>/friend_suggestions/', FriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/<int:pk>/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/remove_friend/<int:other_pk>/', RemoveFriendView.as_view(), name='remove_friend'),
    path('profile/<int:pk>/remove_wishlist/<int:item_pk>/', RemoveWishlistItemView.as_view(), name='remove_wishlist_item'),
    
    #Trip member management
    path('trip/<int:pk>/invite_friends/', InviteFriendsView.as_view(), name='invite_friends'),
    path('trip/<int:trip_pk>/add_member/<int:user_pk>/', AddTripMemberView.as_view(), name='add_trip_member'),
    path('trip/<int:trip_pk>/remove_member/<int:user_pk>/', RemoveTripMemberView.as_view(), name='remove_trip_member'),
    
    # Trip management
    path('trip/<int:trip_pk>/change_status/', ChangeTripsStatusView.as_view(), name='change_trip_status'),
    path('trip/<int:trip_pk>/leave/', LeaveTripsView.as_view(), name='leave_trip'),
    path('trip/<int:trip_pk>/delete/', DeleteTripsView.as_view(), name='delete_trip'),
    path('trip/<int:trip_pk>/remove_friend/<int:friend_pk>/', RemoveFriendFromTripsView.as_view(), name='remove_friend_from_trip'),
    
    # Plan management
    path('trip/<int:trip_pk>/plan/<int:plan_pk>/delete/', DeletePlanView.as_view(), name='delete_plan'),
    
    # Search Flight + Hotel
    path('trip/<int:trip_pk>/search_flights/', FlightSearchView.as_view(), name='search_flights'),
    path('trip/<int:trip_pk>/search_hotels/', HotelSearchView.as_view(), name='search_hotels'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('logout_confirmation/', TemplateView.as_view(template_name='project/logged_out.html'), name='logout_confirmation'),
    
    #Trip List
    path('trip/<int:trip_pk>/add_flight_to_list/', AddFlightToListView.as_view(), name='add_flight_to_list'),
    path('trip/<int:trip_pk>/add_hotel_to_list/', AddHotelToListView.as_view(), name='add_hotel_to_list'),
    path('trip/<int:trip_pk>/add_custom_item/', AddCustomItemToListView.as_view(), name='add_custom_item'),
    path('trip/<int:trip_pk>/remove_list_item/<int:item_id>/', RemoveListItemView.as_view(), name='remove_list_item'),
    
    #Item List View
    path('trip/<int:trip_pk>/plan/<int:plan_pk>/list_items/', GetPlanListItemsView.as_view(), name='get_plan_list_items'),
]
