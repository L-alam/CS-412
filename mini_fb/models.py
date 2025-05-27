from django.db import models

# Create your models here

class Profile(models.Model):
    '''Encapsulate the idea of an Facebook Profile Page'''
    
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.TextField(blank=False)
    pfp_url = models.URLField(blank=True)
    
def __str__(self):
    '''Return a string representation of this Profile object.'''
    return f'{self.title} by {self.author}'