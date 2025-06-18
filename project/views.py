from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView 
from .models import Trip
from .forms import CreateTripForm
from django.urls import reverse

# Create your views here.

class ShowAllTripsView(ListView):
    '''Create a subclass of ListView to display all possible trip destinations.'''

    model = Trip # retrieve objects of type Article from the database
    template_name = 'project/show_all.html'
    context_object_name = 'trips'

class CreateTripView(CreateView):
    '''Create a new Trip and save it to the database.'''
    model = Trip
    template_name = 'project/create_trip_form.html'
    form_class = CreateTripForm
    
    def get_success_url(self):
        '''Redirect to the show_all page after successful creation.'''
        return reverse('show_all')


class ShowTripDetailView(DetailView):
    model = Trip
    template_name = 'project/show_trip.html'
    context_object_name = 'trip'




# {% extends 'project/base.html' %}

# {% block content %}
# <div class="page-header">
#     <h1>Your New Page</h1>
# </div>

# <div class="card">
#     <div class="card-body">
#         <p>Your content here with automatic styling!</p>
#         <a href="#" class="btn btn-primary">Action Button</a>
#     </div>
# </div>
# {% endblock %}