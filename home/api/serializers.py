from rest_framework import serializers
from home.models import BlogModel, transfer
from userauths.models import User

# ---------------------------- Blog ----------------------------
class BlogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # show username instead of ID

    class Meta:
        model = BlogModel
        fields = ['id', 'title', 'slug', 'content', 'user', 'image', 'created_at', 'upload_to']

# ---------------------------- Transfer ----------------------------
class TransferSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = transfer
        fields = ['id', 'title', 'slug', 'content', 'user', 'image', 'created_at', 'upload_to']
