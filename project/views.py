from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View
from .models import *
from .forms import CreateTripForm, CreatePlanForm, AddWishlistItemForm
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.

class ShowAllTripsView(ListView):
    '''Create a subclass of ListView to display all possible trip destinations.'''

    model = Trip
    template_name = 'project/show_all.html'
    context_object_name = 'trips'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get_queryset(self):
        '''Return trips that belong to the logged-in user.'''
        # For now, return all trips. You might want to filter by user later
        return Trip.objects.all()



class CreateTripView(CreateView):
    '''Create a new Trip and save it to the database.'''
    model = Trip
    template_name = 'project/create_trip_form.html'
    form_class = CreateTripForm
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def form_valid(self, form):
        '''Set the user before saving if you add a user field to Trip model.'''
        # form.instance.created_by = self.request.user  # Uncomment if you add this field
        return super().form_valid(form)
    
    def get_success_url(self):
        '''Redirect to the show_all page after successful creation.'''
        return reverse('show_all')



class ShowTripDetailView(DetailView):
    model = Trip
    template_name = 'project/show_trip.html'
    context_object_name = 'trip'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')



class CreatePlanView(CreateView):
    model = Plan
    template_name = 'project/create_plan_form.html'
    form_class = CreatePlanForm
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trip'] = get_object_or_404(Trip, pk=self.kwargs['trip_pk'])
        return context
    
    def form_valid(self, form):
        # Set the trip and user before saving
        trip = get_object_or_404(Trip, pk=self.kwargs['trip_pk'])
        form.instance.trip = trip
        form.instance.created_by = self.request.user
        
        # Handle destinations from the form
        response = super().form_valid(form)
        
        # Process destination data from POST
        plan = form.instance
        destination_count = 1
        
        while f'destination_city_{destination_count}' in self.request.POST:
            city = self.request.POST.get(f'destination_city_{destination_count}')
            country = self.request.POST.get(f'destination_country_{destination_count}')
            notes = self.request.POST.get(f'destination_notes_{destination_count}', '')
            
            if city and country:
                Destination.objects.create(
                    plan=plan,
                    city=city,
                    country=country,
                    notes=notes,
                    order=destination_count
                )
            
            destination_count += 1
        
        return response
    
    def get_success_url(self):
        return reverse('show_trip', kwargs={'pk': self.kwargs['trip_pk']})



class ShowProfilePageView(DetailView):
    """Show the current user's profile"""
    model = Profile
    template_name = 'project/show_profile.html'
    context_object_name = 'profile'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only view their own profile or make it accessible to all"""
        # For now, allow viewing any profile. You might want to restrict this later
        return super().dispatch(request, *args, **kwargs)
    


class AddWishlistItemView(CreateView):
    model = WishlistItem
    form_class = AddWishlistItemForm
    template_name = 'project/add_wishlist_item.html'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only add wishlist items to their own profile"""
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        
        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)
        return super().dispatch(request, *args, **kwargs)
    
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
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can only view friend suggestions for their own profile"""
        profile = get_object_or_404(Profile, pk=self.kwargs.get('pk'))

        if profile.user != request.user:
            return redirect('show_profile', pk=profile.pk)
        return super().dispatch(request, *args, **kwargs)



class AddFriendView(View):
    '''A view to add a friend relationship between two profiles.'''
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get(self, request, *args, **kwargs):
        '''Handle the add friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = get_object_or_404(Profile, pk=pk)
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        if profile.user != request.user:
            return redirect('show_profile', pk=pk)
        
        profile.add_friend(other_profile)
        
        # Redirect back to friend suggestions
        return redirect('friend_suggestions', pk=pk)



class RemoveFriendView(View):
    '''A view to remove a friend relationship between two profiles.'''
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get(self, request, *args, **kwargs):
        '''Handle the remove friend request.'''
        pk = self.kwargs.get('pk')
        other_pk = self.kwargs.get('other_pk')
        
        profile = get_object_or_404(Profile, pk=pk)
        other_profile = get_object_or_404(Profile, pk=other_pk)
        
        if profile.user != request.user:
            return redirect('show_profile', pk=pk)
        
        profile.remove_friend(other_profile)
        
        return redirect('show_profile', pk=pk)

class RemoveWishlistItemView(View):
    '''A view to remove a wishlist item.'''
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get(self, request, *args, **kwargs):
        '''Handle the remove wishlist item request.'''
        pk = self.kwargs.get('pk')  # profile pk
        item_pk = self.kwargs.get('item_pk')  # wishlist item pk
        
        profile = get_object_or_404(Profile, pk=pk)
        wishlist_item = get_object_or_404(WishlistItem, pk=item_pk)
        
        # Add check here if you add user field to Profile model
        if profile.user != request.user:
            return redirect('show_profile', pk=pk)
        
        # Ensure the wishlist item belongs to this profile
        if wishlist_item.profile != profile:
            return redirect('show_profile', pk=pk)
        
        wishlist_item.delete()
        
        return redirect('show_profile', pk=pk)



class CreateProfileView(CreateView):
    '''Create a new Profile and save it to the db.'''
    
    form_class = CreateProfileForm
    template_name = "project/create_profile_form.html"
    
    def get_context_data(self, **kwargs):
        """Add the user creation form to the context"""
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()
        return context
    
    def form_valid(self, form):
        """Process both the UserCreationForm and CreateProfileForm"""
        user_form = UserCreationForm(self.request.POST)
        
        if user_form.is_valid():
            user = user_form.save()
            
            login(self.request, user)
            
            form.instance.user = user  
            
            return super().form_valid(form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, user_form=user_form)
            )
    
    def get_success_url(self):
        return reverse('show_all')

    




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