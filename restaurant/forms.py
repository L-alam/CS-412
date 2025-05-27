from django import forms

class OrderForm(forms.Form):
    # Menu items
    classic_cheese = forms.BooleanField(required=False, label='Classic Cheese ($8.99)')
    steak_cheese = forms.BooleanField(required=False, label='Steak and Cheese ($11.99)')
    waffle_fries = forms.BooleanField(required=False, label='Waffle Fries ($4.99)')
    milk_shake = forms.BooleanField(required=False, label='Milk Shake ($5.99)')
    
    # Milk shake toppings
    whipped_cream = forms.BooleanField(required=False, label='Extra Whipped Cream (+$0.75)')
    chocolate_chips = forms.BooleanField(required=False, label='Chocolate Chips (+$1.25)')
    cherry_on_top = forms.BooleanField(required=False, label='Cherry on Top (+$0.50)')
    cookie_crumbs = forms.BooleanField(required=False, label='Cookie Crumbs (+$1.00)')
    
    # Daily special
    daily_special = forms.BooleanField(required=False, label='Today\'s Special')
    
    # Customer information
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your full name'})
    )
    customer_phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': '(555) 123-4567'})
    )
    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@example.com'})
    )
    
    # Special instructions
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Any allergies, preferences, or special requests...'
        })
    )