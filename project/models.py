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
    trip = models.ForeignKey("Trip", on_delete=models.CASCADE, related_name="trip_plan")



class Destination(models.Model):
    plan = models.ForeignKey("Plan", on_delete=models.CASCADE, related_name="destination")
    city = models.TextField(blank=False)
    country = models.TextField(blank=False)
    
    
    