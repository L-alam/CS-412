from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, View
from .models import *
from .forms import *
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.contrib import messages
from .flight_service import FlightSearchService
from .hotel_service import HotelSearchService
import json

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
        '''Set the user as organizer when creating a trip.'''
        response = super().form_valid(form)
        
        # Add the creator as an organizer of the trip
        self.object.add_member(self.request.user, role='organizer')
        
        return response
    
    def get_success_url(self):
        '''Redirect to the trip detail page after successful creation.'''
        return reverse('show_trip', kwargs={'pk': self.object.pk})



class ShowTripDetailView(DetailView):
    model = Trip
    template_name = 'project/show_trip.html'
    context_object_name = 'trip'
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to view this trip"""
        trip = self.get_object()
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        # Check if user is a member of the trip
        if not trip.is_member(request.user):
            messages.error(request, "You don't have permission to view this trip.")
            return redirect('show_all')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_organizer'] = self.object.members.filter(user=self.request.user, role='organizer').exists()
        context['flight_search_form'] = FlightSearchForm()
        context['hotel_search_form'] = HotelSearchForm()  # Add this line
        return context



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


class InviteFriendsView(DetailView):
    '''Show the invite friends page for a trip'''
    model = Trip
    template_name = 'project/invite_friends.html'
    context_object_name = 'trip'
    
    def get_login_url(self):
        return reverse('login')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user can invite friends (is a member of the trip)"""
        trip = self.get_object()
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.can_edit(request.user):
            messages.error(request, "You don't have permission to invite friends to this trip.")
            return redirect('show_trip', pk=trip.pk)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's profile to find their friends
        try:
            user_profile = self.request.user.trip_profile.first()
            if user_profile:
                # Get friends who aren't already members of this trip
                friends = user_profile.get_friends()
                current_member_users = [member.user for member in self.object.get_members()]
                available_friends = [friend for friend in friends if friend.user not in current_member_users]
                context['available_friends'] = available_friends
                context['user_profile'] = user_profile  # Add this to context
            else:
                context['available_friends'] = []
                context['user_profile'] = None
        except:
            context['available_friends'] = []
            context['user_profile'] = None
            
        return context



