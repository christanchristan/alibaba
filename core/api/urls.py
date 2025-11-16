from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.api import api_views

# DRF Router
router = DefaultRouter()
router.register(r'products', api_views.ProductViewSet, basename='products')
router.register(r'categories', api_views.CategoryViewSet, basename='categories')
router.register(r'vendors', api_views.VendorViewSet, basename='vendors')

# Swagger / ReDoc Schema
schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API",
        default_version='v1',
        description="API documentation for your e-commerce app",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # DRF router
    path('', include(router.urls)),

    # Custom API endpoints
    path('products/<int:product_id>/reviews/', api_views.ProductReviewAPIView.as_view(), name='product-reviews'),
    path('search/', api_views.SearchAPIView.as_view(), name='search-products'),
    path('filter/', api_views.FilterProductAPIView.as_view(), name='filter-products'),
    path('cart/', api_views.CartAPIView.as_view(), name='cart-api'),
    path('checkout/<int:order_id>/', api_views.CheckoutAPIView.as_view(), name='checkout-api'),
    path('stripe-checkout/<int:order_id>/', api_views.StripeCheckoutAPIView.as_view(), name='stripe-checkout'),
    path('wishlist/', api_views.WishlistAPIView.as_view(), name='wishlist-api'),
    path('contact/', api_views.ContactAPIView.as_view(), name='contact-api'),

    # Swagger / ReDoc
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
