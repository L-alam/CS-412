from .models import Profile
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import random

# Create your views here.



class ShowAllProfilesView(ListView):
    """Show all Profiles on one page"""
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'

class ShowProfilePageView(DetailView):
    """Show one Profile on the page"""
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'