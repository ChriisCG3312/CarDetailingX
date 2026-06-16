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

    # Administración de Paquetes
    path('admin/paquetes/', views.PaqueteAdminListView.as_view(), name='paquete_admin_list'),
    path('admin/paquetes/nuevo/', views.PaqueteCreateView.as_view(), name='paquete_crear'),
    path('admin/paquetes/<int:pk>/editar/', views.PaqueteUpdateView.as_view(), name='paquete_editar'),
    path('admin/paquetes/<int:pk>/eliminar/', views.PaqueteDeleteView.as_view(), name='paquete_eliminar'),

    # Flujo para Clientes (Paquete Personalizado)
    path('paquete/personalizado/', views.PaquetePersonalizadoCreateView.as_view(), name='paquete_personalizado_crear'),
]