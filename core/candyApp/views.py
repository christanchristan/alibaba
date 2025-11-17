from django.shortcuts import render
from . import candy

# Create your views here.

def main(request):    
    context={
    }
    return candy.render(request, 'index.html', context)


def implementation(request):    
    context={
    }
    return candy.render(request, 'implementation.html', context)


def contact(request):    
    context={
    }
    return candy.render(request, 'contact.html', context)