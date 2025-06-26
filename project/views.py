# File: views.py
# Author: Labeeb Alam (lalam@bu.edu), 6/26/2025
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

# ListView that displays all trips belonging to the current user on the main dashboard.
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
        return Trip.objects.all()


# CreateView for adding new trips to the database and automatically making the creator an organizer member
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
        
        self.object.add_member(self.request.user, role='organizer')
        
        return response
    
    def get_success_url(self):
        '''Redirect to the trip detail page after successful creation.'''
        return reverse('show_trip', kwargs={'pk': self.object.pk})


# DetailView that displays comprehensive trip information including plans, members, and search functionality with member access control
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
            
        if not trip.is_member(request.user):
            messages.error(request, "You don't have permission to view this trip.")
            return redirect('show_all')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_organizer'] = self.object.members.filter(user=self.request.user, role='organizer').exists()
        context['flight_search_form'] = FlightSearchForm()
        context['hotel_search_form'] = HotelSearchForm()
        
        context['STATUS_CHOICES'] = Trip.STATUS_CHOICES
        
        plans_with_items = []
        for plan in self.object.get_plans():
            plans_with_items.append({
                'plan': plan,
                'list_items': plan.get_list_items(),
                'flight_items': plan.get_flight_items(),
                'hotel_items': plan.get_hotel_items(),
                'custom_items': plan.get_custom_items(),
            })
        
        context['plans_with_items'] = plans_with_items
        context['selected_plan'] = self.object.get_plans().filter(is_selected=True).first()
        
        return context



# CreateView for creating new travel plans with destinations for a specific trip.
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
        trip = get_object_or_404(Trip, pk=self.kwargs['trip_pk'])
        form.instance.trip = trip
        form.instance.created_by = self.request.user
        
        response = super().form_valid(form)
        
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


# DetailView that displays a user's profile information including friends and wishlist items
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
        return super().dispatch(request, *args, **kwargs)
    

# CreateView for adding new destinations to a user's travel wishlist
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


# DetailView that shows suggested friends for the current user's profile
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


# View that handles adding friend relationships between two user profiles.
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
        
        return redirect('friend_suggestions', pk=pk)


# View that removes existing friend relationships between two user profiles.
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


# View that deletes wishlist items from a user's profile.
class RemoveWishlistItemView(View):
    '''A view to remove a wishlist item.'''
    
    def get_login_url(self):
        '''Return the URL for the login page.'''
        return reverse('login')
    
    def get(self, request, *args, **kwargs):
        '''Handle the remove wishlist item request.'''
        pk = self.kwargs.get('pk')  
        item_pk = self.kwargs.get('item_pk') 
        
        profile = get_object_or_404(Profile, pk=pk)
        wishlist_item = get_object_or_404(WishlistItem, pk=item_pk)
        
        if profile.user != request.user:
            return redirect('show_profile', pk=pk)
        
        if wishlist_item.profile != profile:
            return redirect('show_profile', pk=pk)
        
        wishlist_item.delete()
        
        return redirect('show_profile', pk=pk)


# CreateView that handles both user account creation and profile setup in a single form.
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

# DetailView that displays available friends who can be invited to join a specific trip.
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
        
        try:
            user_profile = self.request.user.trip_profile.first()
            if user_profile:
                friends = user_profile.get_friends()
                current_member_users = [member.user for member in self.object.get_members()]
                available_friends = [friend for friend in friends if friend.user not in current_member_users]
                context['available_friends'] = available_friends
                context['user_profile'] = user_profile  
            else:
                context['available_friends'] = []
                context['user_profile'] = None
        except:
            context['available_friends'] = []
            context['user_profile'] = None
            
        return context


