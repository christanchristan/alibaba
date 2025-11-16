from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Import routers
from core.api.urls import router as core_router
from home.api.urls import router as home_router

# ---------- Swagger / ReDoc ----------
schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce + Home API",
        default_version='v1',
        description="Unified API documentation for core and home apps",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Include both routers
    path('api/core/', include(core_router.urls)),
    path('api/home/', include(home_router.urls)),

    # Swagger / ReDoc
    path('api/swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
