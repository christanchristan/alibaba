from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token

from home.models import BlogModel, transfer
from .serializers import (
    BlogSerializer,
    TransferSerializer,
    RegisterSerializer,
)

User = get_user_model()

# ============================
#      BLOG VIEWSET
# ============================
class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogModel.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'


# ============================
#     TRANSFER VIEWSET
# ============================
class TransferViewSet(viewsets.ModelViewSet):
    queryset = transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'slug'


# ============================
#     USER REGISTER API
# ============================


# ============================
#       USER LOGIN API
# ============================
