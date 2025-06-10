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
    
    def get_news_feed(self):
        '''Return a news feed of status messages from self and friends.'''
        own_messages = StatusMessage.objects.filter(profile=self)
        
        friends = self.get_friends()
        friends_messages = StatusMessage.objects.filter(profile__in=friends)
        
        news_feed = own_messages | friends_messages
        return news_feed.order_by('-timestamp')


class StatusMessage(models.Model):
    '''Facebook status message.'''
    
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=False)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    
    def __str__(self):
        '''Return a string representation'''
        return f'{self.message}'
    
    def get_images(self):
        '''Return all images associated with this StatusMessage.'''
        status_images = StatusImage.objects.filter(status_message=self)
        images = [si.image for si in status_images]
        return images


class Image(models.Model):
    '''An image file uploaded by a user.'''
    
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    image_file = models.ImageField(blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True)
    
    def __str__(self):
        '''Return a string representation of this Image.'''
        return f'Image uploaded by {self.profile} at {self.timestamp}'


class StatusImage(models.Model):
    '''Relationship between StatusMessage and Image.'''
    
    status_message = models.ForeignKey("StatusMessage", on_delete=models.CASCADE)
    image = models.ForeignKey("Image", on_delete=models.CASCADE)
    
    def __str__(self):
        '''Return a string representation.'''
        return f'Image {self.image.pk} for status {self.status_message.pk}'


class Friend(models.Model):
    '''Represents a friendship between two profiles.'''
    
    profile1 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="profile2")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        '''Return a string representation of this Friend relationship.'''
        return f'{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}'