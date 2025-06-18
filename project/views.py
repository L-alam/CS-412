from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView 
from .models import Trip

# Create your views here.

class ShowAllTrips(ListView):
    '''Create a subclass of ListView to display all possible trip destinations.'''

    model = Trip # retrieve objects of type Article from the database
    template_name = 'project/show_all.html'
    context_object_name = 'trips'