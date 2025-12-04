from rest_framework import serializers
from taggit.models import Tag
from core.models import (
    Product, Category, Vendor, CartOrder, CartOrderProducts,
    ProductImages, ProductReview, wishlist_model, Address, Coupon
)
from userauths.models import Profile, User

# ---------------------------- Product Images ----------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()  # replace default 'images' field

    class Meta:
        model = ProductImages
        fields = ['id', 'images']

    def get_images(self, obj):
        request = self.context.get('request')  # get request to build full URL
        if request:
            return request.build_absolute_uri(obj.images.url)
        return obj.images.url

# ---------------------------- Product Reviews ----------------------------
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'review', 'rating', 'date']

# ---------------------------- Product ----------------------------
class ProductSerializer(serializers.ModelSerializer):
    p_images = serializers.SerializerMethodField()
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'pid', 'title', 'description', 'price', 'category', 'vendor',
            'product_status', 'featured', 'p_images', 'reviews', 'average_rating'
        ]

    def get_p_images(self, obj):
        request = self.context.get('request')  # Safely get request
        images_qs = obj.p_images.all()  # ProductImages related objects
        if images_qs.exists():
            # Return full URL if request exists, otherwise just relative URLs
            if request:
                return [request.build_absolute_uri(img.images.url) for img in images_qs]
            return [img.images.url for img in images_qs]
        # Fallback: return main product.image if no ProductImages exist
        if obj.image:
            if request:
                return [request.build_absolute_uri(obj.image.url)]
            return [obj.image.url]
        return []

    def get_average_rating(self, obj):
        from django.db.models import Avg
        return obj.reviews.aggregate(avg=Avg('rating'))['avg']

# ---------------------------- Category ----------------------------
class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # the PK
    products = ProductSerializer(many=True, read_only=True, source='product_set')  

    class Meta:
        model = Category
        fields = ['id', 'cid', 'title', 'image', 'products']

# ---------------------------- Vendor ----------------------------
class VendorSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True, source='product')

    class Meta:
        model = Vendor
        fields = ['vid', 'title', 'description', 'products']

# ---------------------------- Cart / Order ----------------------------
class CartOrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartOrderProducts
        fields = '__all__'

class CartOrderSerializer(serializers.ModelSerializer):
    order_items = CartOrderProductsSerializer(source='cartorderproducts_set', many=True, read_only=True)

    class Meta:
        model = CartOrder
        fields = [
            'oid', 'user', 'price', 'full_name', 'email', 'phone',
            'address', 'city', 'state', 'country', 'paid_status', 'order_items'
        ]

# ---------------------------- Wishlist ----------------------------
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = wishlist_model
        fields = ['id', 'user', 'product']

# ---------------------------- Address ----------------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address', 'mobile', 'status']

# ---------------------------- Coupon ----------------------------
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount', 'active']
