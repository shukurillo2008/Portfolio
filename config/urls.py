from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include your portfolio app URLs
    # Replace 'portfolio' with the actual name of your app
    path('', include('main.urls')),
]

# Configuration to serve user-uploaded media (Profile pics, project shots) 
# and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)