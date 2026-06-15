"""URLs raíz del proyecto Detailing."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Apps
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('servicios/', include('apps.servicios.urls', namespace='servicios')),
    path('citas/', include('apps.citas.urls', namespace='citas')),
    path('seguimiento/', include('apps.seguimiento.urls', namespace='seguimiento')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),  # ← nueva

    # Dashboard principal
    path('dashboard/', include('apps.usuarios.urls_dashboard', namespace='dashboard')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
