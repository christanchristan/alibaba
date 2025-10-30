from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password"}))
    bio= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Adress"}))
    phone= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"phone"}))
    country=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"country"}))
    state=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"state"})) 
   

    class Meta:
        model = User
        fields = ['username', 'email','bio','phone','country','state']



class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Full Name"}))
    bio = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Bio"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Phone"}))

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone']