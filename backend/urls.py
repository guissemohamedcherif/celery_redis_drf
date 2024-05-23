from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from django.urls import re_path
from django.views.static import serve
from rest_framework import permissions
from backend.settings import APP_NAME

...
urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/', include('api.urls')),
    re_path(r'^mediafiles/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
