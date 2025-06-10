from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    '''Adding a Profile to the database.'''

    class Meta:
        '''form for Profile model fields'''
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email', 'pfp_url']


class CreateStatusMessageForm(forms.ModelForm):
    '''Adding a status message to DB'''

    class Meta:
        '''form for StatusMessage model fields.'''
        model = StatusMessage
        fields = ['message']


class UpdateProfileForm(forms.ModelForm):
    '''A form to update a Profile in the database.'''
    
    class Meta:
        '''Associate this form with the Profile model.'''
        model = Profile

        fields = ['city', 'email', 'pfp_url']


class UpdateStatusMessageForm(forms.ModelForm):
    '''A form to update a StatusMessage in the database.'''
    
    class Meta:
        '''Associate this form with the StatusMessage model.'''
        model = StatusMessage
        fields = ['message']