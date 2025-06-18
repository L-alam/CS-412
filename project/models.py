from django.db import models

# Create your models here.

class Trip(models.Model):
    '''Data on potential Trips'''
    
    name = models.TextField(blank=False)
    description = models.TextField(blank=False)  # Overall Trip Location
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(blank=True)
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('confirmed', 'Confirmed'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        '''Return a string representation of this Article object.'''
        return f'{self.name}'



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
    
    #plan selection
    is_selected = models.BooleanField(default=False)  # Mark the chosen plan
    
    # Optional for now
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f'{self.name} for {self.trip.name}'
    
    class Meta:
        ordering = ['-created_date']



class Destination(models.Model):
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="destinations")
    city = models.TextField(blank=False)
    country = models.TextField(blank=False)
    
    #Extra destination details
    arrival_date = models.DateTimeField(null=True, blank=True)
    departure_date = models.DateTimeField(null=True, blank=True)
    nights_staying = models.IntegerField(null=True, blank=True)
    
    #For multi-city trips
    order = models.IntegerField(default=1, help_text="Order of visit in this plan")
    
    # Optional details
    notes = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)