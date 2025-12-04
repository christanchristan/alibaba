from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# DRF + Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Project-level Swagger schema
schema_view = get_schema_view(
    openapi.Info(
        title="Ecomprj API",
        default_version='v1',
        description="Unified API documentation for the project",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web routes
    path('', include('core.urls')),
    path('user/', include('userauths.urls')),
    path('vendor/', include('vendor.urls')),
     path('delivery/', include('delivery.urls')),
    path('useradmin/', include('useradmin.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    
    # API routes
    path('api/core/', include('core.api.urls')),          # products, categories, vendors
    path('api/user/', include('userauths.api.urls')),    # register, login, profile, logout
    path('accounts/', include('allauth.urls')),

    # Project-level Swagger / ReDoc
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Static & media for dev
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
