from django import forms
from .models import *

class CreateTripForm(forms.ModelForm):
    '''Adding a Trip to the database.'''
    
    class Meta:
        model = Trip
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CreatePlanForm(forms.ModelForm):
    '''Adding a Plan to the database'''
    
    class Meta:
        model = Plan
        fields = ['name']


class AddWishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['destination_name', 'target_year']
        

class CreateProfileForm(forms.ModelForm):
    '''Adding a Profile to the database.'''

    class Meta:
        '''form for Profile model fields'''
        model = Profile
        fields = ['first_name', 'last_name', 'email']