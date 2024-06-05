from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/', include('debug_toolbar.urls')),
    path('api/', include('movies.api.urls')),
]
