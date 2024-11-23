"""
URL configuration for todo_list project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

api_patterns = [
    path('', include('tasks.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]

# Only add swagger urls if not testing
if not getattr(settings, 'TESTING', False):
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="Tasks API",
            default_version='v1',
            description="API for managing tasks",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@tasks.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
