from django.urls import path
from .views import *

urlpatterns = [
    path('', ShowAllTripsView.as_view(), name='show_all'),
    path('create_trip/', CreateTripView.as_view(), name='create_trip'),
    path('trip/<int:pk>/', ShowTripDetailView.as_view(), name='show_trip'),
    path('trip/<int:trip_pk>/create_plan/', CreatePlanView.as_view(), name='create_plan'),
    path('profile/<int:pk>/', ShowProfilePageView.as_view(), name='show_profile'),
    path('profile/<int:pk>/add_wishlist/', AddWishlistItemView.as_view(), name='add_wishlist_item'),
    path('profile/<int:pk>/friend_suggestions/', FriendSuggestionsView.as_view(), name='friend_suggestions'),
    path('profile/<int:pk>/add_friend/<int:other_pk>/', AddFriendView.as_view(), name='add_friend'),
    path('profile/<int:pk>/remove_friend/<int:other_pk>/', RemoveFriendView.as_view(), name='remove_friend'),
    path('profile/<int:pk>/remove_wishlist/<int:item_pk>/', RemoveWishlistItemView.as_view(), name='remove_wishlist_item'),
]

