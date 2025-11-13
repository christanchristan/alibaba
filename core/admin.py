from django.contrib import admin
from django.utils.html import mark_safe
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

# ---------------- CartOrder Admin ----------------
@admin.register(CartOrder)
class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'email', 'product_status', 'sku']
    list_display = ['user', 'email', 'price', 'paid_status', 'order_date', 'product_status', 'sku']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            return qs.none()
        return qs.filter(cartorderproducts__item__in=Product.objects.filter(vendor=vendor).values_list('title', flat=True)).distinct()

# ---------------- CartOrderProducts Admin ----------------
class CartOrderProductsAdmin(admin.ModelAdmin):
    list_display = [
        'order_shipping', 'order_phone', 'invoice_no', 'item', 'vendor_name', 'image_link',
        'qty', 'price', 'total'
    ]

    def get_queryset(self, request):
        self.request = request  # store request for order_shipping/order_phone
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            return qs.none()
        vendor_products_titles = Product.objects.filter(vendor=vendor).values_list('title', flat=True)
        return qs.filter(item__in=vendor_products_titles)

    def vendor_name(self, obj):
        try:
            product = Product.objects.get(title=obj.item)
            return (product.vendor.title, product.vendor.contact,product.vendor.address)
        except Product.DoesNotExist:
            return "-"
    vendor_name.short_description = 'Vendor'

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
        if self.request.user.is_superuser:
            return order.phone
        return "-"
    order_phone.short_description = 'Phone'

    def image_link(self, obj):
        if obj.image:
            image_url = f"/media/{obj.image.lstrip('media/')}"
            return mark_safe(f'<a href="{image_url}" target="_blank"><img src="{image_url}" width="50" height="50"/></a>')
        return "-"
    image_link.short_description = 'Image'

admin.site.register(CartOrderProducts, CartOrderProductsAdmin)

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

