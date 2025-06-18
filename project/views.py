from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView 
from .models import Trip

# Create your views here.

class ShowAllTrips(ListView):
    '''Create a subclass of ListView to display all possible trip destinations.'''

    model = Trip # retrieve objects of type Article from the database
    template_name = 'project/show_all.html'
    context_object_name = 'trips'




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