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
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    email =  models.TextField(blank=False)
    
    def __str__(self):
        '''Return a string representation of this Profile.'''
        return  f'{self.first_name} {self.last_name}'


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
        return f'{self.city}, {self.country}'