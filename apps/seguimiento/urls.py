"""URLs del módulo de Seguimiento."""
from django.urls import path
from . import views

app_name = 'seguimiento'

urlpatterns = [
    # Seguimiento del servicio
    path('', views.SeguimientoListView.as_view(), name='lista'),
    path('nuevo/', views.SeguimientoCreateView.as_view(), name='crear'),
    path('<int:pk>/actualizar/', views.SeguimientoUpdateView.as_view(), name='actualizar'),

    # Notificaciones
    path('notificaciones/', views.NotificacionListView.as_view(), name='notificaciones'),
    path('notificaciones/<int:pk>/leida/', views.MarcarLeidaView.as_view(), name='marcar_leida'),
    path('notificaciones/leer-todas/', views.MarcarTodasLeidasView.as_view(), name='leer_todas'),
]
