"""URLs del módulo de Seguimiento."""
from django.urls import path
from . import views

app_name = 'seguimiento'

urlpatterns = [
    # Seguimientos
    path('',                     views.SeguimientoListaView.as_view(),           name='lista'),
    path('nuevo/',               views.SeguimientoCrearView.as_view(),           name='crear'),
    path('<int:pk>/actualizar/', views.SeguimientoActualizarView.as_view(),      name='actualizar'),
    path('<int:pk>/detalle/',    views.SeguimientoDetalleClienteView.as_view(),  name='detalle_cliente'),

    # Notificaciones
    path('notificaciones/',               views.NotificacionListaView.as_view(),    name='notificaciones'),
    path('notificaciones/marcar-todas/',  views.MarcarTodasLeidasView.as_view(),    name='marcar_todas'),
    path('notificaciones/<int:pk>/leer/', views.MarcarLeidaView.as_view(),          name='marcar_leida'),
    
]