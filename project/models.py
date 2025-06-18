from django.db import models

# Create your models here.

class Trip(models.Model):
    '''Data on potential Trips'''
    
    name = models.TextField(blank=False)
    location = models.TextField(blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    
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

    
    