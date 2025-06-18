from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView 
from .models import *
from .forms import CreateTripForm, CreatePlanForm
from django.urls import reverse
from django.shortcuts import get_object_or_404

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


class CreatePlanView(CreateView):
    model = Plan
    template_name = 'project/create_plan_form.html'
    form_class = CreatePlanForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trip'] = get_object_or_404(Trip, pk=self.kwargs['trip_pk'])
        return context
    
    def form_valid(self, form):
        # Set the trip before saving
        trip = get_object_or_404(Trip, pk=self.kwargs['trip_pk'])
        form.instance.trip = trip
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('show_trip', kwargs={'pk': self.kwargs['trip_pk']})
    




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