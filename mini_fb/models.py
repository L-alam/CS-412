from django.db import models
from django.urls import reverse

# Create your models here
class Profile(models.Model):
    '''Facebook Profile Page'''
    
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email = models.TextField(blank=False)
    pfp_url = models.URLField(blank=True)
    
    def __str__(self):
        '''String representation of Profile'''
        return f'{self.first_name} {self.last_name}'
    
    def get_absolute_url(self):
        '''Return  URL to display instance of this Profile.'''
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_status_messages(self):
        '''Return all status messages for this Profile'''
        status_messages = StatusMessage.objects.filter(profile=self).order_by('-timestamp')
        return status_messages


class StatusMessage(models.Model):
    '''Facebook status message.'''
    
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    
    def __str__(self):
        '''Return a string representation'''
        return f'{self.message}'