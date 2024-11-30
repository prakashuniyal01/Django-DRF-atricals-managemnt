
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import render

schema_view = get_schema_view(
    openapi.Info(
        title="Article managenet",
        default_version="v1",
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', lambda request: render(request, 'home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('articles', include('apps.articles.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
