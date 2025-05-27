from django.urls import path
from .views import ShowAllView # our view class definition 

urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllView.as_view(), name='show_all'), # generic class-based view
]