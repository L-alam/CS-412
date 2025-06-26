from django import forms
from .models import *

# Form for creating new trips with name, description, and date range fields using date picker widgets.
class CreateTripForm(forms.ModelForm):
    '''Adding a Trip to the database.'''
    
    class Meta:
        model = Trip
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

# Form for creating travel plans with just a name field.
class CreatePlanForm(forms.ModelForm):
    '''Adding a Plan to the database'''
    
    class Meta:
        model = Plan
        fields = ['name']

# Form for adding destinations to a user's travel wishlist with optional target year.
class AddWishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['destination_name', 'target_year']
        
# Form for creating user profiles with basic contact information fields.
class CreateProfileForm(forms.ModelForm):
    '''Adding a Profile to the database.'''

    class Meta:
        '''form for Profile model fields'''
        model = Profile
        fields = ['first_name', 'last_name', 'email']


# Flight search form with departure/arrival cities, dates, travel class, and passenger count for API queries.
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

# Form with destination, check-in/out dates, and guest count parameters for Hotel API requests.
class HotelSearchForm(forms.Form):
    '''Form for searching hotels using SerpAPI'''
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Paris, Tokyo, New York',
            'class': 'form-control'
        }),
        help_text='Enter city or destination'
    )
    
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Check-in date'
    )
    
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Check-out date'
    )
    
    adults = forms.IntegerField(
        initial=2,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10'
        }),
        help_text='Number of adults'
    )
    
    children = forms.IntegerField(
        initial=0,
        min_value=0,
        max_value=8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'max': '8'
        }),
        help_text='Number of children'
    )