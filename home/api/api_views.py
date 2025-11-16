from rest_framework import viewsets
from home.models import BlogModel, transfer
from .serializers import BlogSerializer, TransferSerializer

# ---------- Blog ViewSet ----------
class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogModel.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'  # optional if you want detail by slug

# ---------- Transfer ViewSet ----------
class TransferViewSet(viewsets.ModelViewSet):
    queryset = transfer.objects.all()
    serializer_class = TransferSerializer
    lookup_field = 'slug'
