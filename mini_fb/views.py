from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView, DetailView
import random

# Create your views here.

class ShowAllView(ListView):
    '''Create a subclass of ListView to display all blog articles.'''

    model = Profile # retrieve objects of type Article from the database
    template_name = 'mini_fb/show_all.html'
    context_object_name = 'articles' # how to find the data in the template file