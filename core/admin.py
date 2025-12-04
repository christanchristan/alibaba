from django.contrib import admin
from django.utils.html import mark_safe
from .admin_notifications import *
from django.contrib.auth import get_user_model
User = get_user_model()
admin.site.get_urls_without_custom
from core.models import (
    CartOrderProducts, Product, Category, Vendor, CartOrder,
    ProductImages, ProductReview, wishlist_model, Address
)

# ---------------- Product Images Inline ----------------
class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

# ---------------- Product Admin ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_editable = ['title', 'price', 'featured', 'product_status']
    list_display = ['user', 'title', 'product_image', 'price', 'category', 'vendor', 'featured', 'product_status', 'pid']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vendor = Vendor.objects.get(user=request.user)
            return qs.filter(vendor=vendor)
        except Vendor.DoesNotExist:
            return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            vendor = Vendor.objects.filter(user=request.user).first()
            if vendor:
                obj.vendor = vendor
                obj.user = request.user
        obj.save()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['vendor', 'user']

# ---------------- Category Admin ----------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']


# ---------------- Vendor Admin ----------------
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['user']

    # Include JS for real-time vendor notifications
    class Media:
        js = ('js/vendor_notifications.js',)   # Make sure this file exists in your static folder
# ---------------- CartOrder Admin ----------------
@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'email', 'product_status','vendor_confirmation','shipping_cost', 'shipping_estimate','sku']
    list_display = ['user', 'email', 'price', 'paid_status','vendor_confirmation','order_date', 'product_status','shipping_cost', 'shipping_estimate','sku']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            return qs.none()
        return qs.filter(cartorderproducts__item__in=Product.objects.filter(vendor=vendor).values_list('title', flat=True)).distinct()
from django.contrib.auth import get_user_model
User = get_user_model()

class CartOrderProductsAdmin(admin.ModelAdmin):
    list_display = [
        'order_shipping', 'order_phone', 'vendor_confirmation', 'invoice_no',
        'item', 'vendor_name','customer_center', 'product', 'vendor_center', 'image_link',
        'qty', 'price', 'total'
    ]

    def get_queryset(self, request):
        self.request = request
        qs = super().get_queryset(request)

        # Superusers see all
        if request.user.is_superuser:
            return qs

        # Vendors see only their products
        vendor_products = Product.objects.filter(user=request.user)
        return qs.filter(product__in=vendor_products)

    def vendor_name(self, obj):
        """
        Display vendor info safely using the ForeignKey to Product
        """
        if obj.product and obj.product.user:
            user = obj.product.user
            email = getattr(user, 'email', '')
            username = getattr(user, 'username', '')
            bio = getattr(user, 'bio', '')
            phone = getattr(user, 'phone', '')
            return f"{email} - {username} - {bio} - {phone}"
        return "-"
    vendor_name.short_description = 'venderinfo'

    # ⭐ ADDED METHOD (fix for admin error)
    def vendor_center(self, obj):
        """
        Returns vendor center/location from product.user.state
        """
        try:
            return obj.product.user.state
        except:
            return "-"
    vendor_center.short_description = 'Vendor Center'

    def order_shipping(self, obj):
        order = obj.order
        if not order:
            return "-"

        if self.request.user.is_superuser:
            return f"{order.full_name}, {order.address}, {order.state}, {order.country}"
        else:
            return f"{order.address}, {order.state}, {order.country}"
    order_shipping.short_description = 'Shipping Info'

    def order_phone(self, obj):
        order = obj.order
        if not order:
            return "-"
        return order.phone if self.request.user.is_superuser else "-"
    order_phone.short_description = 'Phone'

    def image_link(self, obj):
        if obj.image:
            image_url = f"/media/{obj.image.lstrip('media/')}"
            return mark_safe(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" width="50" height="50"/></a>'
            )
        return "-"
    image_link.short_description = 'Image'

def vendor_center(self, obj):
    """
    Return vendor center from product.user.state
    """
    try:
        return obj.product.user.state
    except:
        return "-"
    def order_shipping(self, obj):
        order = obj.order
        if not order:
            return "-"
        if self.request.user.is_superuser:
            return f"{order.full_name}, {order.address}, {order.state}, {order.country}"
        else:
            return f"{order.address}, {order.state}, {order.country}"
    order_shipping.short_description = 'Shipping Info'

    def order_phone(self, obj):
        order = obj.order
        if not order:
            return "-"
        return order.phone if self.request.user.is_superuser else "-"
    order_phone.short_description = 'Phone'

    def image_link(self, obj):
        if obj.image:
            image_url = f"/media/{obj.image.lstrip('media/')}"
            return mark_safe(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" width="50" height="50"/></a>'
            )
        return "-"
    image_link.short_description = 'Image'


admin.site.register(CartOrderProducts, CartOrderProductsAdmin)




# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User  # just to attach admin

class NotificationAdmin(admin.ModelAdmin):
    change_list_template = "admin/notifications.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('notifications/', self.admin_site.admin_view(self.notification_view), name='notifications'),
        ]
        return custom_urls + urls

    def notification_view(self, request):
        notifications = [
            {"message": "New user registered", "level": "info"},
            {"message": "Order #1234 pending", "level": "warning"},
        ]
        return render(request, "admin/notifications.html", {"notifications": notifications})

# Register dummy model just to attach admin view
admin.site.register(User, NotificationAdmin)


# ---------------- ProductReview Admin ----------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']

# ---------------- Wishlist Admin ----------------
@admin.register(wishlist_model)
class wishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

# ---------------- Address Admin ----------------
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_editable = ['address', 'status']
    list_display = ['user', 'address', 'status']