class AddTripMemberView(View):
    '''Add a friend to a trip as a member'''
    
    def get_login_url(self):
        return reverse('login')
    
    def post(self, request, trip_pk, user_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        user_to_add = get_object_or_404(User, pk=user_pk)
        
        # Check permissions
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.can_edit(request.user):
            messages.error(request, "You don't have permission to add members to this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        # Add the user as a member
        if not trip.is_member(user_to_add):
            trip.add_member(user_to_add, role='member')
            messages.success(request, f"Successfully added {user_to_add.username} to the trip!")
        else:
            messages.info(request, f"{user_to_add.username} is already a member of this trip.")
        
        return redirect('invite_friends', pk=trip.pk)



class RemoveTripMemberView(View):
    '''Remove a member from a trip'''
    
    def get_login_url(self):
        return reverse('login')
    
    def post(self, request, trip_pk, user_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        user_to_remove = get_object_or_404(User, pk=user_pk)
        
        # Check permissions
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.can_edit(request.user):
            messages.error(request, "You don't have permission to remove members from this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        # Don't allow removing the last organizer
        if trip.get_organizers().count() == 1:
            organizer = trip.get_organizers().first()
            if organizer.user == user_to_remove:
                messages.error(request, "Cannot remove the last organizer from the trip.")
                return redirect('show_trip', pk=trip.pk)
        
        # Remove the member
        trip_member = trip.members.filter(user=user_to_remove).first()
        if trip_member:
            trip_member.delete()
            messages.success(request, f"Removed {user_to_remove.username} from the trip.")
        else:
            messages.info(request, f"{user_to_remove.username} is not a member of this trip.")
        
        return redirect('show_trip', pk=trip.pk)



class FlightSearchView(View):
    '''AJAX view for searching flights within a trip'''
    
    def post(self, request, *args, **kwargs):
        '''Handle flight search requests'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        # Check if user has permission to view this trip
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Parse JSON data from request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Validate required fields
        required_fields = ['departure_city', 'arrival_city', 'departure_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        try:
            # Initialize flight search service
            flight_service = FlightSearchService()
            
            # Search for flights
            api_response = flight_service.search_flights(
                departure_city=data['departure_city'],
                arrival_city=data['arrival_city'],
                departure_date=data['departure_date'],
                return_date=data.get('return_date'),
                travel_class=data.get('travel_class', '1'),
                adults=data.get('adults', 1),
                page_token=data.get('page_token')
            )
            
            # Format results for frontend
            formatted_flights = flight_service.format_flight_results(api_response)
            
            # Get pagination info
            pagination = api_response.get('serpapi_pagination', {})
            
            response_data = {
                'flights': formatted_flights,
                'pagination': {
                    'current_from': pagination.get('current_from', 1),
                    'current_to': pagination.get('current_to', len(formatted_flights)),
                    'next_page_token': pagination.get('next_page_token'),
                    'has_next': bool(pagination.get('next_page_token'))
                },
                'search_params': {
                    'departure_city': data['departure_city'],
                    'arrival_city': data['arrival_city'],
                    'departure_date': data['departure_date'],
                    'return_date': data.get('return_date'),
                    'travel_class': data.get('travel_class', '1'),
                    'adults': data.get('adults', 1)
                }
            }
            
            return JsonResponse(response_data)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Flight search failed: {str(e)}'}, status=500)



class HotelSearchView(View):
    '''AJAX view for searching hotels within a trip'''
    
    def post(self, request, *args, **kwargs):
        '''Handle hotel search requests'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        # Check if user has permission to view this trip
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Parse JSON data from request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        # Validate required fields
        required_fields = ['city', 'check_in_date', 'check_out_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Validate dates
        try:
            from datetime import datetime
            check_in = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
            check_out = datetime.strptime(data['check_out_date'], '%Y-%m-%d')
            
            if check_out <= check_in:
                return JsonResponse({'error': 'Check-out date must be after check-in date'}, status=400)
                
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        try:
            # Initialize hotel search service
            hotel_service = HotelSearchService()
            
            # Search for hotels
            api_response = hotel_service.search_hotels(
                city=data['city'],
                check_in_date=data['check_in_date'],
                check_out_date=data['check_out_date'],
                adults=data.get('adults', 2),
                children=data.get('children', 0),
                page_token=data.get('page_token')
            )
            
            # Format results for frontend
            formatted_hotels = hotel_service.format_hotel_results(api_response)
            
            # Get pagination info
            pagination = api_response.get('serpapi_pagination', {})
            
            # Calculate nights for total price display
            nights = hotel_service._calculate_nights(data['check_in_date'], data['check_out_date'])
            
            response_data = {
                'hotels': formatted_hotels,
                'nights': nights,
                'pagination': {
                    'current_from': pagination.get('current_from', 1),
                    'current_to': pagination.get('current_to', len(formatted_hotels)),
                    'next_page_token': pagination.get('next_page_token'),
                    'has_next': bool(pagination.get('next_page_token'))
                },
                'search_params': {
                    'city': data['city'],
                    'check_in_date': data['check_in_date'],
                    'check_out_date': data['check_out_date'],
                    'adults': data.get('adults', 2),
                    'children': data.get('children', 0)
                }
            }
            
            return JsonResponse(response_data)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Hotel search failed: {str(e)}'}, status=500)


class AddFlightToListView(View):
    '''Add a flight to the trip's list'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        # Check permissions
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['title', 'departure_code', 'arrival_code', 'departure_time', 'arrival_time', 'duration_formatted', 'airline', 'price']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create the list item
            list_item = TripListItem.objects.create(
                trip=trip,
                added_by=request.user,
                item_type='flight',
                title=f"{data['departure_code']} → {data['arrival_code']}",
                description=f"{data['airline']} • {data['duration_formatted']} • {data.get('stops_text', 'Direct')}",
                price=data['price'],
                item_data={
                    'departure_code': data['departure_code'],
                    'arrival_code': data['arrival_code'],
                    'departure_time': data['departure_time'],
                    'arrival_time': data['arrival_time'],
                    'duration_formatted': data['duration_formatted'],
                    'airline': data['airline'],
                    'stops': data.get('stops', 0),
                    'booking_token': data.get('booking_token', ''),
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Flight added to list!',
                'item_id': list_item.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AddHotelToListView(View):
    '''Add a hotel to the trip's list'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        # Check permissions
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['name', 'rating', 'price_per_night', 'total_price']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create description with rating and amenities
            amenities_text = ', '.join(data.get('amenities', [])[:3])
            if len(data.get('amenities', [])) > 3:
                amenities_text += f" +{len(data['amenities']) - 3} more"
            
            description = f"★ {data['rating']} • {data.get('star_rating', 'N/A')} stars"
            if amenities_text:
                description += f" • {amenities_text}"
            
            # Create the list item
            list_item = TripListItem.objects.create(
                trip=trip,
                added_by=request.user,
                item_type='hotel',
                title=data['name'],
                description=description,
                price=data.get('total_price_value', data.get('price_per_night_value', 0)),
                item_data={
                    'name': data['name'],
                    'rating': data['rating'],
                    'star_rating': data.get('star_rating', 0),
                    'price_per_night': data['price_per_night'],
                    'price_per_night_value': data.get('price_per_night_value', 0),
                    'total_price': data['total_price'],
                    'total_price_value': data.get('total_price_value', 0),
                    'amenities': data.get('amenities', []),
                    'property_token': data.get('property_token', ''),
                    'reviews': data.get('reviews', 0),
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Hotel added to list!',
                'item_id': list_item.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AddCustomItemToListView(View):
    '''Add a custom item to the trip's list'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        # Check permissions
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            
            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)
            
            # Create the list item
            list_item = TripListItem.objects.create(
                trip=trip,
                added_by=request.user,
                item_type='custom',
                title=title,
                description=description,
                item_data={
                    'custom_title': title,
                    'custom_description': description,
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Item added to list!',
                'item_id': list_item.id,
                'item_html': self._render_list_item(list_item)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _render_list_item(self, item):
        '''Render HTML for a list item'''
        price_display = f"${item.price}" if item.price else ""
        
        if item.item_type == 'flight':
            icon = "✈️"
        elif item.item_type == 'hotel':
            icon = "🏨"
        else:
            icon = "📝"
        
        return f'''
        <div class="list-item saved-item" data-item-id="{item.id}">
            <div class="item-main">
                <div class="item-title">{icon} {item.title}</div>
                <div class="item-description">{item.description}</div>
                <small class="added-info">Added by {item.added_by.username} on {item.added_date.strftime('%b %d, %Y')}</small>
            </div>
            {f'<div class="item-price">{price_display}</div>' if price_display else ''}
            <div class="item-actions">
                <button class="btn-delete" onclick="removeListItem({item.id})">Delete</button>
            </div>
        </div>
        '''


class RemoveListItemView(View):
    '''Remove an item from the trip's list'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        item_id = kwargs.get('item_id')
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        list_item = get_object_or_404(TripListItem, id=item_id, trip=trip)
        
        # Check permissions
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Allow item creator or trip organizers to delete
        if list_item.added_by != request.user and not trip.is_organizer(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            list_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Item removed from list!'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



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