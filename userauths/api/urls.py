from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from userauths.api import views

# ----------------- Swagger / ReDoc Schema -----------------
schema_view = get_schema_view(
    openapi.Info(
        title="User Auth API",
        default_version='v1',
        description="API documentation for User Authentication (register, login, logout, profile)",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="support@yourapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# ----------------- URL Patterns -----------------
urlpatterns = [
    # User authentication APIs (class-based views)
    path('register/', views.RegisterAPIView.as_view(), name='register-api'),
    path('login/', views.LoginAPIView.as_view(), name='login-api'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout-api'),
    path('profile/', views.ProfileUpdateAPIView.as_view(), name='profile-api'),
  
    # Swagger / ReDoc endpoints
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
