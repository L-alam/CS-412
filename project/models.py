from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Trip(models.Model):
    '''Data on potential Trips'''
    
    name = models.TextField(blank=False)
    description = models.TextField(blank=True)  # Description field
    start_date = models.DateField()
    end_date = models.DateField()
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('confirmed', 'Confirmed'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        '''Return a string representation of this Trip object.'''
        return f'{self.name}'

    def get_plans(self):
        '''Return all plans for this trip'''
        return self.plans.all()



class Profile(models.Model):
    # Make it nullable for now to handle existing data
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trip_profile', null=True, blank=True)
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    email = models.TextField(blank=False)
    
    def __str__(self):
        '''Return a string representation of this Profile.'''
        return f'{self.first_name} {self.last_name}'
    
    def get_friends(self):
        '''Return a list of all friends (Profile objects) for this Profile.'''
        friends_as_profile1 = Friend.objects.filter(profile1=self)
        friends_as_profile2 = Friend.objects.filter(profile2=self)
        
        friend_profiles = []
        
        for friend in friends_as_profile1:
            friend_profiles.append(friend.profile2)
        
        for friend in friends_as_profile2:
            friend_profiles.append(friend.profile1)
        
        return friend_profiles
    
    def add_friend(self, other):
        '''Add a friend relationship between self and other Profile.'''
        if self == other:
            return
        
        existing_friend = Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | 
            models.Q(profile1=other, profile2=self)
        ).first()
        
        if not existing_friend:
            Friend.objects.create(profile1=self, profile2=other)
    
    def get_friend_suggestions(self):
        '''Return a list of Profiles that could be friends.'''
        all_profiles = Profile.objects.all()
        
        current_friends = self.get_friends()
        
        suggestions = []
        for profile in all_profiles:
            if profile != self and profile not in current_friends:
                suggestions.append(profile)
        
        return suggestions
    
    def remove_friend(self, other):
        '''Remove a friend relationship between self and other Profile.'''
        Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | 
            models.Q(profile1=other, profile2=self)
        ).delete()
    

    
class Friend(models.Model):
    '''Represents a friendship between two profiles.'''
    
    profile1 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile2")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        '''Return a string representation of this Friend relationship.'''
        return f'{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}'
        


class Plan(models.Model):
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="plans")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField(blank=False, help_text="e.g., 'Option A', 'Beach Route', 'Budget Plan'")
    
    # Plan selection
    is_selected = models.BooleanField(default=False)  # Mark the chosen plan
    
    # Optional for now
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f'{self.name} for {self.trip.name}'
    
    def get_destinations(self):
        '''Return all destinations for this plan'''
        return self.destinations.all()
    
    class Meta:
        ordering = ['-created_date']


class Destination(models.Model):
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="destinations")
    city = models.TextField(blank=False)
    country = models.TextField(blank=False)
    
    # Extra destination details
    arrival_date = models.DateTimeField(null=True, blank=True)
    departure_date = models.DateTimeField(null=True, blank=True)
    nights_staying = models.IntegerField(null=True, blank=True)
    
    # For multi-city trips
    order = models.IntegerField(default=1, help_text="Order of visit in this plan")
    
    # Optional details
    notes = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f'{self.city} - {self.plan}'



class WishlistItem(models.Model):
    '''A place that a user wants to visit in their wishlist.'''
    
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="wishlist")
    destination_name = models.TextField(blank=False, help_text="e.g., 'Paris', 'Bali', 'Tokyo'")
    
    added_date = models.DateTimeField(auto_now_add=True)
    target_year = models.IntegerField(null=True, blank=True, help_text="Year you hope to visit")
    
    def __str__(self):
        return f'{self.destination_name}, - {self.profile.first_name}'
    
    class Meta:
        ordering = ['-added_date']


class Accommodation(models.Model):
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="accommodations")  # Fixed: changed from "destinations"
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    location = models.TextField()
    price_total = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField()
    booking_url = models.URLField(blank=True)
    
    def __str__(self):
        return f'{self.name} - {self.plan.trip.name}' 



class Expense(models.Model):
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="expenses")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField() 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.description} - ${self.amount}'


class Flight(models.Model):
    FLIGHT_TYPE_CHOICES = [
        ('outbound', 'Outbound'),
        ('return', 'Return'),
        ('connecting', 'Connecting'),
    ]
    
    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('premium_economy', 'Premium Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]
    
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="flights")
    suggested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    airline = models.TextField()
    flight_number = models.CharField(max_length=20)
    departure_airport = models.CharField(max_length=10) 
    arrival_airport = models.CharField(max_length=10)
    departure_city = models.TextField()
    arrival_city = models.TextField()
    
    def __str__(self):
        return f'{self.airline} {self.flight_number}: {self.departure_city} → {self.arrival_city}'
    
    # class Meta:
    #     ordering = ['departure_date']
