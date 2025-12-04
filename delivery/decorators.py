from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

def delivery_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # User not authenticated
        if not request.user.is_authenticated:
            messages.warning(request, "You must sign in to access this page")
            return redirect('/user/sign-in/')

        # User is authenticated but not in the vendor group
        if not request.user.groups.filter(name='delivery').exists():
            messages.warning(request, "You are not authorized to access this page")
            return redirect('/')  # or another page for non-vendors

        # User is authenticated and in vendor group
        return view_func(request, *args, **kwargs)

    return wrapper