# View that adds users as members to a trip with permission checking.
class AddTripMemberView(View):
    '''Add a friend to a trip as a member'''
    
    def get_login_url(self):
        return reverse('login')
    
    def post(self, request, trip_pk, user_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        user_to_add = get_object_or_404(User, pk=user_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.can_edit(request.user):
            messages.error(request, "You don't have permission to add members to this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        if not trip.is_member(user_to_add):
            trip.add_member(user_to_add, role='member')
            messages.success(request, f"Successfully added {user_to_add.username} to the trip!")
        else:
            messages.info(request, f"{user_to_add.username} is already a member of this trip.")
        
        return redirect('invite_friends', pk=trip.pk)


# View that removes members from a trip with organizer permission validation.
class RemoveTripMemberView(View):
    '''Remove a member from a trip'''
    
    def get_login_url(self):
        return reverse('login')
    
    def post(self, request, trip_pk, user_pk):
        trip = get_object_or_404(Trip, pk=trip_pk)
        user_to_remove = get_object_or_404(User, pk=user_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.can_edit(request.user):
            messages.error(request, "You don't have permission to remove members from this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        if trip.get_organizers().count() == 1:
            organizer = trip.get_organizers().first()
            if organizer.user == user_to_remove:
                messages.error(request, "Cannot remove the last organizer from the trip.")
                return redirect('show_trip', pk=trip.pk)
        
        trip_member = trip.members.filter(user=user_to_remove).first()
        if trip_member:
            trip_member.delete()
            messages.success(request, f"Removed {user_to_remove.username} from the trip.")
        else:
            messages.info(request, f"{user_to_remove.username} is not a member of this trip.")
        
        return redirect('show_trip', pk=trip.pk)


# view that handles flight search requests using the SerpAPI and returns formatted JSON results
class FlightSearchView(View):
    '''AJAX view for searching flights within a trip'''
    
    def post(self, request, *args, **kwargs):
        '''Handle flight search requests'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        required_fields = ['departure_city', 'arrival_city', 'departure_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        try:
            flight_service = FlightSearchService()
            
            api_response = flight_service.search_flights(
                departure_city=data['departure_city'],
                arrival_city=data['arrival_city'],
                departure_date=data['departure_date'],
                return_date=data.get('return_date'),
                travel_class=data.get('travel_class', '1'),
                adults=data.get('adults', 1),
                page_token=data.get('page_token')
            )
            
            formatted_flights = flight_service.format_flight_results(api_response)
            
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


# view that processes hotel search requests and returns formatted accommodation data via JSON
class HotelSearchView(View):
    '''AJAX view for searching hotels within a trip'''
    
    def post(self, request, *args, **kwargs):
        '''Handle hotel search requests'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        required_fields = ['city', 'check_in_date', 'check_out_date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        try:
            from datetime import datetime
            check_in = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
            check_out = datetime.strptime(data['check_out_date'], '%Y-%m-%d')
            
            if check_out <= check_in:
                return JsonResponse({'error': 'Check-out date must be after check-in date'}, status=400)
                
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        try:
            hotel_service = HotelSearchService()
            
            api_response = hotel_service.search_hotels(
                city=data['city'],
                check_in_date=data['check_in_date'],
                check_out_date=data['check_out_date'],
                adults=data.get('adults', 2),
                children=data.get('children', 0),
                page_token=data.get('page_token')
            )
            
            formatted_hotels = hotel_service.format_hotel_results(api_response)
            
            pagination = api_response.get('serpapi_pagination', {})
            
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


# view that saves selected flights to a specific trip plan's list
class AddFlightToListView(View):
    '''Add a flight to the trip's list for a specific plan'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            
            plan_id = data.get('plan_id')
            if not plan_id:
                return JsonResponse({'error': 'Plan ID is required'}, status=400)
            
            plan = get_object_or_404(Plan, pk=plan_id, trip=trip)
            
            required_fields = ['title', 'departure_code', 'arrival_code', 'departure_time', 'arrival_time', 'duration_formatted', 'airline', 'price']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            list_item = TripListItem.objects.create(
                trip=trip,
                plan=plan, 
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
                'message': f'Flight added to {plan.name}!',
                'item_id': list_item.id,
                'plan_id': plan.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# view that adds selected hotels to a specific trip plan's saved items list.
class AddHotelToListView(View):
    '''Add a hotel to the trip's list for a specific plan'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            print(f"Received hotel data: {data}")
            
            plan_id = data.get('plan_id')
            if not plan_id:
                return JsonResponse({'error': 'Plan ID is required'}, status=400)
            
            plan = get_object_or_404(Plan, pk=plan_id, trip=trip)
            
            name = data.get('name', 'Unknown Hotel')
            rating = data.get('rating', 0)
            star_rating = data.get('star_rating', 0)
            price_per_night = data.get('price_per_night', 'N/A')
            price_per_night_value = data.get('price_per_night_value', 0)
            total_price = data.get('total_price', 'N/A')
            total_price_value = data.get('total_price_value', 0)
            amenities = data.get('amenities', [])
            property_token = data.get('property_token', '')
            reviews = data.get('reviews', 0)
            
            amenities_text = ', '.join(amenities[:3])
            if len(amenities) > 3:
                amenities_text += f" +{len(amenities) - 3} more"
            
            description = f"★ {rating} • {star_rating} stars"
            if amenities_text:
                description += f" • {amenities_text}"
            
            price_to_store = total_price_value if total_price_value > 0 else price_per_night_value
            
            list_item = TripListItem.objects.create(
                trip=trip,
                plan=plan, 
                added_by=request.user,
                item_type='hotel',
                title=name,
                description=description,
                price=price_to_store,
                item_data={
                    'name': name,
                    'rating': rating,
                    'star_rating': star_rating,
                    'price_per_night': price_per_night,
                    'price_per_night_value': price_per_night_value,
                    'total_price': total_price,
                    'total_price_value': total_price_value,
                    'amenities': amenities,
                    'property_token': property_token,
                    'reviews': reviews,
                }
            )
            
            print(f"Successfully created hotel list item: {list_item.id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Hotel added to {plan.name}!',
                'item_id': list_item.id,
                'plan_id': plan.id
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error creating hotel list item: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
        

# view that creates custom list items for trip plans with user-defined titles and prices
class AddCustomItemToListView(View):
    '''Add a custom item to the trip's list for a specific plan'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            data = json.loads(request.body)
            print(f"Received custom item data: {data}")
            
            plan_id = data.get('plan_id')
            if not plan_id:
                return JsonResponse({'error': 'Plan ID is required'}, status=400)
            
            plan = get_object_or_404(Plan, pk=plan_id, trip=trip)
            
            title = data.get('title', '').strip()
            price = data.get('price')
            
            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)
            
            price_value = None
            if price is not None and price != '':
                try:
                    price_value = float(price)
                    if price_value < 0:
                        return JsonResponse({'error': 'Price cannot be negative'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Invalid price format'}, status=400)
            
            list_item = TripListItem.objects.create(
                trip=trip,
                plan=plan,
                added_by=request.user,
                item_type='custom',
                title=title,
                description='',
                price=price_value,
                item_data={
                    'custom_title': title,
                    'custom_price': price_value,
                }
            )
            
            print(f"Successfully created custom list item: {list_item.id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Item added to {plan.name}!',
                'item_id': list_item.id,
                'plan_id': plan.id
            })
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error creating custom list item: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)
        
    
# view that deletes items from trip plan lists with proper permission checking
class RemoveListItemView(View):
    '''Remove an item from the trip's list'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        item_id = kwargs.get('item_id')
        
        print(f"Remove request: trip_pk={trip_pk}, item_id={item_id}") 
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        list_item = get_object_or_404(TripListItem, id=item_id, trip=trip)
        
        print(f"Found item: {list_item.title}")
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied - not a trip member'}, status=403)
        
        if list_item.added_by != request.user and not trip.is_organizer(request.user):
            return JsonResponse({'error': 'Permission denied - not item creator or organizer'}, status=403)
        
        try:
            list_item.delete()
            print(f"Successfully deleted item {item_id}")
            return JsonResponse({
                'success': True,
                'message': 'Item removed from list!'
            })
        except Exception as e:
            print(f"Error deleting item: {e}") 
            return JsonResponse({'error': str(e)}, status=500)


# view that retrieves and returns all list items for a specific trip plan.
class GetPlanListItemsView(View):
    '''Get list items for a specific plan via AJAX'''
    
    def get(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        plan_pk = kwargs.get('plan_pk')
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        plan = get_object_or_404(Plan, pk=plan_pk, trip=trip)
        
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        if not trip.is_member(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        try:
            list_items = []
            for item in plan.get_list_items():
                list_items.append({
                    'id': item.id,
                    'item_type': item.item_type,
                    'title': item.title,
                    'description': item.description,
                    'price': str(item.price) if item.price else None,
                    'added_by': item.added_by.username,
                    'added_date': item.added_date.strftime('%b %j, %Y'),
                    'can_delete': item.added_by == request.user or trip.is_organizer(request.user)
                })
            
            return JsonResponse({
                'success': True,
                'plan_id': plan.id,
                'plan_name': plan.name,
                'items': list_items
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

# View that allows trip organizers to update the status of their trips.
class ChangeTripsStatusView(View):
    '''Change the status of a trip'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_organizer(request.user):
            messages.error(request, "Only organizers can change trip status.")
            return redirect('show_trip', pk=trip.pk)
        
        new_status = request.POST.get('status')
        if new_status not in [choice[0] for choice in Trip.STATUS_CHOICES]:
            messages.error(request, "Invalid status selected.")
            return redirect('show_trip', pk=trip.pk)
        
        trip.status = new_status
        trip.save()
        
        messages.success(request, f"Trip status changed to {trip.get_status_display()}.")
        return redirect('show_trip', pk=trip.pk)
    

# View that removes the current user from a trip membership.
class LeaveTripsView(View):
    '''Remove yourself from a trip'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_member(request.user):
            messages.error(request, "You are not a member of this trip.")
            return redirect('show_all')
        
        if trip.is_organizer(request.user) and trip.get_organizers().count() == 1:
            messages.error(request, "You cannot leave the trip as you are the only organizer. Please make someone else an organizer first or delete the trip.")
            return redirect('show_trip', pk=trip.pk)
        
        trip_member = trip.members.filter(user=request.user).first()
        if trip_member:
            trip_member.delete()
            messages.success(request, f"You have left the trip '{trip.name}'.")
        
        return redirect('show_all')
    

# View that completely deletes a trip and all associated data with organizer permission required.
class DeleteTripsView(View):
    '''Delete a trip completely'''
    
    def get(self, request, *args, **kwargs):
        '''Show confirmation page'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_organizer(request.user):
            messages.error(request, "Only organizers can delete trips.")
            return redirect('show_trip', pk=trip.pk)
        
        return render(request, 'project/delete_trip_confirm.html', {'trip': trip})
    
    def post(self, request, *args, **kwargs):
        '''Actually delete the trip'''
        trip_pk = kwargs.get('trip_pk')
        trip = get_object_or_404(Trip, pk=trip_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_organizer(request.user):
            messages.error(request, "Only organizers can delete trips.")
            return redirect('show_trip', pk=trip.pk)
        
        trip_name = trip.name
        trip.delete()
        
        messages.success(request, f"Trip '{trip_name}' has been deleted.")
        return redirect('show_all')


# View that removes specific friends from trip membership with organizer permissions.
class RemoveFriendFromTripsView(View):
    '''Remove a friend from a trip (similar to RemoveTripMemberView but with friend context)'''
    
    def post(self, request, *args, **kwargs):
        trip_pk = kwargs.get('trip_pk')
        friend_pk = kwargs.get('friend_pk')
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        friend_profile = get_object_or_404(Profile, pk=friend_pk)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_organizer(request.user):
            messages.error(request, "Only organizers can remove members from trips.")
            return redirect('show_trip', pk=trip.pk)
        
        if trip.get_organizers().count() == 1:
            organizer = trip.get_organizers().first()
            if organizer.user == friend_profile.user:
                messages.error(request, "Cannot remove the last organizer from the trip.")
                return redirect('show_trip', pk=trip.pk)
        
        trip_member = trip.members.filter(user=friend_profile.user).first()
        if trip_member:
            trip_member.delete()
            messages.success(request, f"Removed {friend_profile.first_name} {friend_profile.last_name} from the trip.")
        else:
            messages.info(request, f"{friend_profile.first_name} {friend_profile.last_name} is not a member of this trip.")
        
        return redirect('show_trip', pk=trip.pk)


# View that deletes travel plans from trips with creator or organizer permission validation.
class DeletePlanView(View):
    '''Delete a plan from a trip'''
    
    def get(self, request, *args, **kwargs):
        '''Show confirmation page'''
        trip_pk = kwargs.get('trip_pk')
        plan_pk = kwargs.get('plan_pk')
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        plan = get_object_or_404(Plan, pk=plan_pk, trip=trip)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_member(request.user):
            messages.error(request, "You don't have permission to delete plans from this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        if plan.created_by != request.user and not trip.is_organizer(request.user):
            messages.error(request, "You can only delete plans you created, or you must be an organizer.")
            return redirect('show_trip', pk=trip.pk)
        
        return render(request, 'project/delete_plan_confirm.html', {
            'trip': trip,
            'plan': plan
        })
    
    def post(self, request, *args, **kwargs):
        '''Actually delete the plan'''
        trip_pk = kwargs.get('trip_pk')
        plan_pk = kwargs.get('plan_pk')
        
        trip = get_object_or_404(Trip, pk=trip_pk)
        plan = get_object_or_404(Plan, pk=plan_pk, trip=trip)
        
        if not request.user.is_authenticated:
            return redirect('login')
            
        if not trip.is_member(request.user):
            messages.error(request, "You don't have permission to delete plans from this trip.")
            return redirect('show_trip', pk=trip.pk)
        
        if plan.created_by != request.user and not trip.is_organizer(request.user):
            messages.error(request, "You can only delete plans you created, or you must be an organizer.")
            return redirect('show_trip', pk=trip.pk)
        
        plan_name = plan.name
        plan.delete()
        
        messages.success(request, f"Plan '{plan_name}' has been deleted.")
        return redirect('show_trip', pk=trip.pk)
    
