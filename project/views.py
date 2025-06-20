from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View
from .models import *
from .forms import CreateTripForm, CreatePlanForm, AddWishlistItemForm
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

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
    

class ShowProfilePageView(DetailView):
    """Show the current user's profile"""
    model = Profile
    template_name = 'project/show_profile.html'
    context_object_name = 'profile'
    


class AddWishlistItemView(CreateView):
    model = WishlistItem
    form_class = AddWishlistItemForm
    template_name = 'project/add_wishlist_item.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})



class FriendSuggestionsView(DetailView):
    '''Show friend suggestions for a profile.'''
    model = Profile
    template_name = 'project/friend_suggestions.html'
    context_object_name = 'profile'


class AddFriendView(View):
    '''A view to add a friend relationship between two profiles.'''
    
    def get(self, request, *args, **kwargs):
        '''Handle the add friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = get_object_or_404(Profile, pk=pk)
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        profile.add_friend(other_profile)
        
        # Redirect back to friend suggestions
        return redirect('friend_suggestions', pk=pk)


class RemoveFriendView(View):
    '''A view to remove a friend relationship between two profiles.'''
    
    def get(self, request, *args, **kwargs):
        '''Handle the remove friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = get_object_or_404(Profile, pk=pk)
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        profile.remove_friend(other_profile)
        
        return redirect('show_profile', pk=pk)

    




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