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