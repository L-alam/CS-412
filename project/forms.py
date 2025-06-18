from django import forms
from .models import Trip

class CreateTripForm(forms.ModelForm):
    '''Adding a Trip to the database.'''
    
    class Meta:
        model = Trip
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }