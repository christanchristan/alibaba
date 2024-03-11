from django import forms
from froala_editor.widgets import FroalaEditor
from .models import *


class BlogForm(forms.ModelForm):
    class Meta:
        model = BlogModel
        fields = ['title', 'content']


        class BlogForm(forms.ModelForm):
    class Meta:
        model = transfer
        fields = ['title', 'content']
