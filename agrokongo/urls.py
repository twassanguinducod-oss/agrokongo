# agrokongo/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='home'),
    path('health/', views.health_check, name='health'),

    # Admin
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🔷 DOCUMENTAÇÃO API (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # ← Schema YAML
    path('api/schema/json/', SpectacularAPIView.as_view(), {'format': 'json'}, name='schema-json'),  # ← Schema JSON
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # ← Swagger UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ← ReDoc
    path('api/docs/postman/', SpectacularAPIView.as_view(), {'format': 'json'}, name='postman-collection'),
    # ← Postman (formato nos kwargs)

    # Apps API
    path('api/accounts/', include('accounts.urls')),
    path('api/marketplace/', include('marketplace.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/core/', include('core.urls')),
]