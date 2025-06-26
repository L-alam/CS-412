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



class FlightSearchForm(forms.Form):
    '''Form for searching flights using SerpAPI'''
    
    departure_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., New York, Paris, LAX',
            'class': 'form-control'
        }),
        help_text='Enter city name or airport code'
    )
    
    arrival_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., London, Tokyo, CDG',
            'class': 'form-control'
        }),
        help_text='Enter city name or airport code'
    )
    
    departure_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Select departure date'
    )
    
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Optional: Select return date for round trip'
    )
    
    travel_class = forms.ChoiceField(
        choices=[
            ('1', 'Economy'),
            ('2', 'Premium Economy'),
            ('3', 'Business'),
            ('4', 'First Class')
        ],
        initial='1',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    adults = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=9,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '9'
        })
    )