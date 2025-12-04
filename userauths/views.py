from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import Profile, User


# User = settings.AUTH_USER_MODEL

def register_view(request):
    
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, You account was created successfully.")
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password=form.cleaned_data['password1']
            )
            login(request, new_user)
            return redirect("core:cart")
    else:
        form = UserRegisterForm()


    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)


from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth.models import User

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse

User = get_user_model()  # ✅ Use your custom User model




def login_view(request):
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")

        # Check group membership for redirect
        if request.user.is_superuser:
            return redirect("useradmin:dashboard")
        elif request.user.groups.filter(name="Vendor").exists():
            return redirect("useradmin:vendor_dashboard")
        elif request.user.groups.filter(name="Delivery").exists():
            return redirect("delivery:delivery_dashboard")
        else:
            return redirect("core:index")  # customer/homepage

    # Build absolute URL for Google One-Tap login (if used)
    login_uri = request.build_absolute_uri(reverse('core:google-one-tap-login'))

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")

            # ✅ Role/group based redirect after login
            if user.is_superuser:
                return redirect("useradmin:dashboard")
                print("User is Superadmin!")
            elif user.groups.filter(name="Vendor").exists():
                print("User is Vendor!")  # DEBUG
                return redirect("vendor:dashboard")
            
            elif user.groups.filter(name="Delivery").exists():
              print("User is Vendor!")          
              return redirect("delivery:dashboard")
            else:
                return redirect("core:index")  # customer/homepage
        else:
            messages.warning(request, "Invalid email or password. Please try again or create an account.")

    # Render login page
    return render(request, "userauths/sign-in.html", {'login_uri': login_uri})








def logout_view(request):

    logout(request)
    messages.success(request, "You logged out.")
    return redirect("userauths:sign-in")


def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("core:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "userauths/profile-edit.html", context)
