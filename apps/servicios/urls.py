"""URLs del módulo de Servicios."""
from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    # Vista pública (sin login)
    path('', views.ServicioListView.as_view(), name='catalogo'),

    # Administración de servicios
    path('admin/', views.ServicioAdminListView.as_view(), name='admin_lista'),
    path('admin/nuevo/', views.ServicioCreateView.as_view(), name='crear'),
    path('admin/<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='editar'),
    path('admin/<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='eliminar'),

    # Promociones
    path('promociones/', views.PromocionListView.as_view(), name='promociones'),
    path('promociones/nueva/', views.PromocionCreateView.as_view(), name='crear_promo'),
    path('promociones/<int:pk>/editar/', views.PromocionUpdateView.as_view(), name='editar_promo'),
    path('promociones/<int:pk>/eliminar/', views.PromocionDeleteView.as_view(), name='eliminar_promo'),
]
