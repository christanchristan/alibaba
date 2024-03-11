from django.contrib import admin

# Register your models here.
from .models import  transfer, BlogModel, Profiles

admin.site.register(BlogModel)
admin.site.register(Profiles)
admin.site.register(transfer)