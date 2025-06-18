from django.urls import path
from .views import *

urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllTripsView.as_view(), name='show_all'), # generic class-based view
    path('create_trip/', CreateTripView.as_view(), name='create_trip'),
    path('trip/<int:pk>/', ShowTripDetailView.as_view(), name='show_trip'),
]