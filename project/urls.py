from django.urls import path
from .views import ShowAllTrips

urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllTrips.as_view(), name='show_all'), # generic class-based view
]