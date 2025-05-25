from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random

# Create your views here.
quotes = [
    "Books are a uniquely portable magic.",
    "If you don't have time to read, you don't have the time (or the tools) to write. Simple as that.",
    "Get busy living or get busy dying.",
    "Monsters are real, and ghosts are real too. They live inside us, and sometimes, they win.",
    "Good books don't give up all their secrets at once",
    "Fiction is the truth inside the lie",
    "The road to hell is paved with adverbs.",
    "The scariest moment is always just before you start.",
]

images = [
    "https://upload.wikimedia.org/wikipedia/commons/b/b4/Stephen_King_-_2011.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJ1SiSKiHBSpNk9qIJ8-GLjtmA5_08FNisJg&s", 
    "https://live.staticflickr.com/3778/10968972143_96c3b9cdaf_b.jpg",
    "https://static01.nyt.com/images/2015/10/31/arts/31KING/31KING-superJumbo.jpg",
    "https://media.npr.org/assets/img/2024/05/21/ap21056480405009-22a85758785af449b6e6fc1b514a0e9bcbf2c081.jpg?s=1100&c=50&f=jpeg",
    "https://mediaproxy.salon.com/width/1200/https://media2.salon.com/2008/10/stephen_kings_god_trip.jpg",
]

def quote(request):
    '''
    Define a view to get random quote and image request.
    '''
    
    random_quote = random.choice(quotes)
    random_image = random.choice(images)
    
    context = {
        'quote': random_quote,
        'image': random_image,
    }
    return render(request, 'quotes/quote.html', context)



def show_all(request):
    '''
    Define a view to show all quotes and images.
    '''
    context = {
        'quotes': quotes,
        'images': images,
    }
    
    return render(request, 'quotes/show_all.html', context)


def about(request):
    '''
    Define a view to handle the 'about' request.
    '''
    
    context = {}
    
    return render(request, 'quotes/about.html', context)
