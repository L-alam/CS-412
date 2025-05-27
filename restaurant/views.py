from django.shortcuts import render
from django.http import HttpRequest
import random
import time
from datetime import datetime, timedelta
from .forms import OrderForm

# Daily specials list (same as before)
daily_specials = [
    {'name': 'LTO Burger', 'price': 12.99, 'description': 'Lettuce, tomato, onion with special sauce'},
    {'name': 'Bacon Cheeseburger', 'price': 13.99, 'description': 'Classic burger with crispy bacon and cheese'},
    {'name': 'Mushroom Burger', 'price': 12.49, 'description': 'Sautéed mushrooms with Swiss cheese'},
    {'name': 'Truffle Fries', 'price': 8.99, 'description': 'Hand-cut fries with truffle oil and parmesan'},
    {'name': 'Spicy Grilled Cheese', 'price': 9.99, 'description': 'Three-cheese blend with jalapeños and hot sauce'},
]

def main(request):
    """Main restaurant page"""
    return render(request, 'restaurant/main.html')

def order(request):
    """Order page with Django form"""
    
    todays_special = random.choice(daily_specials)
    
    form = OrderForm()
    
    context = {
        'form': form,
        'daily_special': todays_special,
    }
    
    return render(request, 'restaurant/order.html', context)

def confirmation(request):
    """Process order using Django form validation"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            menu_items = {
                'classic_cheese': {'name': 'Classic Cheese', 'price': 8.99},
                'steak_cheese': {'name': 'Steak and Cheese', 'price': 11.99},
                'waffle_fries': {'name': 'Waffle Fries', 'price': 4.99},
                'milk_shake': {'name': 'Milk Shake', 'price': 5.99},
            }
            
            toppings = {
                'whipped_cream': {'name': 'Extra Whipped Cream', 'price': 0.75},
                'chocolate_chips': {'name': 'Chocolate Chips', 'price': 1.25},
                'cherry_on_top': {'name': 'Cherry on Top', 'price': 0.50},
                'cookie_crumbs': {'name': 'Cookie Crumbs', 'price': 1.00},
            }
            
            ordered_items = []
            total_price = 0
            
            for item_key, item_info in menu_items.items():
                if cleaned_data.get(item_key):
                    ordered_items.append(item_info)
                    total_price += item_info['price']
            
            if cleaned_data.get('milk_shake'):
                for topping_key, topping_info in toppings.items():
                    if cleaned_data.get(topping_key):
                        ordered_items.append(topping_info)
                        total_price += topping_info['price']
            
            if cleaned_data.get('daily_special'):
                special_name = request.POST.get('special_name')
                special_price = float(request.POST.get('special_price'))
                ordered_items.append({'name': special_name, 'price': special_price})
                total_price += special_price
            
            current_time = datetime.now()
            minutes_to_add = random.randint(30, 60)
            ready_time = current_time + timedelta(minutes=minutes_to_add)
            
            context = {
                'ordered_items': ordered_items,
                'total_price': round(total_price, 2),
                'customer_name': cleaned_data['customer_name'],
                'customer_phone': cleaned_data['customer_phone'],
                'customer_email': cleaned_data['customer_email'],
                'special_instructions': cleaned_data.get('special_instructions', ''),
                'ready_time': ready_time.strftime("%I:%M %p"),
            }
            
            return render(request, 'restaurant/confirmation.html', context)
        else:
            todays_special = random.choice(daily_specials)
            context = {
                'form': form,
                'daily_special': todays_special,
            }
            return render(request, 'restaurant/order.html', context)
    
    return render(request, 'restaurant/order.html')