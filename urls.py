from django.contrib import admin
from django.urls import path, include

# ✅ ADD THESE TWO LINES
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
]

# ✅ ADD THIS LINE AT BOTTOM
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)