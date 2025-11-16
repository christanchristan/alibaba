from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from home.api import urls as api_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Home API",
        default_version='v1',
        description="Swagger docs for Home app",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", include(api_urls)),  # Include your Home API viewsets & endpoints
    path("swagger.json/", schema_view.without_ui(cache_timeout=0), name="home-schema-json"),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name="home-schema-swagger-ui"),
    path("redoc/", schema_view.with_ui('redoc', cache_timeout=0), name="home-schema-redoc"),
]
