from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from home.api.api_views  import BlogViewSet, TransferViewSet  # Fixed import

# ---------- DRF Router ----------
router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blogs')
router.register(r'transfers', TransferViewSet, basename='transfers')

# ---------- Swagger / ReDoc Schema ----------
schema_view = get_schema_view(
    openapi.Info(
        title="Home API",
        default_version='v1',
        description="API documentation for the home app (blogs & transfers)",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# ---------- API URL Patterns ----------
urlpatterns = [
    path('', include(router.urls)),

    # ---------- Swagger / ReDoc ----------
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
